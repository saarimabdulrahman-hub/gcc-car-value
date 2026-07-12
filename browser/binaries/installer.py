"""Binary Installer — abstraction for downloading and installing browser binaries.

Interface only — no actual downloads. Future implementations:
    PlaywrightInstaller  — uses playwright install
    SeleniumManager      — uses selenium's driver manager
    CustomInstaller      — downloads from configurable URLs
"""

from abc import ABC, abstractmethod
from browser.binaries.models import BrowserBinary


class BinaryInstaller(ABC):
    """Abstract browser binary installer."""

    @abstractmethod
    async def install(self, browser_type: str, version: str = "") -> BrowserBinary:
        """Download and install a browser binary. Returns the installed binary."""
        ...

    @abstractmethod
    async def is_installed(self, browser_type: str, version: str = "") -> bool:
        """Check if a browser binary is already installed."""
        ...

    @abstractmethod
    async def uninstall(self, browser_type: str, version: str = "") -> None:
        """Remove a browser binary."""
        ...
