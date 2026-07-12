"""Time-Series Engine — daily, weekly, monthly, quarterly, yearly aggregations."""

import time
from storage.history.repository import HistoryRepository
from analytics.query.models import FilterCriteria, TimeSeriesPoint
from analytics.query.filters import apply_filters


class TimeSeriesEngine:
    def __init__(self, repo: HistoryRepository):
        self._repo = repo

    def query(self, metric: str, period: str,
              filters: FilterCriteria | None,
              limit: int = 12) -> list[TimeSeriesPoint]:
        """Build a time-series for the given metric and period."""
        snapshots = self._get_snapshots(filters)
        if not snapshots: return []

        buckets: dict[str, list[float]] = {}
        for s in snapshots:
            key = self._period_key(s.captured_at, period)
            val = self._metric_value(s, metric)
            if val is not None:
                buckets.setdefault(key, []).append(val)

        points = []
        for key in sorted(buckets.keys())[-limit:]:
            vals = buckets[key]
            points.append(TimeSeriesPoint(
                timestamp=self._key_to_ts(key, period),
                period=key, value=sum(vals) / len(vals) if vals else 0.0,
                count=len(vals),
            ))
        return points

    def _period_key(self, ts: float, period: str) -> str:
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        if period == "daily": return dt.strftime("%Y-%m-%d")
        if period == "weekly": return f"{dt.year}-W{dt.isocalendar()[1]:02d}"
        if period == "monthly": return dt.strftime("%Y-%m")
        if period == "quarterly": return f"{dt.year}-Q{(dt.month-1)//3+1}"
        if period == "yearly": return str(dt.year)
        return dt.strftime("%Y-%m")

    def _key_to_ts(self, key: str, period: str) -> float:
        import datetime
        if period == "monthly":
            dt = datetime.datetime.strptime(key, "%Y-%m")
            return dt.replace(tzinfo=datetime.timezone.utc).timestamp()
        return 0.0

    def _metric_value(self, snapshot, metric: str) -> float | None:
        if metric == "price": return snapshot.price if snapshot.price > 0 else None
        if metric == "mileage": return float(snapshot.mileage_km)
        if metric == "count": return 1.0
        return None

    def _get_snapshots(self, filters):
        snapshots = []
        for fp in self._repo._snapshots._store:
            snapshots.extend(self._repo.get_snapshots(fp).values()
                           if hasattr(self._repo.get_snapshots(fp), 'values')
                           else self._repo.get_snapshots(fp))
        return snapshots
