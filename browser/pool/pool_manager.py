"""PoolManager — high-level orchestrator for BrowserPool lifecycle."""

import asyncio
from browser.pool.browser_pool import BrowserPool
from browser.pool.config import PoolConfig
from browser.pool.health import PoolHealthMonitor
from browser.pool.statistics import PoolStatistics


class PoolManager:
    """Orchestrates the browser pool with periodic health checks and scaling.

    Usage:
        mgr = PoolManager(pool)
        await mgr.start()
        # ... use pool ...
        await mgr.shutdown()
    """

    def __init__(self, pool: BrowserPool):
        self._pool = pool
        self._health = PoolHealthMonitor(pool)
        self._stats = PoolStatistics(pool)
        self._health_task: asyncio.Task | None = None
        self._scale_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the pool and background tasks."""
        await self._pool.start()
        cfg = self._pool.config
        self._health_task = asyncio.create_task(
            self._health_loop(cfg.health_check_interval)
        )
        self._scale_task = asyncio.create_task(
            self._scale_loop(max(cfg.max_idle_seconds / 2, 60.0))
        )

    async def shutdown(self) -> None:
        """Shutdown pool and background tasks."""
        if self._health_task:
            self._health_task.cancel()
        if self._scale_task:
            self._scale_task.cancel()
        await self._pool.shutdown()

    async def _health_loop(self, interval: float) -> None:
        while True:
            await asyncio.sleep(interval)
            try:
                await self._health.check()
            except Exception:
                pass

    async def _scale_loop(self, interval: float) -> None:
        while True:
            await asyncio.sleep(interval)
            try:
                await self._pool.scale_idle()
            except Exception:
                pass

    @property
    def stats(self) -> dict:
        return self._stats.snapshot()
