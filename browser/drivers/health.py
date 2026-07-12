"""Driver health monitoring."""

from browser.drivers.manager import DriverManager


class DriverHealthMonitor:
    """Periodically checks driver health and reports status."""

    def __init__(self, manager: DriverManager):
        self._manager = manager

    async def check_all(self) -> dict[str, bool]:
        return await self._manager.run_health_checks()
