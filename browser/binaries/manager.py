"""Binary Manager — orchestrates discovery, validation, caching, and resolution."""

import asyncio
import time
import structlog

from browser.binaries.models import BrowserBinary, BinaryStatus
from browser.binaries.registry import BinaryRegistry
from browser.binaries.discovery import BinaryDiscovery
from browser.binaries.validator import BinaryValidator
from browser.binaries.cache import BinaryCache
from browser.binaries.config import BinaryManagerConfig
from browser.binaries.errors import BinaryNotFoundError, BinaryInvalidError

logger = structlog.get_logger()


class BinaryManager:
    """Central manager for browser binary lifecycle.

    Drivers request binaries from this manager. It discovers, validates,
    caches, and resolves the best binary for a given browser type.

    Usage:
        mgr = BinaryManager(BinaryManagerConfig())
        await mgr.initialize()
        binary = await mgr.resolve("chromium", version="120.0.0")
        # Use binary.executable_path to launch
    """

    def __init__(self, config: BinaryManagerConfig | None = None):
        self.config = config or BinaryManagerConfig()
        self._registry = BinaryRegistry()
        self._discovery = BinaryDiscovery(
            configured_paths=self.config.configured_paths,
            search_path=self.config.search_path,
            search_standard=self.config.search_standard_locations,
        )
        self._validator = BinaryValidator()
        self._cache = BinaryCache(ttl_seconds=self.config.cache_ttl_seconds)
        self._lock = asyncio.Lock()

    async def initialize(self) -> list[BrowserBinary]:
        """Discover and validate all available binaries. Call once at startup."""
        async with self._lock:
            discovered = []
            for browser_type in ["chromium", "firefox", "webkit"]:
                found = await self._discovery.discover(browser_type)
                for binary in found:
                    # Check cache first
                    cached = self._cache.get_validation(binary)
                    if cached and cached.valid:
                        binary.status = BinaryStatus.VALID
                    else:
                        result = await self._validator.validate_and_update(binary)
                        self._cache.set_validation(binary, result)

                    try:
                        await self._registry.register(binary)
                    except Exception:
                        pass  # Already registered
                    discovered.append(binary)

            logger.info("binaries_initialized",
                       count=len(discovered),
                       valid=sum(1 for b in discovered if b.status == BinaryStatus.VALID))
            return discovered

    async def resolve(self, browser_type: str,
                      version: str = "") -> BrowserBinary:
        """Find the best binary for the given browser type.

        Priority:
        1. Already-registered, validated binary
        2. Discovered and validated binary
        3. Raises BinaryNotFoundError
        """
        start = time.monotonic()

        # Try registry first
        binary = await self._registry.find(browser_type, version)
        if binary and binary.status == BinaryStatus.VALID:
            return binary

        # Try discovery
        found = await self._discovery.discover(browser_type)
        for b in found:
            cached = self._cache.get_validation(b)
            if cached is None:
                result = await self._validator.validate_and_update(b)
                self._cache.set_validation(b, result)
                cached = result

            if cached.valid:
                try:
                    await self._registry.register(b)
                except Exception:
                    pass
                return b

        duration = (time.monotonic() - start) * 1000
        raise BinaryNotFoundError(
            f"No valid '{browser_type}' binary found (took {duration:.1f}ms). "
            f"Configured paths: {self.config.configured_paths}. "
            f"Install a browser or add its path to the configuration."
        )

    async def validate(self, binary: BrowserBinary) -> bool:
        """Validate a specific binary. Updates cache and registry."""
        result = await self._validator.validate_and_update(binary)
        self._cache.set_validation(binary, result)
        return result.valid

    async def list_available(self) -> list[BrowserBinary]:
        """List all registered binaries."""
        return await self._registry.list_all()

    async def refresh(self) -> None:
        """Clear cache and re-discover."""
        self._cache.clear()
        await self.initialize()
