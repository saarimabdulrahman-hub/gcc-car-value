from abc import ABC, abstractmethod
from ml.features.models import DatasetVersion

class DatasetBuilderInterface(ABC):
    @abstractmethod
    def build(self, **filters) -> DatasetVersion: ...
    @abstractmethod
    def export_csv(self, path: str) -> None: ...
