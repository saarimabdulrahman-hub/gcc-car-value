"""Test Playwright driver — structure, interfaces, error translation.

All tests verify the driver's architecture without needing Playwright installed.
"""
import pytest
from browser.drivers.playwright.errors import translate_error, _import_playwright
from browser.drivers.playwright.config import PlaywrightChromiumConfig
from browser.drivers.playwright.models import PlaywrightSession
from browser.drivers.interfaces import BrowserDriver
from browser.drivers.models import DriverCapabilities


class TestPlaywrightImport:
    def test_missing_playwright_returns_error(self):
        async_playwright, err = _import_playwright()
        if async_playwright is None:
            assert "pip install playwright" in err
        else:
            pytest.skip("Playwright is installed")


class TestErrorTranslation:
    def test_translates_timeout(self):
        class FakeTimeout(Exception): pass
        e = FakeTimeout("Timeout 30000ms exceeded")
        translated = translate_error(e)
        assert "Timeout" in type(translated).__name__

    def test_translates_target_closed(self):
        class TargetClosedError(Exception): pass
        e = TargetClosedError("Target page has been closed")
        translated = translate_error(e)
        assert "PageClosed" in type(translated).__name__ or "Page" in type(translated).__name__

    def test_generic_error_gets_browser_error(self):
        from browser.errors import BrowserError
        translated = translate_error(RuntimeError("something went wrong"))
        assert isinstance(translated, BrowserError)


class TestDriverStructure:
    def test_driver_implements_browser_driver(self):
        """PlaywrightChromiumDriver implements BrowserDriver ABC."""
        # Can't instantiate without Playwright, but verify class hierarchy
        from browser.drivers.playwright.chromium_driver import PlaywrightChromiumDriver
        assert issubclass(PlaywrightChromiumDriver, BrowserDriver)

    def test_driver_name_and_version(self):
        from browser.drivers.playwright.chromium_driver import PlaywrightChromiumDriver
        driver = PlaywrightChromiumDriver()
        assert driver.name == "playwright-chromium"
        assert isinstance(driver.version, str)

    def test_driver_capabilities(self):
        from browser.drivers.playwright.chromium_driver import PlaywrightChromiumDriver
        driver = PlaywrightChromiumDriver()
        caps = driver.capabilities
        assert isinstance(caps, DriverCapabilities)
        assert caps.browser_type == "chromium"
        assert caps.headless is True
        assert caps.screenshots is True

    def test_launch_without_playwright_raises(self):
        from browser.drivers.playwright.chromium_driver import PlaywrightChromiumDriver
        driver = PlaywrightChromiumDriver()
        async_playwright, _ = _import_playwright()
        if async_playwright is None:
            with pytest.raises(RuntimeError, match="Playwright"):
                import asyncio
                asyncio.run(driver.launch())
        else:
            pytest.skip("Playwright is installed — skipping error test")


class TestConfig:
    def test_default_config(self):
        cfg = PlaywrightChromiumConfig()
        assert cfg.headless is True
        assert cfg.viewport_width == 1920
        assert cfg.locale == "en-AE"


class TestSessionModel:
    def test_session_defaults(self):
        s = PlaywrightSession()
        assert s.browser_type == "chromium"
        assert s.healthy is True
        assert s.crash_count == 0


class TestAdapterImports:
    """Verify Playwright adapters exist and have correct class hierarchy."""
    def test_playwright_browser_subclasses_browser(self):
        from browser.base.interfaces import Browser
        from browser.drivers.playwright.browser import PlaywrightBrowser
        assert issubclass(PlaywrightBrowser, Browser)

    def test_playwright_context_subclasses_browser_context(self):
        from browser.base.interfaces import BrowserContext
        from browser.drivers.playwright.context import PlaywrightContext
        assert issubclass(PlaywrightContext, BrowserContext)

    def test_playwright_page_subclasses_browser_page(self):
        from browser.base.interfaces import BrowserPage
        from browser.drivers.playwright.page import PlaywrightPage
        assert issubclass(PlaywrightPage, BrowserPage)
