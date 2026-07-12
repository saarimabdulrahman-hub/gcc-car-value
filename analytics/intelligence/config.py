from dataclasses import dataclass

@dataclass
class IntelligenceConfig:
    index_base_period: str = "2026-01"       # Base month for price index (100)
    depreciation_max_age: int = 15             # Max vehicle age for depreciation calc
    liquidity_active_threshold_days: int = 7   # Listings seen within N days considered active
    market_health_stability_weight: float = 0.3
