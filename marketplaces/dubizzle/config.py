from dataclasses import dataclass, field

@dataclass
class DubizzleConfig:
    base_url: str = "https://uae.dubizzle.com"
    search_path: str = "/motors/used-cars"
    max_pages: int = 50
    max_listings_per_page: int = 25
    request_delay_seconds: float = 2.0
    checkpoint_enabled: bool = True
    checkpoint_path: str = ".dubizzle_checkpoint.json"
    skip_incomplete: bool = True
    country: str = "AE"
    marketplace_name: str = "dubizzle_uae"
