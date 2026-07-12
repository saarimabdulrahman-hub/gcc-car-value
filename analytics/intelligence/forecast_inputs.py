"""Forecast Input Builder — generates features for future ML models."""

from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.intelligence.models import ForecastInputs


class ForecastInputBuilder:
    def __init__(self, query: QueryEngine): self._query = query

    def compute(self, make: str = "", model: str = "",
                marketplace: str = "") -> ForecastInputs:
        seg = f"{make}_{model}_{marketplace}" if any([make, model, marketplace]) else "overall"
        f = FilterCriteria(make=make, model=model, marketplace=marketplace)

        # 30-day moving average
        ts_30d = self._query.time_series("price", "daily", f, limit=30)
        ma_30d = sum(p.value for p in ts_30d) / len(ts_30d) if ts_30d else 0.0

        # 90-day volatility
        ts_90d = self._query.time_series("price", "daily", f, limit=90)
        vals_90d = [p.value for p in ts_90d if p.value > 0]
        if len(vals_90d) >= 2:
            import statistics
            avg_90d = sum(vals_90d) / len(vals_90d)
            variance = sum((v - avg_90d) ** 2 for v in vals_90d) / len(vals_90d)
            volatility_90d = (variance ** 0.5) / avg_90d if avg_90d > 0 else 0.0
        else:
            volatility_90d = 0.0

        # Inventory delta 30d
        inventory_delta = self._query.new_listings(marketplace, days=30, filters=f) - \
                         self._query.removed_listings(marketplace, days=30)

        # Price velocity (rate of change per day)
        if len(ts_30d) >= 2:
            first = ts_30d[0].value
            last = ts_30d[-1].value
            price_velocity = (last - first) / max(len(ts_30d), 1) if first > 0 else 0.0
        else:
            price_velocity = 0.0

        # Market momentum (combines price trend + inventory trend)
        trend = self._query.price_trend(make=make, model=model, marketplace=marketplace, periods=4)
        momentum = trend.change_pct * 0.6 + (inventory_delta * 0.1)

        return ForecastInputs(
            segment=seg, ma_30d=round(ma_30d, 1),
            volatility_90d=round(volatility_90d, 3),
            inventory_delta_30d=round(inventory_delta, 1),
            price_velocity=round(price_velocity, 1),
            market_momentum=round(momentum, 1),
        )
