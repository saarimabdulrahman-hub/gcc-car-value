"""Browser registry — register browser driver implementations."""

from typing import Type
from browser.base.interfaces import Browser


class BrowserRegistry:
    """Registry of browser driver classes by name.

    Usage:
        registry = BrowserRegistry()
        registry.register("playwright", PlaywrightBrowser)
        cls = registry.get("playwright")
    """

    def __init__(self):
        self._drivers: dict[str, Type[Browser]] = {}

    def register(self, name: str, driver_cls: Type[Browser]) -> None:
        self._drivers[name] = driver_cls

    def get(self, name: str) -> Type[Browser]:
        if name not in self._drivers:
            raise KeyError(f"No browser driver registered: '{name}'")
        return self._drivers[name]

    def list_drivers(self) -> list[str]:
        return sorted(self._drivers.keys())


browser_registry = BrowserRegistry()
