"""OpenSooq discovery — country-aware URL generation."""

from marketplaces.opensooq.config import OpenSooqConfig


class OpenSooqDiscovery:
    def __init__(self, config: OpenSooqConfig): self.config = config

    def search_url(self, page: int = 1, make: str = "", category: str = "cars") -> str:
        base = f"{self.config.base_url}{self.config.search_path}"
        params = []
        if category: params.append(f"category={category}")
        if make: params.append(f"make={make}")
        if page > 1: params.append(f"page={page}")
        return f"{base}?{'&'.join(params)}" if params else base

    def listing_url(self, listing_id: str) -> str:
        return f"{self.config.base_url}/vehicles/{listing_id}"

    def seed_urls(self) -> list[str]:
        makes = ["toyota", "nissan", "hyundai", "honda", "bmw", "mercedes"]
        return [self.search_url(make=m) for m in makes]
