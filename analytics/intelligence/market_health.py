"""Market Health Engine — inventory growth, volatility, freshness, stability score."""

from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import MarketHealth


class MarketHealthEngine:
    def __init__(self, query: QueryEngine): self._query = query

    def compute(self, marketplace: str = "") -> MarketHealth:
        f = FilterCriteria(marketplace=marketplace) if marketplace else None
        seg = marketplace or "overall"

        # Inventory growth: (new - removed) / active
        new_30d = self._query.new_listings(marketplace, days=30, filters=f)
        removed_30d = self._query.removed_listings(marketplace, days=30)
        active = self._query.active_count(marketplace, f)
        growth = ((new_30d - removed_30d) / max(active, 1)) * 100

        # Price volatility
        volatility = self._query.price_volatility(filters=f) * 100

        # Freshness: % of active listings seen in last 7 days
        new_7d = self._query.new_listings(marketplace, days=7, filters=f)
        freshness = (new_7d / max(active, 1)) * 100

        supply_trend = "growing" if growth > 5 else ("shrinking" if growth < -5 else "stable")
        demand = "high" if volatility < 5 and growth < 0 else ("low" if growth > 10 else "moderate")

        # Stability score: higher = more stable market
        stability = max(0, 100 - abs(growth) - volatility - abs(50 - freshness))

        return MarketHealth(
            segment=seg, inventory_growth_pct=round(growth, 1),
            price_volatility_pct=round(volatility, 1),
            listing_freshness_pct=round(freshness, 1),
            supply_trend=supply_trend, demand_proxy=demand,
            stability_score=round(stability, 1),
        )
