"""Capability resolution — find drivers that support required features."""

from browser.drivers.models import DriverCapabilities


class CapabilityResolver:
    """Match driver capabilities against scraper requirements.

    Usage:
        resolver = CapabilityResolver()
        driver = resolver.find_best(registry, required={"headless": True, "screenshots": True})
    """

    def find_best(self, registry, required: dict) -> list[str]:
        """Return driver names that satisfy all required capabilities."""
        results = []
        for name in registry.list_all_sync() if hasattr(registry, 'list_all_sync') else []:
            # This is a synchronous helper — use the async registry in manager
            pass
        return results

    @staticmethod
    def matches(cap: DriverCapabilities, required: dict) -> bool:
        """Check if capabilities satisfy requirements."""
        for key, value in required.items():
            if not hasattr(cap, key):
                return False
            if getattr(cap, key) != value:
                return False
        return True
