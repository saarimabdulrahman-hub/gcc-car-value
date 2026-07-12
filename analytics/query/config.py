from dataclasses import dataclass

@dataclass
class AnalyticsConfig:
    cache_ttl_seconds: float = 300.0
    default_limit: int = 100
    max_limit: int = 1000
    cache_enabled: bool = True
