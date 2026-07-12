"""Price History Analyzer — vehicle-level and marketplace-level price queries."""

from storage.history.repository import HistoryRepository


class PriceHistoryAnalyzer:
    def __init__(self, repo: HistoryRepository):
        self._repo = repo

    def get(self, fingerprint: str) -> list[dict]:
        return self._repo.get_price_timeline(fingerprint)
