"""Aggregation engine — average, median, volatility, group-by."""

import time, statistics
from storage.history.repository import HistoryRepository
from analytics.query.models import FilterCriteria, AggregationResult
from analytics.query.filters import apply_filters


class Aggregator:
    def __init__(self, repo: HistoryRepository):
        self._repo = repo

    def average(self, field: str, filters: FilterCriteria | None = None) -> float:
        entries = self._get_filtered(filters)
        if not entries: return 0.0
        vals = [getattr(e, field, 0.0) or 0.0 for e in entries]
        return sum(vals) / len(vals)

    def median(self, field: str, filters: FilterCriteria | None = None) -> float:
        entries = self._get_filtered(filters)
        if not entries: return 0.0
        vals = sorted([getattr(e, field, 0.0) or 0.0 for e in entries])
        return statistics.median(vals) if vals else 0.0

    def volatility(self, field: str, filters: FilterCriteria | None = None) -> float:
        entries = self._get_filtered(filters)
        if len(entries) < 2: return 0.0
        vals = [getattr(e, field, 0.0) or 0.0 for e in entries]
        avg = sum(vals) / len(vals)
        variance = sum((v - avg) ** 2 for v in vals) / len(vals)
        return (variance ** 0.5) / avg if avg > 0 else 0.0

    def aggregate(self, field: str, group_by: str,
                  filters: FilterCriteria | None = None) -> AggregationResult:
        start = time.perf_counter()
        entries = self._get_filtered(filters)
        groups: dict[str, list[float]] = {}
        for e in entries:
            key = getattr(e, group_by, "unknown") if hasattr(e, group_by) else str(getattr(e, "marketplace", ""))
            val = getattr(e, field, 0.0) or 0.0
            groups.setdefault(str(key), []).append(val)

        result = AggregationResult()
        for key, vals in groups.items():
            result.groups.append({
                "key": key, "count": len(vals),
                "average": sum(vals) / len(vals) if vals else 0.0,
                "median": statistics.median(vals) if vals else 0.0,
            })
        result.total_count = len(entries)
        result.query_time_ms = (time.perf_counter() - start) * 1000
        return result

    def _get_filtered(self, filters):
        return apply_filters(self._repo._current, filters) if filters else self._repo._current._store.values()
