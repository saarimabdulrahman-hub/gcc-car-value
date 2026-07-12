from abc import ABC, abstractmethod
from analytics.intelligence.models import PriceIndex, DepreciationCurve

class MarketIntelligenceProvider(ABC):
    @abstractmethod
    def price_index(self, **kwargs) -> PriceIndex: ...
    @abstractmethod
    def depreciation(self, make: str, model: str) -> DepreciationCurve: ...
