"""Scraper factory — instantiate scrapers with dependency injection."""

from scrapers.base.base_scraper import BaseScraper
from scrapers.models import ScraperConfig
from scrapers.registry import scraper_registry


class ScraperFactory:
    """Create scraper instances from the registry.

    Usage:
        factory = ScraperFactory()
        scraper = factory.create("dubizzle_uae", config)
        result = await scraper.run()
    """

    def __init__(self):
        self._registry = scraper_registry

    def create(self, marketplace: str,
               config: ScraperConfig | None = None) -> BaseScraper:
        """Instantiate a scraper for the given marketplace.

        Args:
            marketplace: Registered marketplace name (e.g., 'dubizzle_uae').
            config: ScraperConfig. If None, creates a default config.

        Returns:
            A BaseScraper subclass instance ready to run.

        Raises:
            KeyError: If marketplace is not registered.
        """
        scraper_cls = self._registry.get(marketplace)
        cfg = config or ScraperConfig(marketplace=marketplace)
        return scraper_cls(cfg)

    def create_all(self, configs: list[ScraperConfig]) -> list[BaseScraper]:
        """Create scrapers for multiple marketplaces."""
        scrapers = []
        for cfg in configs:
            scrapers.append(self.create(cfg.marketplace, cfg))
        return scrapers

    def list_available(self) -> list[str]:
        """List all registered marketplaces."""
        return self._registry.list_marketplaces()
