from dataclasses import dataclass, field

@dataclass
class BinaryManagerConfig:
    configured_paths: list[str] = field(default_factory=list)
    search_path: bool = True
    search_standard_locations: bool = True
    min_chromium_version: str = "100.0.0"
    min_firefox_version: str = "100.0"
    preferred_chromium_version: str = ""
    preferred_firefox_version: str = ""
    cache_ttl_seconds: float = 300.0
