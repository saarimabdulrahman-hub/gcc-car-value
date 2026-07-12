"""Browser session — manages browser lifecycle, contexts, and pages."""

from browser.base.interfaces import Browser, BrowserContext
from browser.models import BrowserConfig
from browser.base.browser import BaseBrowser


class BrowserSession:
    """High-level session manager wrapping a Browser driver.

    Usage:
        async with BrowserSession(browser) as session:
            ctx = await session.new_context()
            page = await ctx.new_page()
            await page.goto("https://example.com")
    """

    def __init__(self, browser: Browser):
        self._browser = browser
        self._contexts: list[BrowserContext] = []

    async def __aenter__(self) -> "BrowserSession":
        await self._browser.start()
        return self

    async def __aexit__(self, *args) -> None:
        for ctx in self._contexts:
            await ctx.close()
        await self._browser.stop()

    async def new_context(self, config: BrowserConfig | None = None) -> BrowserContext:
        ctx = await self._browser.new_context(config)
        self._contexts.append(ctx)
        return ctx

    @property
    def browser(self) -> Browser:
        return self._browser
