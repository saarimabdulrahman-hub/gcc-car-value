"""PlaywrightContext — wraps a Playwright BrowserContext behind the BrowserContext ABC."""

from browser.base.interfaces import BrowserContext
from browser.drivers.playwright.page import PlaywrightPage
from browser.drivers.playwright.errors import translate_error


class PlaywrightContext(BrowserContext):
    """Wraps a Playwright BrowserContext. Creates PlaywrightPage instances."""

    def __init__(self, pw_context):
        self._pw_context = pw_context

    async def new_page(self) -> PlaywrightPage:
        try:
            pw_page = await self._pw_context.new_page()
            return PlaywrightPage(pw_page)
        except Exception as e:
            raise translate_error(e)

    async def set_cookies(self, cookies: list[dict]) -> None:
        try:
            await self._pw_context.add_cookies(cookies)
        except Exception as e:
            raise translate_error(e)

    async def cookies(self) -> list[dict]:
        try:
            return await self._pw_context.cookies()
        except Exception as e:
            raise translate_error(e)

    async def close(self) -> None:
        try:
            await self._pw_context.close()
        except Exception:
            pass

    @property
    def _playwright_context(self):
        return self._pw_context
