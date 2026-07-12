"""Base driver implementation — common functionality for all drivers."""

from browser.drivers.interfaces import BrowserDriver
from browser.drivers.models import DriverCapabilities


class BaseDriver(BrowserDriver):
    """Base class for driver implementations. Real drivers extend this."""

    @property
    def name(self) -> str:
        return "base"

    @property
    def version(self) -> str:
        return "0.0.0"

    @property
    def capabilities(self) -> DriverCapabilities:
        return DriverCapabilities()
