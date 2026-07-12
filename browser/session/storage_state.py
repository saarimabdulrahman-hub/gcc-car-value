"""Storage State Manager — local storage, session storage, Playwright storage_state format."""

import asyncio


class StorageStateManager:
    """Manages browser storage state (localStorage, sessionStorage, cookies).

    Produces and consumes Playwright-compatible storage_state dicts.
    Storage is isolated by session_id.
    """

    def __init__(self):
        self._states: dict[str, dict] = {}  # session_id -> storage_state
        self._lock = asyncio.Lock()

    async def save(self, session_id: str, state: dict) -> None:
        """Save a storage state snapshot (Playwright format)."""
        async with self._lock:
            self._states[session_id] = dict(state)

    async def load(self, session_id: str) -> dict | None:
        """Load a previously saved storage state."""
        async with self._lock:
            return dict(self._states.get(session_id, {})) or None

    async def clear(self, session_id: str) -> None:
        async with self._lock:
            self._states.pop(session_id, None)

    async def export_for_context(self, session_id: str,
                                 cookie_store) -> dict:
        """Build a Playwright-compatible storage_state dict from cookies + storage."""
        from browser.session.cookie_store import CookieStore
        cookies = await cookie_store.export_dicts(session_id)
        storage = await self.load(session_id) or {}
        return {
            "cookies": cookies,
            "origins": storage.get("origins", []),
        }

    async def import_from_context(self, session_id: str,
                                  state: dict, cookie_store) -> None:
        """Import a Playwright storage_state dict into cookies + storage."""
        await cookie_store.import_dicts(session_id, state.get("cookies", []))
        await self.save(session_id, state)
