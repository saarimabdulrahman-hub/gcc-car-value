"""Inventory Analytics — active, new, removed, duration stats."""

import time
from storage.history.repository import HistoryRepository
from analytics.query.models import FilterCriteria
from analytics.query.filters import apply_filters


class InventoryAnalytics:
    def __init__(self, repo: HistoryRepository):
        self._repo = repo

    def active_count(self, marketplace: str = "",
                     filters: FilterCriteria | None = None) -> int:
        f = filters or FilterCriteria(marketplace=marketplace)
        entries = apply_filters(self._repo._current, f)
        return len([e for e in entries if e.status != "removed"])

    def new_count(self, marketplace: str = "", days: int = 7,
                  filters: FilterCriteria | None = None) -> int:
        f = filters or FilterCriteria(marketplace=marketplace)
        cutoff = time.time() - (days * 86400)
        entries = apply_filters(self._repo._current, f)
        return len([e for e in entries if e.last_updated >= cutoff and e.status != "removed"])

    def removed_count(self, marketplace: str = "", days: int = 7) -> int:
        removed = self._repo.list_removed()
        cutoff = time.time() - (days * 86400)
        if marketplace:
            removed = [e for e in removed if e.marketplace == marketplace]
        return len([e for e in removed if e.last_updated >= cutoff])

    def average_duration(self, marketplace: str = "",
                         filters: FilterCriteria | None = None) -> float:
        """Average days from first_seen to last_seen for active listings."""
        f = filters or FilterCriteria(marketplace=marketplace)
        entries = apply_filters(self._repo._current, f)
        durations = []
        for e in entries:
            fp = e.fingerprint
            snapshots = self._repo.get_snapshots(fp)
            if len(snapshots) >= 2:
                duration = snapshots[-1].captured_at - snapshots[0].captured_at
                durations.append(duration / 86400.0)
        return sum(durations) / len(durations) if durations else 0.0
