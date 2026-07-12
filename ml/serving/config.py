from dataclasses import dataclass, field

@dataclass
class ServingConfig:
    cache_ttl_seconds: float = 300.0
    cache_max_size: int = 10000
    prediction_timeout: float = 5.0
    fallback_enabled: bool = True
    ab_default_split: float = 0.5      # 50/50 split for A/B
    canary_start_pct: float = 0.01     # Start canary at 1%
    canary_increment: float = 0.05     # Increase by 5% each step
    canary_stable_period: int = 300    # Seconds before next increment
