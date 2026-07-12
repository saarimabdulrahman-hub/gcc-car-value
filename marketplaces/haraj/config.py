from dataclasses import dataclass, field

@dataclass
class HarajConfig:
    base_url: str = "https://haraj.com.sa"
    search_path: str = "/haraj/cars"
    max_pages: int = 50
    max_listings_per_page: int = 25
    request_delay_seconds: float = 2.0
    checkpoint_enabled: bool = True
    checkpoint_path: str = ".haraj_checkpoint.json"
    skip_incomplete: bool = True
    country: str = "SA"
    marketplace_name: str = "haraj"
