"""HealthRegistry — registers checks, executes with timeout, aggregates results."""

from __future__ import annotations

import asyncio
import time
from typing import Callable

import structlog

from src.core.health.base import (
    HealthCheck, CheckResult, HealthStatus, CheckSeverity,
)

logger = structlog.get_logger()


class HealthRegistry:
    """Registry for health checks. Executes all registered checks concurrently.

    Usage:
        registry = HealthRegistry()
        registry.register(DatabaseCheck(session_factory))
        registry.register(MemoryCheck())

        result = await registry.run_all()
        # result = {"status": "healthy", "checks": [...], "duration_ms": ...}
    """

    def __init__(self):
        self._checks: dict[str, HealthCheck] = {}

    def register(self, check: HealthCheck) -> None:
        """Register a health check. Replaces existing check with same name."""
        self._checks[check.name] = check

    def unregister(self, name: str) -> None:
        """Remove a health check by name."""
        self._checks.pop(name, None)

    def get_check(self, name: str) -> HealthCheck | None:
        """Look up a registered check by name."""
        return self._checks.get(name)

    def list_checks(self) -> list[str]:
        """List all registered check names."""
        return sorted(self._checks.keys())

    async def run_all(self) -> dict:
        """Execute all registered checks concurrently with timeout.

        Returns a dict suitable for serialization to JSON.
        Critical failures → status "unhealthy".
        Optional failures → status "degraded".
        All healthy → status "healthy".
        """
        start = time.perf_counter()
        names = list(self._checks.keys())

        if not names:
            return {
                "status": HealthStatus.HEALTHY.value,
                "checks": [],
                "duration_ms": 0.0,
            }

        # Run all checks concurrently with individual timeouts
        tasks = []
        for name in names:
            check = self._checks[name]
            tasks.append(self._run_with_timeout(check))

        results: list[CheckResult] = await asyncio.gather(*tasks)

        # Aggregate status
        status = self._aggregate_status(results)
        duration_ms = (time.perf_counter() - start) * 1000

        # Emit metrics for monitoring
        self._emit_metrics(results, duration_ms)

        return {
            "status": status.value,
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "severity": r.severity.value,
                    "duration_ms": round(r.duration_ms, 2),
                    "error": r.error,
                    **r.details,
                }
                for r in results
            ],
            "duration_ms": round(duration_ms, 2),
        }

    async def run_readiness(self) -> dict:
        """Run only critical-severity checks. Returns 200 if ready, 503 if not."""
        result = await self.run_all()
        # Readiness: only critical checks matter
        critical_failures = [
            c for c in result["checks"]
            if c["status"] != "healthy" and c.get("severity") == "critical"
        ]
        if critical_failures:
            result["status"] = "unhealthy"
        return result

    async def run_liveness(self) -> dict:
        """Minimal liveness check — application loop is alive.

        Does not check external dependencies. Only verifies the process
        is responsive. Always returns healthy if this code executes.
        """
        return {
            "status": HealthStatus.HEALTHY.value,
            "checks": [
                {
                    "name": "liveness",
                    "status": HealthStatus.HEALTHY.value,
                    "detail": "Process is alive and responding",
                }
            ],
            "duration_ms": 0.0,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _run_with_timeout(self, check: HealthCheck) -> CheckResult:
        """Execute a single check with timeout and error handling."""
        check_start = time.perf_counter()

        try:
            result = await asyncio.wait_for(
                check.check(),
                timeout=check.timeout_seconds,
            )
        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - check_start) * 1000
            result = CheckResult.unhealthy(
                name=check.name,
                error=f"Health check timed out after {check.timeout_seconds}s",
                severity=check.severity,
                duration_ms=duration_ms,
            )
            logger.warning("health_check_timeout", check=check.name,
                         timeout=check.timeout_seconds)
        except Exception as e:
            duration_ms = (time.perf_counter() - check_start) * 1000
            result = CheckResult.unhealthy(
                name=check.name,
                error=str(e)[:500],
                severity=check.severity,
                duration_ms=duration_ms,
            )
            logger.error("health_check_failed", check=check.name, error=str(e)[:200])

        if result.duration_ms == 0.0:
            result.duration_ms = (time.perf_counter() - check_start) * 1000

        return result

    def _aggregate_status(self, results: list[CheckResult]) -> HealthStatus:
        """Determine overall status from individual check results."""
        has_unhealthy = any(
            r.status == HealthStatus.UNHEALTHY
            and r.severity == CheckSeverity.CRITICAL
            for r in results
        )
        if has_unhealthy:
            return HealthStatus.UNHEALTHY

        has_degraded = any(
            r.status != HealthStatus.HEALTHY
            for r in results
        )
        if has_degraded:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    def _emit_metrics(self, results: list[CheckResult],
                      total_duration_ms: float) -> None:
        """Publish health check metrics to the global registry."""
        try:
            from src.core.metrics import Metrics

            for r in results:
                Metrics.increment("health.checks_total",
                                 tags={"name": r.name, "status": r.status.value})
                Metrics.observe("health.check_duration_ms",
                               r.duration_ms,
                               tags={"name": r.name})

            Metrics.set_gauge("health.total_duration_ms", total_duration_ms)
        except Exception:
            pass  # Never let metrics break health checks
