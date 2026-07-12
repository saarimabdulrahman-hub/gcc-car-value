"""Browser factory — create browser instances from the registry."""

from browser.base.interfaces import Browser
from browser.models import BrowserConfig
from browser.registry import browser_registry


class BrowserFactory:
    """Create browser instances by driver name."""

    def __init__(self):
        self._registry = browser_registry

    def create(self, driver: str, config: BrowserConfig | None = None) -> Browser:
        """Create a browser instance for the given driver name."""
        cls = self._registry.get(driver)
        return cls(config or BrowserConfig())

    def list_available(self) -> list[str]:
        return self._registry.list_drivers()
