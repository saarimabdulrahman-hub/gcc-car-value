"""Discovery — generate search URLs for Dubizzle UAE."""

from marketplaces.dubizzle.config import DubizzleConfig
from marketplaces.dubizzle.constants import SEARCH_URL


class DubizzleDiscovery:
    """Generates search URLs for Dubizzle UAE.

    Supports brand, price range, and category filters. All URLs are
    constructed from config — no hardcoded paths.
    """

    def __init__(self, config: DubizzleConfig | None = None):
        self.config = config or DubizzleConfig()

    def search_url(self, page: int = 1,
                   make: str = "", model: str = "",
                   year_min: int = 0, year_max: int = 0,
                   price_min: int = 0, price_max: int = 0) -> str:
        """Generate a search URL with optional filters."""
        base = f"{self.config.base_url}{self.config.search_path}"

        params = []
        if make:
            params.append(f"make={make.replace(' ', '-').lower()}")
        if model:
            params.append(f"model={model.replace(' ', '-').lower()}")
        if year_min:
            params.append(f"year_min={year_min}")
        if year_max:
            params.append(f"year_max={year_max}")
        if price_min:
            params.append(f"price_min={price_min}")
        if price_max:
            params.append(f"price_max={price_max}")
        if page > 1:
            params.append(f"page={page}")

        if params:
            return f"{base}?{'&'.join(params)}"
        if page > 1:
            return f"{base}?page={page}"
        return base

    def listing_url(self, listing_id: str) -> str:
        """Generate a detail page URL from a listing ID."""
        return f"{self.config.base_url}/motors/used-cars/{listing_id}"

    def seed_urls(self) -> list[str]:
        """Return seed URLs for initial crawl — popular makes."""
        makes = ["toyota", "nissan", "honda", "hyundai", "bmw", "mercedes"]
        return [self.search_url(make=m) for m in makes]
