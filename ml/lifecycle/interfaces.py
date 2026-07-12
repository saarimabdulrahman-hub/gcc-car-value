from abc import ABC, abstractmethod
from ml.lifecycle.models import WorkflowRecord

class LifecycleManager(ABC):
    @abstractmethod
    def start(self, model_name: str, trigger) -> WorkflowRecord | None: ...
