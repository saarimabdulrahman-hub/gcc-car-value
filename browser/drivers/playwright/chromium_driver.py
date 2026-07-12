"""PlaywrightChromiumDriver — implements BrowserDriver for Chromium via Playwright.

This is the entry point that the DriverManager uses. All Playwright objects
are created and managed inside this module. The rest of the platform sees
only Browser/BrowserContext/BrowserPage ABCs.
"""

from __future__ import annotations

import time
import structlog

from browser.drivers.interfaces import BrowserDriver
from browser.drivers.models import DriverCapabilities
from browser.drivers.playwright.config import PlaywrightChromiumConfig
from browser.drivers.playwright.browser import PlaywrightBrowser
from browser.drivers.playwright.errors import _import_playwright, translate_error

logger = structlog.get_logger()


class PlaywrightChromiumDriver(BrowserDriver):
    """Playwright-based Chromium driver.

    Implements the BrowserDriver interface. The DriverManager calls
    launch() to get a Browser instance. All Playwright internals are
    encapsulated — nothing Playwright-specific leaks out.

    Usage (via DriverManager, never directly):
        mgr = DriverManager(registry)
        browser = await mgr.launch(prefer="playwright-chromium")
    """

    def __init__(self, config: PlaywrightChromiumConfig | None = None):
        self._config = config or PlaywrightChromiumConfig()
        self._pw = None            # Playwright instance
        self._pw_browser = None    # Raw Playwright browser
        self._browser: PlaywrightBrowser | None = None
        self._launch_count = 0
        self._crash_count = 0

    # ------------------------------------------------------------------
    # BrowserDriver interface
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "playwright-chromium"

    @property
    def version(self) -> str:
        try:
            import playwright
            return playwright.__version__ if hasattr(playwright, '__version__') else "unknown"
        except ImportError:
            return "not-installed"

    @property
    def capabilities(self) -> DriverCapabilities:
        return DriverCapabilities(
            browser_type="chromium",
            headless=True,
            extensions=False,
            downloads=True,
            screenshots=True,
            pdf=True,
            video=False,
            har_recording=False,
            tracing=False,
            proxy_support=True,
            mobile_emulation=False,
            geolocation=False,
            permissions=True,
            network_interception=False,
        )

    async def launch(self) -> PlaywrightBrowser:
        """Launch Chromium via Playwright.

        Uses BinaryManager to locate the browser executable if configured.
        Falls back to Playwright's built-in browser discovery.
        """
        async_playwright, err = _import_playwright()
        if async_playwright is None:
            raise RuntimeError(err)

        start = time.monotonic()

        try:
            self._pw = await async_playwright().start()
            cfg = self._config

            launch_kwargs = {
                "headless": cfg.headless,
                "args": list(cfg.args),
                **cfg.extra_launch_options,
            }

            if cfg.proxy:
                launch_kwargs["proxy"] = {"server": cfg.proxy}

            # Try BinaryManager for executable path
            try:
                from browser.binaries.manager import BinaryManager
                from browser.binaries.config import BinaryManagerConfig
                binary_mgr = BinaryManager(BinaryManagerConfig())
                binary = await binary_mgr.resolve("chromium")
                launch_kwargs["executable_path"] = binary.executable_path
            except Exception:
                pass  # Let Playwright use its own Chromium

            self._pw_browser = await self._pw.chromium.launch(**launch_kwargs)
            self._browser = PlaywrightBrowser(self._pw_browser)
            self._launch_count += 1

            launch_ms = (time.monotonic() - start) * 1000
            logger.info("playwright_chromium_launched",
                       headless=cfg.headless,
                       launch_ms=round(launch_ms, 1))

            return self._browser

        except Exception as e:
            self._crash_count += 1
            raise translate_error(e)

    async def shutdown(self) -> None:
        """Shutdown Playwright and the browser."""
        try:
            if self._browser:
                await self._browser.stop()
        except Exception:
            pass
        try:
            if self._pw:
                await self._pw.stop()
        except Exception:
            pass
        self._browser = None
        self._pw_browser = None
        self._pw = None

    async def health(self) -> bool:
        """Check if the driver is operational."""
        if self._browser is None:
            return False
        return await self._browser.health()

    @property
    def launch_count(self) -> int:
        return self._launch_count

    @property
    def crash_count(self) -> int:
        return self._crash_count
