"""History statistics tracker."""

from pipeline.history.models import LifecycleState


class HistoryStatistics:
    def __init__(self):
        self._counts = {s: 0 for s in LifecycleState}

    def record(self, state: LifecycleState):
        if state in self._counts:
            self._counts[state] += 1

    @property
    def total(self) -> int: return sum(self._counts.values())

    def snapshot(self) -> dict:
        return {
            "total": self.total,
            "new": self._counts.get(LifecycleState.NEW, 0),
            "updated": self._counts.get(LifecycleState.UPDATED, 0),
            "unchanged": self._counts.get(LifecycleState.UNCHANGED, 0),
            "removed": self._counts.get(LifecycleState.REMOVED, 0),
            "duplicate": self._counts.get(LifecycleState.DUPLICATE, 0),
            "archived": self._counts.get(LifecycleState.ARCHIVED, 0),
        }
