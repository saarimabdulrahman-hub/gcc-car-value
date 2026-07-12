from abc import ABC, abstractmethod
from pipeline.history.models import ListingHistory, ListingSnapshot
from storage.history.models import CurrentListing

class HistoryStore(ABC):
    @abstractmethod
    def save(self, history: ListingHistory) -> None: ...
    @abstractmethod
    def load_current(self, fingerprint: str) -> CurrentListing | None: ...
    @abstractmethod
    def load_snapshots(self, fingerprint: str) -> list[ListingSnapshot]: ...
