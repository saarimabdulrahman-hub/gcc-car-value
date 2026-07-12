"""Storage interface — raw HTML, parsed results, metadata."""

from scrapers.base.interfaces import BaseStorage


class NoOpStorage(BaseStorage):
    """Storage that discards everything — for testing."""
    async def store_raw(self, key: str, content: str, content_type: str = "text/html") -> str:
        return key
    async def store_result(self, key: str, data: dict) -> str:
        return key
