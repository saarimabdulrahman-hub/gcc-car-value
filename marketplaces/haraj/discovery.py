"""Haraj discovery — generates search URLs for Haraj SA."""

from marketplaces.haraj.config import HarajConfig
from marketplaces.haraj.constants import SEARCH_URL


class HarajDiscovery:
    def __init__(self, config: HarajConfig | None = None):
        self.config = config or HarajConfig()

    def search_url(self, page: int = 1, make: str = "",
                   city: str = "", price_min: int = 0) -> str:
        """Generate a Haraj search URL with optional filters."""
        base = SEARCH_URL
        params = []
        if make:
            params.append(f"make={make}")
        if city:
            params.append(f"city={city}")
        if price_min:
            params.append(f"price_min={price_min}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            return f"{base}?{'&'.join(params)}"
        return base

    def listing_url(self, listing_id: str) -> str:
        return f"{self.config.base_url}/haraj/{listing_id}"

    def seed_urls(self) -> list[str]:
        makes = ["toyota", "nissan", "hyundai", "honda", "ford", "gmc"]
        return [self.search_url(make=m) for m in makes]
