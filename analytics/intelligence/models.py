"""Market intelligence data models."""

from dataclasses import dataclass, field


@dataclass
class PriceIndex:
    """A price index value for a specific segment."""
    segment: str                    # e.g., "toyota_camry", "dubizzle_uae", "AE_Dubai"
    index_type: str                 # "make", "model", "marketplace", "country", "city"
    current_index: float = 100.0    # Current index value (base = 100)
    previous_index: float = 100.0   # Previous period's index
    change_pct: float = 0.0
    sample_count: int = 0
    base_period: str = ""


@dataclass
class DepreciationCurve:
    """Depreciation data for a vehicle segment."""
    make: str = ""
    model: str = ""
    avg_annual_depreciation_pct: float = 0.0
    median_depreciation_pct: float = 0.0
    data_points: list[dict] = field(default_factory=list)  # [{age_years, residual_pct, sample_count}]
    mileage_factor: float = 0.0     # Price change per 10,000 km


@dataclass
class LiquidityMetrics:
    """How quickly vehicles sell in a segment."""
    segment: str = ""
    avg_days_active: float = 0.0
    median_days_active: float = 0.0
    days_to_sell_estimate: float = 0.0
    inventory_turnover_30d: float = 0.0    # % of inventory that sold in last 30 days
    new_listing_rate_7d: int = 0
    removal_rate_7d: int = 0


@dataclass
class MarketHealth:
    """Overall health indicators for a market segment."""
    segment: str = ""
    inventory_growth_pct: float = 0.0
    price_volatility_pct: float = 0.0
    avg_discount_pct: float = 0.0        # Difference between asking and selling prices
    listing_freshness_pct: float = 0.0   # % of listings seen in last 7 days
    supply_trend: str = "stable"          # growing, shrinking, stable
    demand_proxy: str = "moderate"        # high, moderate, low
    stability_score: float = 0.0          # 0-100


@dataclass
class Benchmark:
    """A benchmark price for a vehicle segment."""
    make: str = ""; model: str = ""
    marketplace: str = ""; country: str = ""
    p10: float = 0.0; p25: float = 0.0; p50: float = 0.0
    p75: float = 0.0; p90: float = 0.0
    avg_price: float = 0.0; sample_count: int = 0


@dataclass
class ForecastInputs:
    """Features for future ML forecasting models."""
    segment: str = ""
    ma_30d: float = 0.0
    volatility_90d: float = 0.0
    inventory_delta_30d: float = 0.0
    price_velocity: float = 0.0          # Rate of price change per day
    market_momentum: float = 0.0
