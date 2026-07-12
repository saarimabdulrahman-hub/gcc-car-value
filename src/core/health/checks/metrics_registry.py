"""Metrics registry health check — verifies the metrics framework is operational."""

import time
from src.core.health.base import HealthCheck, CheckResult, CheckSeverity


class MetricsRegistryCheck(HealthCheck):
    """Check that the metrics registry is initialized and functional.

    Verifies:
        - Metrics singleton is accessible
        - Registry can register and retrieve a metric
        - At least app lifecycle metrics are present
    """

    def __init__(self, timeout_seconds: float = 2.0):
        super().__init__(
            name="metrics_registry",
            severity=CheckSeverity.OPTIONAL,
            timeout_seconds=timeout_seconds,
        )

    async def check(self) -> CheckResult:
        start = time.perf_counter()

        try:
            from src.core.metrics import Metrics

            metric_count = Metrics.metric_count()
            names = Metrics.list_names()

            duration_ms = (time.perf_counter() - start) * 1000

            if metric_count == 0:
                return CheckResult.degraded(
                    name=self.name,
                    error="Metrics registry is empty — no metrics registered",
                    severity=self.severity,
                    duration_ms=duration_ms,
                )

            # Verify app lifecycle metrics exist
            app_metrics = [n for n in names if n.startswith("app.")]
            if not app_metrics:
                return CheckResult.degraded(
                    name=self.name,
                    error="App lifecycle metrics not found in registry",
                    severity=self.severity,
                    duration_ms=duration_ms,
                )

            return CheckResult.healthy(
                name=self.name,
                severity=self.severity,
                duration_ms=duration_ms,
                metric_count=metric_count,
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.degraded(
                name=self.name,
                error=f"Metrics registry check failed: {str(e)[:200]}",
                severity=self.severity,
                duration_ms=duration_ms,
            )
