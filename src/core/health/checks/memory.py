"""Memory health check — process memory usage and system thresholds."""

import time
import psutil

from src.core.health.base import HealthCheck, CheckResult, CheckSeverity


class MemoryCheck(HealthCheck):
    """Check process memory usage.

    Verifies:
        - RSS memory is below critical threshold (default 90%)
        - Virtual memory is below critical threshold
    """

    def __init__(self, critical_pct: float = 90.0,
                 timeout_seconds: float = 2.0):
        super().__init__(
            name="memory",
            severity=CheckSeverity.CRITICAL,
            timeout_seconds=timeout_seconds,
        )
        self.critical_pct = critical_pct

    async def check(self) -> CheckResult:
        start = time.perf_counter()

        try:
            process = psutil.Process()
            mem = process.memory_info()
            total = psutil.virtual_memory()

            rss_mb = mem.rss / (1024 * 1024)
            vms_mb = mem.vms / (1024 * 1024)
            rss_pct = (mem.rss / total.total) * 100

            duration_ms = (time.perf_counter() - start) * 1000

            if rss_pct > self.critical_pct:
                return CheckResult.unhealthy(
                    name=self.name,
                    error=f"Memory usage {rss_pct:.1f}% exceeds {self.critical_pct}%",
                    severity=self.severity,
                    duration_ms=duration_ms,
                    rss_mb=round(rss_mb, 1),
                    vms_mb=round(vms_mb, 1),
                    rss_pct=round(rss_pct, 1),
                    total_mb=round(total.total / (1024 * 1024), 1),
                )

            return CheckResult.healthy(
                name=self.name,
                severity=self.severity,
                duration_ms=duration_ms,
                rss_mb=round(rss_mb, 1),
                vms_mb=round(vms_mb, 1),
                rss_pct=round(rss_pct, 1),
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.unhealthy(
                name=self.name,
                error=f"Memory check failed: {str(e)[:200]}",
                severity=self.severity,
                duration_ms=duration_ms,
            )
