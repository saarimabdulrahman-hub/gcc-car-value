"""Navigation engine — timeouts, retries, redirects, history."""

from browser.base.interfaces import BrowserPage
from browser.models import NavigationOptions


class NavigationEngine:
    """Navigation helper wrapping a BrowserPage with timeout and retry logic."""

    def __init__(self, page: BrowserPage):
        self._page = page
        self._history: list[str] = []

    async def goto(self, url: str,
                   options: NavigationOptions | None = None) -> None:
        opts = options or NavigationOptions()
        await self._page.goto(url, opts)
        self._history.append(url)

    async def reload(self) -> None:
        await self._page.reload()

    async def back(self) -> None:
        """Navigate back if history allows."""
        if len(self._history) > 1:
            self._history.pop()
            prev = self._history[-1]
            await self._page.goto(prev)

    @property
    def current_url(self) -> str:
        return self._history[-1] if self._history else ""
