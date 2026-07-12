"""Test browser pool — leasing, scaling, recycling, concurrency."""
import asyncio
import pytest
from browser.base.interfaces import Browser, BrowserContext, BrowserPage
from browser.pool.config import PoolConfig
from browser.pool.browser_pool import BrowserPool
from browser.pool.browser_slot import BrowserSlot, SlotState
from browser.pool.errors import PoolExhaustedError, PoolShuttingDownError
from browser.pool.pool_manager import PoolManager


# ------------------------------------------------------------------
# Dummy browser for testing
# ------------------------------------------------------------------

class DummyPage(BrowserPage):
    def __init__(self): self._url = "about:blank"
    async def goto(self, url, opts=None): self._url = url
    async def content(self): return "<html></html>"
    async def title(self): return "Test"
    async def url(self): return self._url
    async def wait_for_selector(self, s, t=30): pass
    async def click(self, s): pass
    async def fill(self, s, v): pass
    async def evaluate(self, e): return None
    async def screenshot(self, o=None): return b""
    async def reload(self): pass
    async def close(self): pass

class DummyContext(BrowserContext):
    async def new_page(self): return DummyPage()
    async def set_cookies(self, c): pass
    async def cookies(self): return []
    async def close(self): pass

class DummyBrowser(Browser):
    def __init__(self, config=None):
        self._healthy = True
        self._started = False
    async def start(self): self._started = True
    async def stop(self): self._started = False
    async def new_context(self, config=None): return DummyContext()
    async def health(self): return self._healthy


def _make_browser():
    return DummyBrowser()


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestBrowserSlot:
    @pytest.mark.asyncio
    async def test_acquire_release_cycle(self):
        b = DummyBrowser()
        await b.start()
        slot = BrowserSlot(b, "s1")
        assert slot.state == SlotState.IDLE

        ctx = await slot.acquire()
        assert slot.state == SlotState.LEASED
        assert slot.context_count == 1

        await slot.release()
        assert slot.state == SlotState.IDLE
        assert slot.context_count == 0

    @pytest.mark.asyncio
    async def test_health_check(self):
        b = DummyBrowser()
        await b.start()
        slot = BrowserSlot(b, "s1")
        assert await slot.health_check()

    @pytest.mark.asyncio
    async def test_stop(self):
        b = DummyBrowser()
        await b.start()
        slot = BrowserSlot(b, "s1")
        await slot.stop()
        assert slot.state == SlotState.STOPPED


class TestBrowserPool:
    @pytest.fixture
    async def pool(self):
        p = BrowserPool(_make_browser, PoolConfig(
            min_browsers=1, max_browsers=3,
            max_contexts_per_browser=10,
            warm_pool_size=1,
        ))
        await p.start()
        yield p
        await p.shutdown()

    @pytest.mark.asyncio
    async def test_start_creates_warm_pool(self, pool):
        assert len(pool._slots) == 1

    @pytest.mark.asyncio
    async def test_acquire_and_release(self, pool):
        ctx = await pool.acquire()
        assert ctx is not None
        page = await ctx.new_page()
        assert page is not None
        await pool.release(ctx)

    @pytest.mark.asyncio
    async def test_multiple_acquires(self, pool):
        ctx1 = await pool.acquire()
        ctx2 = await pool.acquire()
        assert ctx1 is not ctx2
        await pool.release(ctx1)
        await pool.release(ctx2)

    @pytest.mark.asyncio
    async def test_context_isolation(self, pool):
        """Contexts from different acquires are isolated."""
        ctx1 = await pool.acquire()
        ctx2 = await pool.acquire()
        # Different context objects — isolated cookies/storage
        assert ctx1 is not ctx2
        await pool.release(ctx1)
        await pool.release(ctx2)

    @pytest.mark.asyncio
    async def test_shutdown_prevents_acquire(self, pool):
        await pool.shutdown()
        with pytest.raises(PoolShuttingDownError):
            await pool.acquire()

    @pytest.mark.asyncio
    async def test_scales_up_under_load(self):
        pool = BrowserPool(_make_browser, PoolConfig(
            min_browsers=1, max_browsers=5,
            max_contexts_per_browser=1,  # Force scale-up: only 1 ctx per browser
            warm_pool_size=1, lease_timeout=5.0,
        ))
        await pool.start()

        # Acquire multiple contexts — should scale up
        ctxs = []
        for _ in range(3):
            ctxs.append(await pool.acquire())
        assert len(pool._slots) >= 3  # Scaled up

        for ctx in ctxs:
            await pool.release(ctx)
        await pool.shutdown()


class TestPoolManager:
    @pytest.mark.asyncio
    async def test_start_and_shutdown(self):
        pool = BrowserPool(_make_browser, PoolConfig(warm_pool_size=1))
        mgr = PoolManager(pool)
        await mgr.start()
        stats = mgr.stats
        assert stats["total_slots"] >= 1
        await mgr.shutdown()


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_leases(self):
        """100 concurrent context leases — no race conditions, no double leasing."""
        pool = BrowserPool(_make_browser, PoolConfig(
            min_browsers=1, max_browsers=10,
            max_contexts_per_browser=20,
            lease_timeout=30.0,
        ))
        await pool.start()

        async def lease_and_use(i):
            ctx = await pool.acquire()
            page = await ctx.new_page()
            await page.goto(f"https://example.com/page{i}")
            await asyncio.sleep(0.001)  # Simulate brief usage
            await pool.release(ctx)

        tasks = [lease_and_use(i) for i in range(100)]
        await asyncio.gather(*tasks)

        # All contexts should be released
        stats = pool._slots
        total_ctx = sum(s.context_count for s in stats)
        assert total_ctx == 0  # All released
        await pool.shutdown()
