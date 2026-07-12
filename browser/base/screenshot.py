"""Screenshot engine — viewport, full page, element, bytes/file/memory."""

from browser.base.interfaces import BrowserPage
from browser.models import ScreenshotOptions


class ScreenshotEngine:
    """Takes screenshots via a BrowserPage."""

    def __init__(self, page: BrowserPage):
        self._page = page

    async def capture(self, options: ScreenshotOptions | None = None) -> bytes:
        return await self._page.screenshot(options)

    async def capture_full_page(self) -> bytes:
        return await self._page.screenshot(ScreenshotOptions(full_page=True))
