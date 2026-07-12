"""Configuration health check — validates critical settings."""

import time
from src.core.health.base import HealthCheck, CheckResult, CheckSeverity


class ConfigurationCheck(HealthCheck):
    """Check that critical configuration is valid.

    Verifies:
        - JWT secret is configured (not empty, not a known default)
        - Database URL is set
        - Environment is set to a valid value
    """

    def __init__(self, timeout_seconds: float = 2.0):
        super().__init__(
            name="configuration",
            severity=CheckSeverity.CRITICAL,
            timeout_seconds=timeout_seconds,
        )

    async def check(self) -> CheckResult:
        start = time.perf_counter()

        try:
            from src.config import get_settings
            settings = get_settings()

            issues = []

            if not settings.jwt_secret or len(settings.jwt_secret) < 16:
                issues.append("JWT_SECRET is not configured or too short")

            known_defaults = [
                "dev-secret", "change-in-production", "change-me",
            ]
            for default in known_defaults:
                if default in settings.jwt_secret.lower():
                    issues.append(f"JWT_SECRET contains default indicator '{default}'")
                    break

            if not settings.database_url:
                issues.append("DATABASE_URL is not configured")

            valid_envs = {"development", "staging", "production", "testing"}
            if settings.environment not in valid_envs:
                issues.append(
                    f"ENVIRONMENT '{settings.environment}' not in {valid_envs}"
                )

            duration_ms = (time.perf_counter() - start) * 1000

            if issues:
                return CheckResult.degraded(
                    name=self.name,
                    error="; ".join(issues),
                    severity=self.severity,
                    duration_ms=duration_ms,
                    environment=settings.environment,
                )

            return CheckResult.healthy(
                name=self.name,
                severity=self.severity,
                duration_ms=duration_ms,
                environment=settings.environment,
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.unhealthy(
                name=self.name,
                error=f"Configuration check failed: {str(e)[:200]}",
                severity=self.severity,
                duration_ms=duration_ms,
            )
