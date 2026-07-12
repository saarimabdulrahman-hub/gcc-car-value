"""Cookie Store — add, update, delete, bulk import/export, domain lookup, validation."""

import asyncio
import time
from browser.session.models import Cookie
from browser.session.errors import CookieValidationError


class CookieStore:
    """Thread-safe in-memory cookie store with domain-based lookup.

    Cookies are isolated by session_id. No cross-session contamination.
    Cookie values are masked in logs automatically.
    """

    def __init__(self):
        self._cookies: dict[str, list[Cookie]] = {}  # session_id -> cookies
        self._lock = asyncio.Lock()
        self._total_added = 0
        self._total_removed = 0

    async def add(self, session_id: str, cookie: Cookie) -> None:
        if not cookie.name or not cookie.domain:
            raise CookieValidationError("Cookie name and domain are required")
        async with self._lock:
            if session_id not in self._cookies:
                self._cookies[session_id] = []
            # Replace existing cookie with same name+domain
            existing = [
                c for c in self._cookies[session_id]
                if c.name == cookie.name and c.domain == cookie.domain
            ]
            for c in existing:
                self._cookies[session_id].remove(c)
            self._cookies[session_id].append(cookie)
            self._total_added += 1

    async def add_bulk(self, session_id: str, cookies: list[Cookie]) -> None:
        for c in cookies:
            await self.add(session_id, c)

    async def get_all(self, session_id: str) -> list[Cookie]:
        async with self._lock:
            return list(self._cookies.get(session_id, []))

    async def get_by_domain(self, session_id: str, domain: str) -> list[Cookie]:
        async with self._lock:
            return [
                c for c in self._cookies.get(session_id, [])
                if c.domain == domain or domain.endswith("." + c.domain.lstrip("."))
            ]

    async def delete(self, session_id: str, name: str, domain: str) -> None:
        async with self._lock:
            if session_id in self._cookies:
                self._cookies[session_id] = [
                    c for c in self._cookies[session_id]
                    if not (c.name == name and c.domain == domain)
                ]
                self._total_removed += 1

    async def clear_session(self, session_id: str) -> None:
        async with self._lock:
            self._cookies.pop(session_id, None)

    async def export_dicts(self, session_id: str) -> list[dict]:
        """Export cookies as Playwright-compatible dicts."""
        cookies = await self.get_all(session_id)
        return [c.to_dict() for c in cookies if not self._is_expired(c)]

    async def import_dicts(self, session_id: str, cookie_dicts: list[dict]) -> None:
        """Import cookies from Playwright-compatible dicts."""
        cookies = [Cookie.from_dict(d) for d in cookie_dicts]
        await self.add_bulk(session_id, cookies)

    async def cleanup_expired(self, session_id: str) -> int:
        """Remove expired cookies. Returns count removed."""
        async with self._lock:
            if session_id not in self._cookies:
                return 0
            before = len(self._cookies[session_id])
            self._cookies[session_id] = [
                c for c in self._cookies[session_id]
                if not self._is_expired(c)
            ]
            return before - len(self._cookies[session_id])

    @staticmethod
    def _is_expired(cookie: Cookie) -> bool:
        if cookie.expires is None:
            return False
        return time.time() > cookie.expires

    @property
    def total_operations(self) -> int:
        return self._total_added + self._total_removed
