"""BrowserPage — single tab with navigation, interaction, screenshots."""

from browser.base.interfaces import BrowserPage
from browser.models import NavigationOptions, ScreenshotOptions


class BaseBrowserPage(BrowserPage):
    """Base page that drivers extend with real browser implementation."""

    async def goto(self, url: str, options: NavigationOptions | None = None) -> None:
        raise NotImplementedError

    async def content(self) -> str:
        raise NotImplementedError

    async def title(self) -> str:
        raise NotImplementedError

    async def url(self) -> str:
        raise NotImplementedError

    async def wait_for_selector(self, selector: str, timeout: float = 30.0) -> None:
        raise NotImplementedError

    async def click(self, selector: str) -> None:
        raise NotImplementedError

    async def fill(self, selector: str, value: str) -> None:
        raise NotImplementedError

    async def evaluate(self, expression: str):
        raise NotImplementedError

    async def screenshot(self, options: ScreenshotOptions | None = None) -> bytes:
        raise NotImplementedError

    async def reload(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        pass
