"""Liquidity Engine — listing duration, days-to-sell, turnover, new/removal rates."""

import statistics
from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import LiquidityMetrics


class LiquidityEngine:
    def __init__(self, query: QueryEngine): self._query = query

    def compute(self, make: str = "", model: str = "",
                marketplace: str = "") -> LiquidityMetrics:
        seg = f"{make}_{model}_{marketplace}" if any([make, model, marketplace]) else "overall"
        f = FilterCriteria(make=make, model=model, marketplace=marketplace)
        avg_dur = self._query.average_duration(filters=f)
        new_7d = self._query.new_listings(marketplace, days=7, filters=f)
        removed_7d = self._query.removed_listings(marketplace, days=7)

        active = self._query.active_count(marketplace, f)
        turnover = (removed_7d / active * 100) if active > 0 else 0.0

        return LiquidityMetrics(
            segment=seg, avg_days_active=round(avg_dur, 1),
            days_to_sell_estimate=round(avg_dur * 0.7, 1),  # ~70% of active duration is time-to-sell
            inventory_turnover_30d=round(turnover, 1),
            new_listing_rate_7d=new_7d, removal_rate_7d=removed_7d,
        )
