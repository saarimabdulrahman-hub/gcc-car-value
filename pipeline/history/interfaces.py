from abc import ABC, abstractmethod
from pipeline.history.models import ListingHistory, ListingSnapshot

class HistoryStore(ABC):
    """Abstract history persistence. Future: DB, file, cloud."""
    @abstractmethod
    def save(self, history: ListingHistory) -> None: ...
    @abstractmethod
    def load(self, fingerprint: str) -> ListingHistory | None: ...
    @abstractmethod
    def list_all(self) -> list[ListingHistory]: ...
