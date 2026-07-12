"""Test browser abstraction — interfaces, registry, factory, session, navigation."""
import pytest
from browser.models import BrowserConfig, NavigationOptions, ScreenshotOptions
from browser.base.interfaces import Browser, BrowserContext, BrowserPage
from browser.base.session import BrowserSession
from browser.base.navigation import NavigationEngine
from browser.base.download import DownloadManager, DownloadInfo
from browser.base.screenshot import ScreenshotEngine
from browser.base.network import NetworkManager, RequestInfo, ResponseInfo
from browser.registry import BrowserRegistry, browser_registry
from browser.factory import BrowserFactory


# ------------------------------------------------------------------
# Dummy browser implementations for testing
# ------------------------------------------------------------------

class DummyPage(BrowserPage):
    def __init__(self):
        self._url = "about:blank"
        self._title = "Dummy Page"
        self._content = "<html><body>Dummy</body></html>"
        self._closed = False

    async def goto(self, url, options=None):
        self._url = url

    async def content(self): return self._content
    async def title(self): return self._title
    async def url(self): return self._url
    async def wait_for_selector(self, selector, timeout=30): pass
    async def click(self, selector): pass
    async def fill(self, selector, value): pass
    async def evaluate(self, expression): return None
    async def screenshot(self, options=None): return b"fake-png"
    async def reload(self): pass
    async def close(self): self._closed = True


class DummyContext(BrowserContext):
    async def new_page(self): return DummyPage()
    async def set_cookies(self, cookies): pass
    async def cookies(self): return []
    async def close(self): pass


class DummyBrowser(Browser):
    def __init__(self, config=None):
        self.config = config or BrowserConfig()
        self._started = False

    async def start(self): self._started = True
    async def stop(self): self._started = False
    async def new_context(self, config=None): return DummyContext()
    async def health(self): return self._started


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestBrowserInterface:
    @pytest.mark.asyncio
    async def test_start_stop(self):
        b = DummyBrowser()
        await b.start()
        assert await b.health()
        await b.stop()
        assert not await b.health()

    @pytest.mark.asyncio
    async def test_new_context(self):
        b = DummyBrowser()
        await b.start()
        ctx = await b.new_context()
        assert isinstance(ctx, BrowserContext)


class TestBrowserPage:
    @pytest.mark.asyncio
    async def test_goto_sets_url(self):
        page = DummyPage()
        await page.goto("https://example.com")
        assert await page.url() == "https://example.com"

    @pytest.mark.asyncio
    async def test_content(self):
        page = DummyPage()
        assert "Dummy" in await page.content()

    @pytest.mark.asyncio
    async def test_title(self):
        page = DummyPage()
        assert await page.title() == "Dummy Page"


class TestBrowserSession:
    @pytest.mark.asyncio
    async def test_context_manager(self):
        b = DummyBrowser()
        async with BrowserSession(b) as session:
            ctx = await session.new_context()
            page = await ctx.new_page()
            await page.goto("https://example.com")
            assert await page.url() == "https://example.com"


class TestNavigationEngine:
    @pytest.mark.asyncio
    async def test_goto_adds_to_history(self):
        page = DummyPage()
        nav = NavigationEngine(page)
        await nav.goto("https://a.com")
        await nav.goto("https://b.com")
        assert nav.current_url == "https://b.com"

    @pytest.mark.asyncio
    async def test_back(self):
        page = DummyPage()
        nav = NavigationEngine(page)
        await nav.goto("https://a.com")
        await nav.goto("https://b.com")
        await nav.back()
        assert nav.current_url == "https://a.com"


class TestDownloadManager:
    def test_add_and_list(self):
        mgr = DownloadManager()
        mgr.add_download(DownloadInfo(url="http://a.com/f.pdf", size_bytes=1024))
        assert len(mgr.list_downloads()) == 1
        assert mgr.total_bytes == 1024


class TestScreenshotEngine:
    @pytest.mark.asyncio
    async def test_capture(self):
        page = DummyPage()
        engine = ScreenshotEngine(page)
        img = await engine.capture()
        assert isinstance(img, bytes)
        assert len(img) > 0


class TestNetworkManager:
    @pytest.mark.asyncio
    async def test_request_hook(self):
        mgr = NetworkManager()
        received = []
        async def hook(info):
            received.append(info.url)
        mgr.on_request(hook)
        await mgr._handle_request(RequestInfo("https://example.com/api"))
        assert "https://example.com/api" in received

    @pytest.mark.asyncio
    async def test_response_hook(self):
        mgr = NetworkManager()
        results = []
        async def hook(info):
            results.append(info.status)
        mgr.on_response(hook)
        await mgr._handle_response(ResponseInfo("https://x.com", status=404))
        assert 404 in results


class TestRegistry:
    def test_register_and_get(self):
        reg = BrowserRegistry()
        reg.register("dummy", DummyBrowser)
        assert reg.get("dummy") is DummyBrowser

    def test_get_unregistered_raises(self):
        reg = BrowserRegistry()
        with pytest.raises(KeyError):
            reg.get("nonexistent")


class TestFactory:
    def test_create_returns_browser(self):
        browser_registry.register("dummy_test", DummyBrowser)
        factory = BrowserFactory()
        browser = factory.create("dummy_test")
        assert isinstance(browser, Browser)


class TestStress:
    @pytest.mark.asyncio
    async def test_many_contexts_and_pages(self):
        """Stress test — 100 contexts and pages."""
        b = DummyBrowser()
        await b.start()
        for _ in range(100):
            ctx = await b.new_context()
            page = await ctx.new_page()
            await page.goto("https://example.com")
            assert await page.url() == "https://example.com"
            await page.close()
            await ctx.close()
        await b.stop()
