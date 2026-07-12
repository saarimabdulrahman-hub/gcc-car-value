"""Analytics Query Engine — read-only analytical queries on historical dataset."""

import time
import structlog
from storage.history.repository import HistoryRepository
from analytics.query.config import AnalyticsConfig
from analytics.query.models import FilterCriteria, AggregationResult, TrendResult, TimeSeriesPoint
from analytics.query.filters import apply_filters
from analytics.query.aggregator import Aggregator
from analytics.query.trends import TrendEngine
from analytics.query.inventory import InventoryAnalytics
from analytics.query.price_history import PriceHistoryAnalyzer
from analytics.query.time_series import TimeSeriesEngine
from analytics.query.cache import QueryCache

logger = structlog.get_logger()


class QueryEngine:
    """Read-only analytics query engine over the historical dataset.

    Usage:
        engine = QueryEngine(repository)
        avg = engine.average_price(make="Toyota", model="Camry")
        trend = engine.price_trend(make="Land Cruiser")
    """

    def __init__(self, repo: HistoryRepository, config: AnalyticsConfig | None = None):
        self._repo = repo
        self.config = config or AnalyticsConfig()
        self._aggregator = Aggregator(repo)
        self._trends = TrendEngine(repo)
        self._inventory = InventoryAnalytics(repo)
        self._price_history = PriceHistoryAnalyzer(repo)
        self._time_series = TimeSeriesEngine(repo)
        self._cache = QueryCache(self.config.cache_ttl_seconds)

    # ------------------------------------------------------------------
    # Price History
    # ------------------------------------------------------------------

    def price_history(self, fingerprint: str) -> list[dict]:
        return self._price_history.get(fingerprint)

    def average_price(self, make: str = "", model: str = "",
                      marketplace: str = "", filters: FilterCriteria | None = None) -> float:
        f = filters or FilterCriteria(make=make, model=model, marketplace=marketplace)
        return self._aggregator.average("price", f)

    def median_price(self, make: str = "", model: str = "",
                     marketplace: str = "",
                     filters: FilterCriteria | None = None) -> float:
        f = filters or FilterCriteria(make=make, model=model, marketplace=marketplace)
        return self._aggregator.median("price", f)

    def price_volatility(self, make: str = "", model: str = "",
                         filters: FilterCriteria | None = None) -> float:
        f = filters or FilterCriteria(make=make, model=model)
        return self._aggregator.volatility("price", f)

    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------

    def active_count(self, marketplace: str = "",
                     filters: FilterCriteria | None = None) -> int:
        return self._inventory.active_count(marketplace, filters)

    def new_listings(self, marketplace: str = "",
                     days: int = 7,
                     filters: FilterCriteria | None = None) -> int:
        return self._inventory.new_count(marketplace, days, filters)

    def removed_listings(self, marketplace: str = "",
                         days: int = 7) -> int:
        return self._inventory.removed_count(marketplace, days)

    def average_duration(self, marketplace: str = "",
                         filters: FilterCriteria | None = None) -> float:
        return self._inventory.average_duration(marketplace, filters)

    # ------------------------------------------------------------------
    # Trends
    # ------------------------------------------------------------------

    def price_trend(self, make: str = "", model: str = "",
                    marketplace: str = "",
                    periods: int = 4,
                    filters: FilterCriteria | None = None) -> TrendResult:
        f = filters or FilterCriteria(make=make, model=model, marketplace=marketplace)
        return self._trends.price_trend(f, periods=periods)

    def inventory_trend(self, marketplace: str = "",
                        periods: int = 4) -> TrendResult:
        return self._trends.inventory_trend(marketplace, periods)

    # ------------------------------------------------------------------
    # Time-Series
    # ------------------------------------------------------------------

    def time_series(self, metric: str = "price",
                    period: str = "monthly",
                    filters: FilterCriteria | None = None,
                    limit: int = 12) -> list[TimeSeriesPoint]:
        return self._time_series.query(metric, period, filters, limit)

    def monthly_average(self, make: str = "", model: str = "",
                        months: int = 12,
                        filters: FilterCriteria | None = None) -> list[TimeSeriesPoint]:
        f = filters or FilterCriteria(make=make, model=model)
        return self._time_series.query("price", "monthly", f, months)

    # ------------------------------------------------------------------
    # Aggregations
    # ------------------------------------------------------------------

    def aggregate(self, field: str, group_by: str = "marketplace",
                  filters: FilterCriteria | None = None) -> AggregationResult:
        return self._aggregator.aggregate(field, group_by, filters)
