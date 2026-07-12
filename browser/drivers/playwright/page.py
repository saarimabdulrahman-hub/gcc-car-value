"""PlaywrightPage — wraps a Playwright Page behind the BrowserPage ABC.

All Playwright objects stay inside this module. No Playwright types escape.
"""

from browser.base.interfaces import BrowserPage
from browser.models import NavigationOptions, ScreenshotOptions
from browser.drivers.playwright.errors import translate_error


class PlaywrightPage(BrowserPage):
    """Wraps a Playwright Page object. Every method delegates to Playwright
    and translates errors to platform exceptions."""

    def __init__(self, pw_page):
        self._pw_page = pw_page

    async def goto(self, url: str, options: NavigationOptions | None = None) -> None:
        opts = options or NavigationOptions()
        try:
            await self._pw_page.goto(
                url,
                timeout=opts.timeout * 1000,
                wait_until=opts.wait_until,
                referer=opts.referer or "",
            )
        except Exception as e:
            raise translate_error(e)

    async def content(self) -> str:
        try:
            return await self._pw_page.content()
        except Exception as e:
            raise translate_error(e)

    async def title(self) -> str:
        try:
            return await self._pw_page.title()
        except Exception as e:
            raise translate_error(e)

    async def url(self) -> str:
        return self._pw_page.url

    async def wait_for_selector(self, selector: str, timeout: float = 30.0) -> None:
        try:
            await self._pw_page.wait_for_selector(
                selector, timeout=timeout * 1000
            )
        except Exception as e:
            raise translate_error(e)

    async def click(self, selector: str) -> None:
        try:
            await self._pw_page.click(selector)
        except Exception as e:
            raise translate_error(e)

    async def fill(self, selector: str, value: str) -> None:
        try:
            await self._pw_page.fill(selector, value)
        except Exception as e:
            raise translate_error(e)

    async def evaluate(self, expression: str):
        try:
            return await self._pw_page.evaluate(expression)
        except Exception as e:
            raise translate_error(e)

    async def screenshot(self, options: ScreenshotOptions | None = None) -> bytes:
        opts = options or ScreenshotOptions()
        try:
            return await self._pw_page.screenshot(
                full_page=opts.full_page,
                clip=opts.clip,
                type=opts.type,
                quality=opts.quality if opts.type == "jpeg" else None,
            )
        except Exception as e:
            raise translate_error(e)

    async def reload(self) -> None:
        try:
            await self._pw_page.reload()
        except Exception as e:
            raise translate_error(e)

    async def close(self) -> None:
        try:
            await self._pw_page.close()
        except Exception:
            pass

    # Internal accessor — only for PlaywrightContext (same package)
    @property
    def _playwright_page(self):
        return self._pw_page
