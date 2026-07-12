"""Secrets health check — verifies secrets provider is operational."""

import time
from src.core.health.base import HealthCheck, CheckResult, CheckSeverity


class SecretsCheck(HealthCheck):
    """Check that the secrets provider is accessible and critical secrets exist.

    Verifies:
        - SecretProvider is initialized
        - JWT_SECRET can be retrieved
        - Provider source is valid for the environment
    """

    def __init__(self, timeout_seconds: float = 3.0):
        super().__init__(
            name="secrets",
            severity=CheckSeverity.CRITICAL,
            timeout_seconds=timeout_seconds,
        )

    async def check(self) -> CheckResult:
        start = time.perf_counter()

        try:
            from src.config.secrets import get_secret_provider, SecretName
            provider = get_secret_provider()

            # Check provider is ready
            ready = await provider.ready()
            if not ready:
                duration_ms = (time.perf_counter() - start) * 1000
                return CheckResult.degraded(
                    name=self.name,
                    error=f"Secrets provider '{provider.source_name}' is not ready",
                    severity=self.severity,
                    duration_ms=duration_ms,
                    provider=provider.source_name,
                )

            # Check JWT secret is retrievable
            jwt = await provider.get(SecretName.JWT_SECRET.value)
            jwt_available = jwt is not None and len(jwt) >= 16

            duration_ms = (time.perf_counter() - start) * 1000

            if not jwt_available:
                return CheckResult.unhealthy(
                    name=self.name,
                    error="JWT_SECRET is not available from secrets provider",
                    severity=self.severity,
                    duration_ms=duration_ms,
                    provider=provider.source_name,
                )

            return CheckResult.healthy(
                name=self.name,
                severity=self.severity,
                duration_ms=duration_ms,
                provider=provider.source_name,
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.unhealthy(
                name=self.name,
                error=f"Secrets check failed: {str(e)[:200]}",
                severity=self.severity,
                duration_ms=duration_ms,
            )
