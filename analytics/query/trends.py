"""Trend Engine — price trends, inventory trends, market growth."""

from storage.history.repository import HistoryRepository
from analytics.query.models import FilterCriteria, TrendResult, TimeSeriesPoint
from analytics.query.time_series import TimeSeriesEngine


class TrendEngine:
    def __init__(self, repo: HistoryRepository):
        self._repo = repo
        self._ts = TimeSeriesEngine(repo)

    def price_trend(self, filters: FilterCriteria,
                    periods: int = 4) -> TrendResult:
        points = self._ts.query("price", "weekly", filters, periods)
        return self._compute_trend(points, "price")

    def inventory_trend(self, marketplace: str,
                        periods: int = 4) -> TrendResult:
        f = FilterCriteria(marketplace=marketplace) if marketplace else None
        points = self._ts.query("count", "weekly", f, periods)
        return self._compute_trend(points, "inventory")

    def _compute_trend(self, points: list[TimeSeriesPoint],
                       metric: str) -> TrendResult:
        if len(points) < 2:
            return TrendResult(data_points=points)
        current = points[-1].value
        previous = points[0].value
        change = ((current - previous) / previous * 100) if previous > 0 else 0.0
        direction = "up" if change > 1 else ("down" if change < -1 else "stable")
        return TrendResult(current_value=current, previous_value=previous,
                          change_pct=round(change, 1), direction=direction,
                          data_points=points)
