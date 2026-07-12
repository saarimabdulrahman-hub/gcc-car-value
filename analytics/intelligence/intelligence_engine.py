"""Market Intelligence Engine — computes market indicators from historical data."""

from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.config import IntelligenceConfig
from analytics.intelligence.price_index import PriceIndexEngine
from analytics.intelligence.depreciation import DepreciationEngine
from analytics.intelligence.liquidity import LiquidityEngine
from analytics.intelligence.market_health import MarketHealthEngine
from analytics.intelligence.benchmark import BenchmarkEngine
from analytics.intelligence.forecast_inputs import ForecastInputBuilder
from analytics.intelligence.models import (
    PriceIndex, DepreciationCurve, LiquidityMetrics,
    MarketHealth, Benchmark, ForecastInputs,
)


class IntelligenceEngine:
    """Read-only market intelligence engine.

    Usage:
        engine = IntelligenceEngine(query_engine)
        index = engine.price_index(make="Toyota", model="Land Cruiser")
        curve = engine.depreciation(make="Camry")
        health = engine.market_health(marketplace="dubizzle")
    """

    def __init__(self, query_engine: QueryEngine,
                 config: IntelligenceConfig | None = None):
        self._query = query_engine
        self.config = config or IntelligenceConfig()
        self._price_index = PriceIndexEngine(query_engine)
        self._depreciation = DepreciationEngine(query_engine)
        self._liquidity = LiquidityEngine(query_engine)
        self._health = MarketHealthEngine(query_engine)
        self._benchmark = BenchmarkEngine(query_engine)
        self._forecast = ForecastInputBuilder(query_engine)

    # ------------------------------------------------------------------
    # Price Index
    # ------------------------------------------------------------------

    def price_index(self, make: str = "", model: str = "",
                    marketplace: str = "", country: str = "",
                    city: str = "") -> PriceIndex:
        return self._price_index.compute(
            make=make, model=model, marketplace=marketplace,
            country=country, city=city,
        )

    # ------------------------------------------------------------------
    # Depreciation
    # ------------------------------------------------------------------

    def depreciation(self, make: str, model: str) -> DepreciationCurve:
        return self._depreciation.compute(make, model)

    def depreciation_by_marketplace(self, make: str, model: str,
                                    marketplace: str) -> DepreciationCurve:
        return self._depreciation.compute(make, model, marketplace)

    # ------------------------------------------------------------------
    # Liquidity
    # ------------------------------------------------------------------

    def liquidity(self, make: str = "", model: str = "",
                  marketplace: str = "") -> LiquidityMetrics:
        return self._liquidity.compute(make, model, marketplace)

    # ------------------------------------------------------------------
    # Market Health
    # ------------------------------------------------------------------

    def market_health(self, marketplace: str = "") -> MarketHealth:
        return self._health.compute(marketplace)

    # ------------------------------------------------------------------
    # Benchmarks
    # ------------------------------------------------------------------

    def benchmark(self, make: str, model: str,
                  marketplace: str = "", country: str = "") -> Benchmark:
        return self._benchmark.compute(make, model, marketplace, country)

    def price_bands(self, make: str, model: str) -> list[Benchmark]:
        return self._benchmark.price_bands(make, model)

    # ------------------------------------------------------------------
    # Forecast Inputs
    # ------------------------------------------------------------------

    def forecast_inputs(self, make: str = "", model: str = "",
                        marketplace: str = "") -> ForecastInputs:
        return self._forecast.compute(make, model, marketplace)
