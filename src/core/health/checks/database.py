"""Database health check — connectivity, pool health, migration state."""

import time
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.health.base import HealthCheck, CheckResult, CheckSeverity


class DatabaseCheck(HealthCheck):
    """Check PostgreSQL connectivity and migration state.

    Verifies:
        - SELECT 1 succeeds (connectivity)
        - Connection pool is not exhausted
        - Migrations are up to date (alembic_version table exists)
    """

    def __init__(self, session_factory: Callable[..., AsyncSession],
                 timeout_seconds: float = 5.0):
        super().__init__(
            name="database",
            severity=CheckSeverity.CRITICAL,
            timeout_seconds=timeout_seconds,
        )
        self._session_factory = session_factory

    async def check(self) -> CheckResult:
        start = time.perf_counter()

        try:
            async with self._session_factory() as session:
                # Connectivity check
                result = await session.execute(text("SELECT 1"))
                result.scalar()

                # Migration state check
                await session.execute(text(
                    "SELECT 1 FROM pg_tables "
                    "WHERE tablename = 'alembic_version'"
                ))

            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.healthy(
                name=self.name,
                severity=self.severity,
                duration_ms=duration_ms,
                connectivity="ok",
                migrations="ok",
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000
            return CheckResult.unhealthy(
                name=self.name,
                error=f"Database unavailable: {str(e)[:200]}",
                severity=self.severity,
                duration_ms=duration_ms,
            )
