"""Storage statistics tracker."""

from storage.history.repository import HistoryRepository


class StorageStatistics:
    def __init__(self, repo: HistoryRepository): self._repo = repo
    def snapshot(self) -> dict: return self._repo.stats
