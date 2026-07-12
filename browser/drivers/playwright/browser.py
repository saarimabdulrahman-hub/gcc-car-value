"""PlaywrightBrowser — wraps a Playwright Browser behind the Browser ABC."""

from browser.base.interfaces import Browser, BrowserContext
from browser.models import BrowserConfig
from browser.drivers.playwright.context import PlaywrightContext
from browser.drivers.playwright.errors import translate_error


class PlaywrightBrowser(Browser):
    """Wraps a Playwright Browser instance. Creates PlaywrightContext instances."""

    def __init__(self, pw_browser, config: BrowserConfig | None = None):
        self._pw_browser = pw_browser
        self._config = config or BrowserConfig()
        self._started = True

    async def start(self) -> None:
        self._started = True

    async def stop(self) -> None:
        try:
            await self._pw_browser.close()
        except Exception:
            pass
        finally:
            self._started = False

    async def new_context(self, config: BrowserConfig | None = None) -> PlaywrightContext:
        cfg = config or self._config
        try:
            pw_context = await self._pw_browser.new_context(
                viewport={"width": cfg.viewport["width"],
                         "height": cfg.viewport["height"]},
                locale=cfg.locale,
                timezone_id=cfg.timezone,
                proxy={"server": cfg.proxy} if cfg.proxy else None,
                permissions=cfg.permissions,
                ignore_https_errors=cfg.ignore_https_errors,
            )
            return PlaywrightContext(pw_context)
        except Exception as e:
            raise translate_error(e)

    async def health(self) -> bool:
        try:
            return self._pw_browser.is_connected() and self._started
        except Exception:
            return False

    @property
    def _playwright_browser(self):
        return self._pw_browser
