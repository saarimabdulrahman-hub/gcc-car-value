"""Price Index Engine — computes market indexes by segment."""

import statistics
from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import PriceIndex


class PriceIndexEngine:
    def __init__(self, query: QueryEngine): self._query = query

    def compute(self, make: str = "", model: str = "",
                marketplace: str = "", country: str = "",
                city: str = "") -> PriceIndex:
        f = FilterCriteria(make=make, model=model, marketplace=marketplace,
                          country=country, city=city)
        current_avg = self._query.average_price(filters=f)

        # Previous period (30 days offset in time-series)
        prev_points = self._query.time_series("price", "monthly", f, limit=2)
        previous_avg = prev_points[-2].value if len(prev_points) >= 2 else current_avg

        segment = self._segment_name(make, model, marketplace, country, city)
        idx_type = self._index_type(make, model, marketplace, country, city)
        change = ((current_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0.0

        return PriceIndex(
            segment=segment, index_type=idx_type,
            current_index=round(current_avg, 1),
            previous_index=round(previous_avg, 1),
            change_pct=round(change, 1),
            sample_count=self._query.active_count(filters=f),
        )

    def _segment_name(self, *args) -> str:
        parts = [a for a in args if a]; return "_".join(parts) or "overall"
    def _index_type(self, make, model, mp, country, city) -> str:
        if city: return "city"
        if country: return "country"
        if mp: return "marketplace"
        if model: return "model"
        if make: return "make"
        return "overall"
