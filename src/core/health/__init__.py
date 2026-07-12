"""Enterprise health check framework — HealthRegistry, probes, dependency checks.

Usage:
    from src.core.health import HealthRegistry, HealthStatus
    from src.core.health.checks import DatabaseCheck, MemoryCheck

    registry = HealthRegistry()
    registry.register(DatabaseCheck(session_factory))
    registry.register(MemoryCheck())

    result = await registry.run_all()
    print(result.status)  # healthy | degraded | unhealthy
"""
from src.core.health.base import HealthStatus, CheckResult, HealthCheck
from src.core.health.registry import HealthRegistry

__all__ = ["HealthStatus", "CheckResult", "HealthCheck", "HealthRegistry"]
