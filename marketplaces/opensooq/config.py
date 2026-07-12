"""OpenSooq configuration with multi-country support."""

from dataclasses import dataclass, field
from marketplaces.opensooq.constants import COUNTRY_CONFIGS, DEFAULT_COUNTRY


@dataclass
class OpenSooqConfig:
    country: str = DEFAULT_COUNTRY
    base_url: str = ""
    search_path: str = "/vehicles"
    max_pages: int = 50
    request_delay_seconds: float = 2.0
    checkpoint_enabled: bool = True
    checkpoint_path: str = ""
    skip_incomplete: bool = True
    marketplace_name: str = "opensooq"

    def __post_init__(self):
        cc = COUNTRY_CONFIGS.get(self.country, COUNTRY_CONFIGS[DEFAULT_COUNTRY])
        if not self.base_url:
            self.base_url = cc["base_url"]
        if not self.checkpoint_path:
            self.checkpoint_path = f".opensooq_{self.country}_checkpoint.json"

    @property
    def currency(self) -> str: return COUNTRY_CONFIGS.get(self.country, {}).get("currency", "AED")
    @property
    def locale(self) -> str: return COUNTRY_CONFIGS.get(self.country, {}).get("locale", "ar")
    @property
    def timezone(self) -> str: return COUNTRY_CONFIGS.get(self.country, {}).get("timezone", "Asia/Dubai")
