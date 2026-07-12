"""Abstract interfaces for scraper components.

Every component has a defined contract. Marketplace-specific scrapers
implement only the extraction logic — everything else is inherited.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """Parse raw HTML into structured listing data."""

    @abstractmethod
    async def parse(self, html: str, url: str) -> dict[str, Any]:
        """Extract listing fields from HTML."""
        ...


class BaseStorage(ABC):
    """Store raw HTML, parsed results, and metadata."""

    @abstractmethod
    async def store_raw(self, key: str, content: str, content_type: str = "text/html") -> str:
        """Store raw content. Returns storage key/path."""
        ...

    @abstractmethod
    async def store_result(self, key: str, data: dict) -> str:
        """Store parsed result. Returns storage key/path."""
        ...


class BaseProxy(ABC):
    """Proxy provider abstraction."""

    @abstractmethod
    async def get_proxy(self) -> str | None:
        """Return proxy URL string or None for direct connection."""
        ...
