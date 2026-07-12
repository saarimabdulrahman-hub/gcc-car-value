from abc import ABC, abstractmethod
from ml.monitoring.models import MonitoringReport

class Monitor(ABC):
    @abstractmethod
    def run(self, model_name: str) -> MonitoringReport: ...
