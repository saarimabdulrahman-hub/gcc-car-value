"""Browser health monitoring — periodic checks and recovery."""

from browser.pool.browser_pool import BrowserPool


class PoolHealthMonitor:
    """Periodic health checker for the browser pool."""

    def __init__(self, pool: BrowserPool):
        self._pool = pool

    async def check(self) -> dict:
        """Run a health check and return summary."""
        return await self._pool.run_health_checks()
