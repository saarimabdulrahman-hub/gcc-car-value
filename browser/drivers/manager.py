"""Driver Manager — selects, validates, and manages browser drivers.

The single gateway between the Browser Pool and browser implementations.
The pool requests a driver; the manager resolves which one to use based
on capabilities, preferences, and health.
"""

from __future__ import annotations

import asyncio
import time
from typing import Type

import structlog

from browser.base.interfaces import Browser
from browser.drivers.interfaces import BrowserDriver
from browser.drivers.registry import DriverRegistry
from browser.drivers.config import DriverManagerConfig
from browser.drivers.models import DriverInfo
from browser.drivers.errors import (
    DriverNotFoundError, DriverUnavailableError, DriverLaunchError,
    CapabilityNotSupportedError,
)
from browser.drivers.capabilities import CapabilityResolver

logger = structlog.get_logger()


class DriverManager:
    """Central manager for browser driver selection and lifecycle.

    Usage:
        registry = DriverRegistry()
        await registry.register(PlaywrightDriver)

        mgr = DriverManager(registry)
        browser = await mgr.launch(prefer="playwright-chromium")
        # ... use browser ...
        await mgr.shutdown()
    """

    def __init__(self, registry: DriverRegistry,
                 config: DriverManagerConfig | None = None):
        self._registry = registry
        self.config = config or DriverManagerConfig()
        self._active_drivers: dict[str, BrowserDriver] = {}
        self._driver_info: dict[str, DriverInfo] = {}
        self._resolver = CapabilityResolver()
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Launch
    # ------------------------------------------------------------------

    async def launch(self, prefer: str = "",
                     required_capabilities: dict | None = None) -> Browser:
        """Launch a browser using the best available driver.

        Selection order:
        1. Preferred driver (if specified and healthy)
        2. Driver matching required capabilities
        3. Default registered driver
        4. Fallback driver from config
        """
        driver_cls = await self._select_driver(prefer, required_capabilities)
        if driver_cls is None:
            raise DriverNotFoundError(
                "No suitable driver found. "
                f"Preferred: '{prefer or self.config.preferred_driver}', "
                f"Required capabilities: {required_capabilities}"
            )

        driver = driver_cls()
        name = driver.name

        async with self._lock:
            if name not in self._driver_info:
                self._driver_info[name] = DriverInfo(
                    name=name, version=driver.version,
                    browser_type=driver.capabilities.browser_type,
                    capabilities=driver.capabilities,
                )

        try:
            start = time.monotonic()
            browser = await asyncio.wait_for(
                driver.launch(), timeout=self.config.launch_timeout
            )
            async with self._lock:
                self._active_drivers[name] = driver
                self._driver_info[name].launch_count += 1

            logger.info("driver_launched", driver=name,
                       browser_type=driver.capabilities.browser_type,
                       launch_ms=round((time.monotonic() - start) * 1000, 1))
            return browser
        except asyncio.TimeoutError:
            raise DriverLaunchError(
                f"Driver '{name}' launch timed out after {self.config.launch_timeout}s"
            )
        except Exception as e:
            async with self._lock:
                self._driver_info[name].crash_count += 1
                self._driver_info[name].healthy = False
            raise DriverLaunchError(f"Driver '{name}' failed to launch: {e}")

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    async def _select_driver(self, prefer: str,
                             capabilities: dict | None) -> Type[BrowserDriver] | None:
        """Resolve which driver to use."""
        # 1. Preferred driver
        name = prefer or self.config.preferred_driver
        if name:
            try:
                cls = await self._registry.get(name)
                if await self._is_healthy(name, cls):
                    if not capabilities or self._resolver.matches(
                        cls().capabilities, capabilities
                    ):
                        return cls
            except DriverNotFoundError:
                pass

        # 2. Capability-based search
        if capabilities:
            for name in await self._registry.list_all():
                cls = await self._registry.get(name)
                if self._resolver.matches(cls().capabilities, capabilities):
                    if await self._is_healthy(name, cls):
                        return cls

        # 3. Default
        try:
            return await self._registry.get_default()
        except DriverNotFoundError:
            pass

        # 4. Fallback
        if self.config.fallback_driver:
            try:
                return await self._registry.get(self.config.fallback_driver)
            except DriverNotFoundError:
                pass

        return None

    async def _is_healthy(self, name: str,
                          cls: Type[BrowserDriver]) -> bool:
        """Check if a driver is healthy from tracked info."""
        info = self._driver_info.get(name)
        if info and not info.healthy:
            return False
        return True

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def run_health_checks(self) -> dict[str, bool]:
        """Check health of all active drivers."""
        results = {}
        async with self._lock:
            for name, driver in list(self._active_drivers.items()):
                try:
                    healthy = await asyncio.wait_for(driver.health(), timeout=5.0)
                    self._driver_info[name].healthy = healthy
                    results[name] = healthy
                except Exception:
                    self._driver_info[name].healthy = False
                    results[name] = False
        return results

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def shutdown(self) -> None:
        """Shutdown all active drivers."""
        async with self._lock:
            for name, driver in self._active_drivers.items():
                try:
                    await driver.shutdown()
                except Exception as e:
                    logger.warning("driver_shutdown_error", driver=name, error=str(e)[:200])
            self._active_drivers.clear()

    async def get_driver_info(self, name: str) -> DriverInfo | None:
        """Get metadata about a driver."""
        return self._driver_info.get(name)

    async def list_drivers(self) -> list[str]:
        """List registered driver names."""
        return await self._registry.list_all()
