"""Binary Registry — register, lookup, enumerate browser binaries."""

import asyncio
from browser.binaries.models import BrowserBinary
from browser.binaries.errors import BinaryNotFoundError, BinaryRegistrationError


class BinaryRegistry:
    """Thread-safe registry of browser binaries.

    Keyed by (browser_type, executable_path) to allow multiple versions.
    """

    def __init__(self):
        self._binaries: dict[str, BrowserBinary] = {}
        self._lock = asyncio.Lock()

    def _key(self, binary: BrowserBinary) -> str:
        return f"{binary.browser_type}:{binary.executable_path}"

    async def register(self, binary: BrowserBinary) -> None:
        key = self._key(binary)
        async with self._lock:
            if key in self._binaries:
                raise BinaryRegistrationError(f"Binary already registered: {key}")
            self._binaries[key] = binary

    async def unregister(self, browser_type: str, executable_path: str) -> None:
        key = f"{browser_type}:{executable_path}"
        async with self._lock:
            self._binaries.pop(key, None)

    async def find(self, browser_type: str, version: str = "") -> BrowserBinary | None:
        """Find a binary by browser type, optionally filtering by version."""
        async with self._lock:
            candidates = [
                b for b in self._binaries.values()
                if b.browser_type == browser_type
            ]
            if not candidates:
                return None
            if version:
                from browser.binaries.version import VersionResolver
                candidates = [
                    b for b in candidates
                    if VersionResolver.compare(b.version, version) >= 0
                ]
            candidates.sort(key=lambda b: b.version, reverse=True)
            return candidates[0] if candidates else None

    async def find_by_path(self, executable_path: str) -> BrowserBinary | None:
        async with self._lock:
            for b in self._binaries.values():
                if b.executable_path == executable_path:
                    return b
            return None

    async def list_all(self) -> list[BrowserBinary]:
        async with self._lock:
            return list(self._binaries.values())

    async def list_by_type(self, browser_type: str) -> list[BrowserBinary]:
        async with self._lock:
            return [b for b in self._binaries.values()
                   if b.browser_type == browser_type]
