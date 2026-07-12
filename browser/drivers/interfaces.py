"""BrowserDriver interface — what every driver must implement."""

from abc import ABC, abstractmethod
from browser.base.interfaces import Browser
from browser.drivers.models import DriverCapabilities


class BrowserDriver(ABC):
    """Abstract browser driver. Each implementation (Playwright, Selenium, CDP)
    provides one of these. The DriverManager uses this interface to launch
    and manage browser instances regardless of the underlying technology.
    """

    @abstractmethod
    async def launch(self) -> Browser:
        """Create and start a new Browser instance."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the driver and all managed browsers."""
        ...

    @abstractmethod
    async def health(self) -> bool:
        """Check if the driver is operational."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable driver name (e.g., 'playwright-chromium')."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Driver version string."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> DriverCapabilities:
        """What this driver supports."""
        ...
