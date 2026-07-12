"""Abstract interfaces — every browser driver must implement these.

Future Playwright, Selenium, CDP drivers implement these ABCs.
The scraper framework only depends on these interfaces, never on
a specific browser vendor.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from browser.models import BrowserConfig, NavigationOptions, ScreenshotOptions, DownloadInfo


class BrowserPage(ABC):
    """A single browser tab/page."""

    @abstractmethod
    async def goto(self, url: str, options: NavigationOptions | None = None) -> None:
        """Navigate to a URL."""
        ...

    @abstractmethod
    async def content(self) -> str:
        """Return the full HTML content of the page."""
        ...

    @abstractmethod
    async def title(self) -> str:
        """Return the page title."""
        ...

    @abstractmethod
    async def url(self) -> str:
        """Return the current URL."""
        ...

    @abstractmethod
    async def wait_for_selector(self, selector: str, timeout: float = 30.0) -> None:
        """Wait for an element matching the CSS selector to appear."""
        ...

    @abstractmethod
    async def click(self, selector: str) -> None:
        """Click an element matching the CSS selector."""
        ...

    @abstractmethod
    async def fill(self, selector: str, value: str) -> None:
        """Type text into an input element."""
        ...

    @abstractmethod
    async def evaluate(self, expression: str) -> Any:
        """Execute JavaScript in the page context."""
        ...

    @abstractmethod
    async def screenshot(self, options: ScreenshotOptions | None = None) -> bytes:
        """Take a screenshot. Returns PNG bytes."""
        ...

    @abstractmethod
    async def reload(self) -> None:
        """Reload the current page."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close this page."""
        ...


class BrowserContext(ABC):
    """An isolated browser session — cookies, storage, permissions."""

    @abstractmethod
    async def new_page(self) -> BrowserPage:
        """Open a new page in this context."""
        ...

    @abstractmethod
    async def set_cookies(self, cookies: list[dict[str, Any]]) -> None:
        """Set cookies for this context."""
        ...

    @abstractmethod
    async def cookies(self) -> list[dict[str, Any]]:
        """Get all cookies for this context."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close this context and all its pages."""
        ...


class Browser(ABC):
    """A browser instance — manages contexts, pages, and lifecycle."""

    @abstractmethod
    async def start(self) -> None:
        """Launch the browser."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully shutdown the browser."""
        ...

    @abstractmethod
    async def new_context(self, config: BrowserConfig | None = None) -> BrowserContext:
        """Create a new isolated browser context."""
        ...

    @abstractmethod
    async def health(self) -> bool:
        """Check if the browser is responsive."""
        ...
