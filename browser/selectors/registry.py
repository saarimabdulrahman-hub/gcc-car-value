"""Selector Registry — register, lookup, update, enumerate by marketplace/group."""

import asyncio
from browser.selectors.models import Selector
from browser.selectors.errors import SelectorNotFoundError, DuplicateSelectorError


class SelectorRegistry:
    """Thread-safe registry of versioned selectors.

    Keyed by (marketplace, name) — each marketplace has its own selector set.
    """

    def __init__(self):
        self._selectors: dict[str, Selector] = {}  # key = "marketplace:name"
        self._lock = asyncio.Lock()

    def _key(self, marketplace: str, name: str) -> str:
        return f"{marketplace}:{name}"

    async def register(self, selector: Selector) -> None:
        key = self._key(selector.marketplace, selector.name)
        async with self._lock:
            if key in self._selectors and not selector.deprecated:
                raise DuplicateSelectorError(
                    f"Selector '{selector.name}' already registered for '{selector.marketplace}'"
                )
            self._selectors[key] = selector

    async def get(self, marketplace: str, name: str) -> Selector:
        key = self._key(marketplace, name)
        async with self._lock:
            if key not in self._selectors:
                raise SelectorNotFoundError(
                    f"Selector '{name}' not found for marketplace '{marketplace}'"
                )
            return self._selectors[key]

    async def update(self, selector: Selector) -> None:
        key = self._key(selector.marketplace, selector.name)
        async with self._lock:
            if key in self._selectors:
                selector.version = self._selectors[key].version + 1
            self._selectors[key] = selector

    async def remove(self, marketplace: str, name: str) -> None:
        key = self._key(marketplace, name)
        async with self._lock:
            self._selectors.pop(key, None)

    async def list_by_marketplace(self, marketplace: str) -> list[Selector]:
        async with self._lock:
            return [s for s in self._selectors.values()
                   if s.marketplace == marketplace]

    async def list_by_group(self, marketplace: str, group: str) -> list[Selector]:
        async with self._lock:
            return [s for s in self._selectors.values()
                   if s.marketplace == marketplace and s.group == group]

    async def list_all(self) -> list[Selector]:
        async with self._lock:
            return list(self._selectors.values())

    async def get_marketplaces(self) -> list[str]:
        async with self._lock:
            mps = {s.marketplace for s in self._selectors.values()}
            return sorted(mps)
