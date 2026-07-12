"""Benchmark Engine — price bands, percentile rankings, regional benchmarks."""

import statistics
from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import Benchmark


class BenchmarkEngine:
    def __init__(self, query: QueryEngine): self._query = query

    def compute(self, make: str, model: str,
                marketplace: str = "", country: str = "") -> Benchmark:
        f = FilterCriteria(make=make, model=model, marketplace=marketplace, country=country)
        entries = self._get_filtered(f)
        prices = sorted([e.price for e in entries if e.price > 0])
        if not prices: return Benchmark(make=make, model=model)

        return Benchmark(
            make=make, model=model, marketplace=marketplace, country=country,
            p10=self._pct(prices, 10), p25=self._pct(prices, 25),
            p50=statistics.median(prices), p75=self._pct(prices, 75),
            p90=self._pct(prices, 90),
            avg_price=round(sum(prices) / len(prices)),
            sample_count=len(prices),
        )

    def price_bands(self, make: str, model: str) -> list[Benchmark]:
        """Generate benchmarks per marketplace for a make/model."""
        mps = self._query._repo._current._store.values()
        marketplaces = {e.marketplace for e in mps}
        return [self.compute(make, model, marketplace=mp) for mp in sorted(marketplaces)]

    def _pct(self, prices: list[float], p: int) -> float:
        return round(statistics.median(sorted(prices)[:max(1, len(prices) * p // 100)]), 1)

    def _get_filtered(self, f):
        try:
            return list(self._query._repo._current._store.values())
        except Exception:
            return []
