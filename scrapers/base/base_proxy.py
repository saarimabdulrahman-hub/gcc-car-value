"""Proxy abstraction — no-op, residential, datacenter, rotating."""

from scrapers.base.interfaces import BaseProxy


class NoOpProxy(BaseProxy):
    """Direct connection — no proxy."""
    async def get_proxy(self) -> str | None:
        return None


class StaticProxy(BaseProxy):
    """Single static proxy."""
    def __init__(self, proxy_url: str):
        self._url = proxy_url
    async def get_proxy(self) -> str | None:
        return self._url
