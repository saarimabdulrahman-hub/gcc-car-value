from abc import ABC, abstractmethod
from analytics.query.models import FilterCriteria, AggregationResult

class AnalyticsEngine(ABC):
    @abstractmethod
    def aggregate(self, field: str, group_by: str, filters: FilterCriteria | None = None) -> AggregationResult: ...
