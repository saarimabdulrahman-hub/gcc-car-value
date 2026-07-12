from abc import ABC, abstractmethod
from normalization.models import FieldNormalization

class FieldNormalizer(ABC):
    """Abstract field normalizer."""
    @abstractmethod
    def normalize(self, raw: str) -> FieldNormalization: ...
