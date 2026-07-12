"""Health endpoints — full health, liveness, readiness, startup.

All endpoints delegate to the HealthRegistry. No health logic lives in routes.
The registry executes all registered checks concurrently with per-check timeouts.
"""

from fastapi import APIRouter, Response
from src.core.health import HealthRegistry
from src.core.health.checks import (
    DatabaseCheck, MemoryCheck, ConfigurationCheck,
    SecretsCheck, MetricsRegistryCheck,
)
from src.api.dependencies import async_session_factory

router = APIRouter()

# ------------------------------------------------------------------
# Build the singleton health registry at module load time
# ------------------------------------------------------------------

health_registry = HealthRegistry()

# Register built-in checks
health_registry.register(DatabaseCheck(lambda: async_session_factory()))
health_registry.register(MemoryCheck(critical_pct=90.0))
health_registry.register(ConfigurationCheck())
health_registry.register(SecretsCheck())
health_registry.register(MetricsRegistryCheck())


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.get("/health")
async def full_health():
    """Full health check — all registered dependencies.

    Returns status 'healthy', 'degraded', or 'unhealthy' with per-check details.
    """
    result = await health_registry.run_all()
    status_code = _status_to_http(result["status"])
    return Response(
        content=_to_json(result),
        media_type="application/json",
        status_code=status_code,
    )


@router.get("/health/live")
async def liveness():
    """Liveness probe — is the application process alive?

    Does NOT check external dependencies. Always returns 200 if the
    process is responding. Used by Kubernetes for pod restart decisions.
    """
    result = await health_registry.run_liveness()
    return Response(
        content=_to_json(result),
        media_type="application/json",
        status_code=200,
    )


@router.get("/health/ready")
async def readiness():
    """Readiness probe — is the application ready to serve traffic?

    Checks critical dependencies only. Returns 200 if all critical
    checks pass, 503 if any critical check fails.
    Used by Kubernetes for service endpoint routing.
    """
    result = await health_registry.run_readiness()
    status_code = _status_to_http(result["status"])
    return Response(
        content=_to_json(result),
        media_type="application/json",
        status_code=status_code,
    )


@router.get("/health/startup")
async def startup():
    """Startup probe — has the application finished initializing?

    Same as readiness but intended for Kubernetes startup probe
    (longer timeout, only runs during pod initialization).
    """
    result = await health_registry.run_readiness()
    status_code = _status_to_http(result["status"])
    return Response(
        content=_to_json(result),
        media_type="application/json",
        status_code=status_code,
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _status_to_http(status: str) -> int:
    """Map health status to HTTP status code."""
    return {
        "healthy": 200,
        "degraded": 200,     # Still serving, but with reduced capability
        "unhealthy": 503,     # Service unavailable
    }.get(status, 500)


def _to_json(data: dict) -> str:
    """Serialize health result to JSON string."""
    import json
    return json.dumps(data, default=str)
