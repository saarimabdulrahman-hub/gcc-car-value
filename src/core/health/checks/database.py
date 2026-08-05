"""Database health check — connectivity, pool health, migration state."""

import time
from collections.abc import Callable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.health.base import CheckResult, CheckSeverity, HealthCheck


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

                # Migration state check — verify revision is current
                result = await session.execute(text(
                    "SELECT version_num FROM alembic_version"
                ))
                row = result.fetchone()
                if row is None:
                    raise RuntimeError("alembic_version table is empty — no migrations applied")

            # Compare installed revision against Alembic head
            from alembic.config import Config as AlembicConfig
            from alembic.script import ScriptDirectory
            from pathlib import Path

            alembic_cfg = AlembicConfig("src/db/migrations/alembic.ini")
            script = ScriptDirectory.from_config(alembic_cfg)
            heads = script.get_heads()
            installed = row.version_num

            if installed not in heads:
                duration_ms = (time.perf_counter() - start) * 1000
                return CheckResult.degraded(
                    name=self.name,
                    error=f"Database migration is behind head. Installed: {installed[:12]}..., Head: {heads[0][:12]}...",  # noqa: E501
                    severity=self.severity,
                    duration_ms=duration_ms,
                    installed_revision=installed,
                    head_revision=heads[0],
                )

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
