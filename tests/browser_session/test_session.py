"""Test session manager, cookie store, storage state, policies."""
import asyncio
import pytest
from browser.session.models import BrowserSession, Cookie, SessionPolicy, SessionStatus
from browser.session.cookie_store import CookieStore
from browser.session.storage_state import StorageStateManager
from browser.session.session_manager import SessionManager
from browser.session.policies import SessionPolicies
from browser.session.errors import SessionNotFoundError, SessionExpiredError


class TestCookieStore:
    @pytest.mark.asyncio
    async def test_add_and_get(self):
        store = CookieStore()
        c = Cookie("session", "abc123", domain="example.com")
        await store.add("s1", c)
        cookies = await store.get_all("s1")
        assert len(cookies) == 1
        assert cookies[0].name == "session"

    @pytest.mark.asyncio
    async def test_add_replaces_same_name_domain(self):
        store = CookieStore()
        await store.add("s1", Cookie("a", "1", domain="x.com"))
        await store.add("s1", Cookie("a", "2", domain="x.com"))
        cookies = await store.get_all("s1")
        assert len(cookies) == 1
        assert cookies[0].value == "2"

    @pytest.mark.asyncio
    async def test_domain_lookup(self):
        store = CookieStore()
        await store.add("s1", Cookie("a", "1", domain="example.com"))
        await store.add("s1", Cookie("b", "2", domain="other.com"))
        found = await store.get_by_domain("s1", "example.com")
        assert len(found) == 1
        assert found[0].name == "a"

    @pytest.mark.asyncio
    async def test_export_playwright_format(self):
        store = CookieStore()
        await store.add("s1", Cookie("session", "abc", domain="example.com"))
        dicts = await store.export_dicts("s1")
        assert len(dicts) == 1
        assert dicts[0]["name"] == "session"
        assert "httpOnly" in dicts[0]

    @pytest.mark.asyncio
    async def test_import_playwright_format(self):
        store = CookieStore()
        await store.import_dicts("s1", [
            {"name": "session", "value": "xyz", "domain": "example.com",
             "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"}
        ])
        cookies = await store.get_all("s1")
        assert len(cookies) == 1
        assert cookies[0].value == "xyz"

    @pytest.mark.asyncio
    async def test_session_isolation(self):
        store = CookieStore()
        await store.add("s1", Cookie("a", "1", domain="x.com"))
        await store.add("s2", Cookie("b", "2", domain="x.com"))
        s1 = await store.get_all("s1")
        s2 = await store.get_all("s2")
        assert len(s1) == 1 and s1[0].name == "a"
        assert len(s2) == 1 and s2[0].name == "b"

    @pytest.mark.asyncio
    async def test_clear_session(self):
        store = CookieStore()
        await store.add("s1", Cookie("a", "1", domain="x.com"))
        await store.clear_session("s1")
        assert len(await store.get_all("s1")) == 0


class TestSessionManager:
    @pytest.fixture
    async def mgr(self):
        return SessionManager()

    @pytest.mark.asyncio
    async def test_create_session(self, mgr):
        s = await mgr.create("test_market")
        assert s.marketplace == "test_market"
        assert s.status == SessionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_and_acquire(self, mgr):
        s = await mgr.create("test")
        acquired = await mgr.acquire(s.session_id)
        assert acquired.session_id == s.session_id

    @pytest.mark.asyncio
    async def test_acquire_nonexistent_raises(self, mgr):
        with pytest.raises(SessionNotFoundError):
            await mgr.acquire("nonexistent")

    @pytest.mark.asyncio
    async def test_release_sets_idle(self, mgr):
        s = await mgr.create("test")
        await mgr.release(s.session_id)
        session = await mgr.get_session(s.session_id)
        assert session.status == SessionStatus.IDLE

    @pytest.mark.asyncio
    async def test_destroy_removes(self, mgr):
        s = await mgr.create("test")
        await mgr.destroy(s.session_id)
        assert await mgr.get_session(s.session_id) is None

    @pytest.mark.asyncio
    async def test_stats(self, mgr):
        await mgr.create("a")
        await mgr.create("b")
        stats = await mgr.stats()
        assert stats["total_sessions"] == 2

    @pytest.mark.asyncio
    async def test_persistent_reuse(self, mgr):
        """Persistent sessions for same marketplace are reused."""
        SessionPolicies.set_policy("dubizzle", SessionPolicy.PERSISTENT)
        s1 = await mgr.create("dubizzle")
        s2 = await mgr.create("dubizzle")
        assert s1.session_id == s2.session_id  # Reused

    @pytest.mark.asyncio
    async def test_ephemeral_always_new(self, mgr):
        """Ephemeral sessions are never reused."""
        SessionPolicies.set_policy("test_eph", SessionPolicy.EPHEMERAL)
        s1 = await mgr.create("test_eph")
        s2 = await mgr.create("test_eph")
        assert s1.session_id != s2.session_id  # Always new


class TestStorageState:
    @pytest.mark.asyncio
    async def test_save_and_load(self):
        mgr = StorageStateManager()
        state = {"origins": [{"origin": "https://example.com", "localStorage": []}]}
        await mgr.save("s1", state)
        loaded = await mgr.load("s1")
        assert loaded == state

    @pytest.mark.asyncio
    async def test_clear(self):
        mgr = StorageStateManager()
        await mgr.save("s1", {"key": "val"})
        await mgr.clear("s1")
        assert await mgr.load("s1") is None


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_cookie_ops(self):
        store = CookieStore()
        async def add_one(i):
            await store.add("s1", Cookie(f"c{i}", f"v{i}", domain="x.com"))
        await asyncio.gather(*[add_one(i) for i in range(100)])
        cookies = await store.get_all("s1")
        assert len(cookies) == 100

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        mgr = SessionManager()
        async def create_one(i):
            return await mgr.create(f"market-{i}")
        sessions = await asyncio.gather(*[create_one(i) for i in range(50)])
        assert len(sessions) == 50
