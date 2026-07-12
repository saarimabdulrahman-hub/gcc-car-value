"""Scraper registry — central registration of marketplace scraper classes."""

from typing import Type
from scrapers.base.base_scraper import BaseScraper


class ScraperRegistry:
    """Registry of scraper classes by marketplace name.

    Usage:
        registry = ScraperRegistry()
        registry.register("dubizzle_uae", DubizzleUAEScraper)
        cls = registry.get("dubizzle_uae")
    """

    def __init__(self):
        self._scrapers: dict[str, Type[BaseScraper]] = {}

    def register(self, marketplace: str, scraper_cls: Type[BaseScraper]) -> None:
        """Register a scraper class for a marketplace."""
        self._scrapers[marketplace] = scraper_cls

    def get(self, marketplace: str) -> Type[BaseScraper]:
        """Get a registered scraper class.

        Raises KeyError if not registered.
        """
        if marketplace not in self._scrapers:
            raise KeyError(
                f"No scraper registered for marketplace '{marketplace}'. "
                f"Available: {list(self._scrapers.keys())}"
            )
        return self._scrapers[marketplace]

    def list_marketplaces(self) -> list[str]:
        """List all registered marketplace names."""
        return sorted(self._scrapers.keys())

    def is_registered(self, marketplace: str) -> bool:
        """Check if a marketplace has a registered scraper."""
        return marketplace in self._scrapers


# Global singleton
scraper_registry = ScraperRegistry()
