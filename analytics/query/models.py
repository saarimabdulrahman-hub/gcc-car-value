"""Analytics query models."""

from dataclasses import dataclass, field


@dataclass
class FilterCriteria:
    """Filter parameters for analytical queries."""
    marketplace: str = ""
    country: str = ""
    city: str = ""
    make: str = ""
    model: str = ""
    year_min: int = 0
    year_max: int = 0
    price_min: float = 0.0
    price_max: float = 0.0
    mileage_min: int = 0
    mileage_max: int = 0
    date_from: float = 0.0
    date_to: float = 0.0
    lifecycle: str = ""
    seller_type: str = ""
    fuel_type: str = ""
    transmission: str = ""
    body_type: str = ""
    limit: int = 100
    offset: int = 0


@dataclass
class AggregationResult:
    """Result of an aggregation query."""
    groups: list[dict] = field(default_factory=list)
    total_count: int = 0
    query_time_ms: float = 0.0


@dataclass
class TimeSeriesPoint:
    """A single point in a time-series."""
    timestamp: float = 0.0
    period: str = ""           # "2026-07", "2026-W27", "2026-07-12"
    value: float = 0.0
    count: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class TrendResult:
    """Trend analysis result."""
    current_value: float = 0.0
    previous_value: float = 0.0
    change_pct: float = 0.0
    direction: str = "stable"   # up, down, stable
    data_points: list[TimeSeriesPoint] = field(default_factory=list)
