"""Browser base class with events and metrics — driver-agnostic.

Future Playwright/Selenium drivers inherit from this and implement the
Browser interface. This class adds event emission and metrics collection
that all drivers share.
"""

from __future__ import annotations

from browser.base.interfaces import Browser, BrowserContext, BrowserPage
from browser.models import BrowserConfig


class BaseBrowser(Browser):
    """Browser with event bus and metrics. Drivers extend this."""

    def __init__(self, config: BrowserConfig):
        self.config = config
        self._started = False

    async def start(self) -> None:
        self._started = True

    async def stop(self) -> None:
        self._started = False

    async def health(self) -> bool:
        return self._started

    async def new_context(self, config: BrowserConfig | None = None) -> BrowserContext:
        raise NotImplementedError
