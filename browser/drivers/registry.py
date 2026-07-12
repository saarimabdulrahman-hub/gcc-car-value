"""Driver Registry — register, lookup, enumerate browser drivers."""

import asyncio
from typing import Type
from browser.drivers.interfaces import BrowserDriver
from browser.drivers.errors import DriverNotFoundError, DriverRegistrationError


class DriverRegistry:
    """Thread-safe registry of browser driver classes.

    Supports concurrent registration, lookup by name/browser_type/capabilities.
    """

    def __init__(self):
        self._drivers: dict[str, Type[BrowserDriver]] = {}
        self._default: str = ""
        self._lock = asyncio.Lock()

    async def register(self, driver_cls: Type[BrowserDriver]) -> None:
        """Register a driver class."""
        # Instantiate temporarily to get name
        instance = driver_cls()
        name = instance.name
        async with self._lock:
            if name in self._drivers:
                raise DriverRegistrationError(
                    f"Driver '{name}' is already registered"
                )
            self._drivers[name] = driver_cls
            if not self._default:
                self._default = name

    async def unregister(self, name: str) -> None:
        async with self._lock:
            self._drivers.pop(name, None)
            if self._default == name:
                self._default = next(iter(self._drivers), "")

    async def get(self, name: str) -> Type[BrowserDriver]:
        async with self._lock:
            if name not in self._drivers:
                raise DriverNotFoundError(
                    f"Driver '{name}' not found. Available: {list(self._drivers.keys())}"
                )
            return self._drivers[name]

    async def get_default(self) -> Type[BrowserDriver]:
        async with self._lock:
            if not self._default:
                raise DriverNotFoundError("No drivers registered")
            return self._drivers[self._default]

    async def find_by_browser_type(self, browser_type: str) -> Type[BrowserDriver] | None:
        """Find a driver that supports the given browser type."""
        async with self._lock:
            for cls in self._drivers.values():
                inst = cls()
                if inst.capabilities.browser_type == browser_type:
                    return cls
            return None

    async def list_all(self) -> list[str]:
        async with self._lock:
            return sorted(self._drivers.keys())

    async def set_default(self, name: str) -> None:
        async with self._lock:
            if name not in self._drivers:
                raise DriverNotFoundError(f"Cannot set default: '{name}' not registered")
            self._default = name
