"""Session Manager — create, acquire, release, expire, refresh, destroy, restore browser sessions."""

import asyncio
import time
import structlog

from browser.session.models import (
    BrowserSession, SessionStatus, SessionPolicy,
)
from browser.session.cookie_store import CookieStore
from browser.session.storage_state import StorageStateManager
from browser.session.config import SessionManagerConfig
from browser.session.policies import SessionPolicies
from browser.session.errors import SessionNotFoundError, SessionExpiredError

logger = structlog.get_logger()


class SessionManager:
    """Central session lifecycle manager.

    Usage:
        mgr = SessionManager()
        session = await mgr.create("dubizzle_uae", policy=SessionPolicy.PERSISTENT)
        await mgr.restore_cookies(session.session_id, context)
        # ... use browser ...
        await mgr.save_cookies(session.session_id, context)
        await mgr.release(session.session_id)
    """

    def __init__(self, config: SessionManagerConfig | None = None):
        self.config = config or SessionManagerConfig()
        self._sessions: dict[str, BrowserSession] = {}
        self._cookie_store = CookieStore()
        self._storage = StorageStateManager()
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def create(self, marketplace: str,
                     policy: SessionPolicy | None = None,
                     browser_type: str = "chromium",
                     **kwargs) -> BrowserSession:
        """Create a new browser session. If policy is persistent/authenticated
        and an existing valid session exists for this marketplace, reuse it."""
        pol = policy or SessionPolicies.get_policy(marketplace)

        # Try reuse for persistent/authenticated policies
        if SessionPolicies.is_reusable(pol):
            existing = await self._find_reusable(marketplace, pol)
            if existing:
                existing.touch()
                existing.status = SessionStatus.ACTIVE
                return existing

        # Create fresh session
        async with self._lock:
            if len(self._sessions) >= self.config.max_sessions:
                await self._evict_one()

        session = BrowserSession(
            marketplace=marketplace,
            browser_type=browser_type,
            policy=pol,
            max_lifetime_seconds=self.config.session_max_lifetime,
            max_idle_seconds=self.config.session_max_idle,
            expires_at=time.time() + self.config.session_max_lifetime,
            metadata=kwargs,
        )
        async with self._lock:
            self._sessions[session.session_id] = session

        logger.info("session_created",
                   session_id=session.session_id[:8],
                   marketplace=marketplace,
                   policy=pol.value)
        return session

    async def acquire(self, session_id: str) -> BrowserSession:
        """Acquire an existing session for use."""
        async with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        if session.is_expired:
            await self.expire(session_id)
            raise SessionExpiredError(session_id)
        session.touch()
        return session

    async def release(self, session_id: str) -> None:
        """Release a session after use. Marks as idle."""
        async with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            return
        session.status = SessionStatus.IDLE
        session.touch()

    async def expire(self, session_id: str) -> None:
        """Expire a session — keeps cookies for future reuse."""
        async with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            return
        session.status = SessionStatus.EXPIRED

    async def destroy(self, session_id: str) -> None:
        """Destroy a session and its cookies/storage."""
        async with self._lock:
            self._sessions.pop(session_id, None)
        await self._cookie_store.clear_session(session_id)
        await self._storage.clear(session_id)

    # ------------------------------------------------------------------
    # Cookie & Storage Operations
    # ------------------------------------------------------------------

    async def save_cookies(self, session_id: str, cookie_dicts: list[dict]) -> None:
        """Save cookies from a browser context."""
        await self._cookie_store.import_dicts(session_id, cookie_dicts)

    async def restore_cookies(self, session_id: str, context) -> None:
        """Restore saved cookies into a browser context."""
        cookies = await self._cookie_store.get_all(session_id)
        if cookies:
            await context.set_cookies([c.to_dict() for c in cookies])

    async def save_storage_state(self, session_id: str, state: dict) -> None:
        await self._storage.save(session_id, state)

    async def load_storage_state(self, session_id: str) -> dict | None:
        return await self._storage.load(session_id)

    async def export_storage_state(self, session_id: str) -> dict:
        """Export full storage state for Playwright context creation."""
        return await self._storage.export_for_context(session_id, self._cookie_store)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_session(self, session_id: str) -> BrowserSession | None:
        async with self._lock:
            return self._sessions.get(session_id)

    async def list_sessions(self, marketplace: str = "") -> list[BrowserSession]:
        async with self._lock:
            sessions = list(self._sessions.values())
        if marketplace:
            sessions = [s for s in sessions if s.marketplace == marketplace]
        return sessions

    async def stats(self) -> dict:
        async with self._lock:
            sessions = list(self._sessions.values())
        return {
            "total_sessions": len(sessions),
            "active": sum(1 for s in sessions if s.status == SessionStatus.ACTIVE),
            "idle": sum(1 for s in sessions if s.status == SessionStatus.IDLE),
            "expired": sum(1 for s in sessions if s.status == SessionStatus.EXPIRED),
            "total_cookies": sum(s.cookie_count for s in sessions),
            "cookie_ops": self._cookie_store.total_operations,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _find_reusable(self, marketplace: str,
                             policy: SessionPolicy) -> BrowserSession | None:
        async with self._lock:
            for s in self._sessions.values():
                if (s.marketplace == marketplace
                        and s.policy == policy
                        and not s.is_expired
                        and s.status != SessionStatus.DESTROYED):
                    return s
        return None

    async def _evict_one(self) -> None:
        """Evict the oldest expired/idle session to make room."""
        candidates = sorted(
            self._sessions.values(),
            key=lambda s: s.last_used,
        )
        for s in candidates:
            if s.status in (SessionStatus.EXPIRED, SessionStatus.IDLE):
                await self.destroy(s.session_id)
                return
        # If all are active, destroy the oldest
        if candidates:
            await self.destroy(candidates[0].session_id)
