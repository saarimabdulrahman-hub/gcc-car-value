"""Test driver manager — registry, selection, capabilities, health, concurrency."""
import asyncio
import pytest
from browser.base.interfaces import Browser, BrowserContext, BrowserPage
from browser.drivers.interfaces import BrowserDriver
from browser.drivers.models import DriverCapabilities
from browser.drivers.registry import DriverRegistry
from browser.drivers.manager import DriverManager
from browser.drivers.config import DriverManagerConfig
from browser.drivers.errors import DriverNotFoundError, DriverRegistrationError


# Dummy browser (same as in pool tests)
class _Page(BrowserPage):
    async def goto(self, u, o=None): pass
    async def content(self): return ""
    async def title(self): return ""
    async def url(self): return ""
    async def wait_for_selector(self, s, t=30): pass
    async def click(self, s): pass
    async def fill(self, s, v): pass
    async def evaluate(self, e): return None
    async def screenshot(self, o=None): return b""
    async def reload(self): pass
    async def close(self): pass

class _Context(BrowserContext):
    async def new_page(self): return _Page()
    async def set_cookies(self, c): pass
    async def cookies(self): return []
    async def close(self): pass

class _Browser(Browser):
    def __init__(self): self._ok = True
    async def start(self): pass
    async def stop(self): pass
    async def new_context(self, c=None): return _Context()
    async def health(self): return self._ok


# Dummy drivers
class DummyChromiumDriver(BrowserDriver):
    @property
    def name(self): return "dummy-chromium"
    @property
    def version(self): return "1.0.0"
    @property
    def capabilities(self):
        return DriverCapabilities(
            browser_type="chromium", headless=True,
            screenshots=True, downloads=True,
        )
    async def launch(self): return _Browser()
    async def shutdown(self): pass
    async def health(self): return True

class DummyFirefoxDriver(BrowserDriver):
    @property
    def name(self): return "dummy-firefox"
    @property
    def version(self): return "2.0.0"
    @property
    def capabilities(self):
        return DriverCapabilities(
            browser_type="firefox", headless=True,
            screenshots=True, pdf=True,
        )
    async def launch(self): return _Browser()
    async def shutdown(self): pass
    async def health(self): return True


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestDriverRegistry:
    @pytest.mark.asyncio
    async def test_register_and_get(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        cls = await reg.get("dummy-chromium")
        assert cls is DummyChromiumDriver

    @pytest.mark.asyncio
    async def test_duplicate_registration_raises(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        with pytest.raises(DriverRegistrationError):
            await reg.register(DummyChromiumDriver)

    @pytest.mark.asyncio
    async def test_unregister(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        await reg.unregister("dummy-chromium")
        with pytest.raises(DriverNotFoundError):
            await reg.get("dummy-chromium")

    @pytest.mark.asyncio
    async def test_default_driver(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        default = await reg.get_default()
        assert default is DummyChromiumDriver

    @pytest.mark.asyncio
    async def test_find_by_browser_type(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        await reg.register(DummyFirefoxDriver)
        found = await reg.find_by_browser_type("firefox")
        assert found is DummyFirefoxDriver

    @pytest.mark.asyncio
    async def test_list_all(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        await reg.register(DummyFirefoxDriver)
        names = await reg.list_all()
        assert len(names) == 2


class TestDriverManager:
    @pytest.fixture
    async def mgr(self):
        reg = DriverRegistry()
        await reg.register(DummyChromiumDriver)
        await reg.register(DummyFirefoxDriver)
        m = DriverManager(reg, DriverManagerConfig(preferred_driver="dummy-chromium"))
        yield m
        await m.shutdown()

    @pytest.mark.asyncio
    async def test_launch_with_preferred(self, mgr):
        browser = await mgr.launch(prefer="dummy-chromium")
        assert isinstance(browser, Browser)
        info = await mgr.get_driver_info("dummy-chromium")
        assert info is not None
        assert info.launch_count == 1

    @pytest.mark.asyncio
    async def test_launch_unknown_driver_falls_back(self, mgr):
        """When preferred driver not found, falls back to default."""
        browser = await mgr.launch(prefer="nonexistent")
        assert isinstance(browser, Browser)

    @pytest.mark.asyncio
    async def test_health_checks(self, mgr):
        await mgr.launch(prefer="dummy-chromium")
        results = await mgr.run_health_checks()
        assert "dummy-chromium" in results
        assert results["dummy-chromium"] is True

    @pytest.mark.asyncio
    async def test_list_drivers(self, mgr):
        names = await mgr.list_drivers()
        assert "dummy-chromium" in names
        assert "dummy-firefox" in names


class TestCapabilities:
    def test_chromium_capabilities(self):
        d = DummyChromiumDriver()
        assert d.capabilities.browser_type == "chromium"
        assert d.capabilities.headless is True

    def test_firefox_capabilities(self):
        d = DummyFirefoxDriver()
        assert d.capabilities.browser_type == "firefox"
        assert d.capabilities.pdf is True

    def test_capability_matching(self):
        from browser.drivers.capabilities import CapabilityResolver
        resolver = CapabilityResolver()
        cap = DriverCapabilities(browser_type="chromium", headless=True, screenshots=True)
        assert resolver.matches(cap, {"headless": True})
        assert resolver.matches(cap, {"headless": True, "screenshots": True})
        assert not resolver.matches(cap, {"pdf": True})


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_registration(self):
        """Multiple concurrent registrations are safe."""
        reg = DriverRegistry()

        async def register_one(i):
            class DynamicDriver(BrowserDriver):
                @property
                def name(self): return f"dynamic-{i}"
                @property
                def version(self): return "1.0"
                @property
                def capabilities(self): return DriverCapabilities()
                async def launch(self): return _Browser()
                async def shutdown(self): pass
                async def health(self): return True

            await reg.register(DynamicDriver)

        await asyncio.gather(*[register_one(i) for i in range(20)])
        names = await reg.list_all()
        assert len(names) == 20
