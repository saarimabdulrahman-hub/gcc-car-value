"""BrowserContext — isolated session with cookies, storage, permissions."""

from browser.base.interfaces import BrowserContext, BrowserPage


class BaseBrowserContext(BrowserContext):
    """Base context that drivers extend with real browser implementation."""

    def __init__(self):
        self._pages: list[BrowserPage] = []

    async def new_page(self) -> BrowserPage:
        raise NotImplementedError

    async def set_cookies(self, cookies: list[dict]) -> None:
        pass

    async def cookies(self) -> list[dict]:
        return []

    async def close(self) -> None:
        for page in self._pages:
            await page.close()
        self._pages.clear()
