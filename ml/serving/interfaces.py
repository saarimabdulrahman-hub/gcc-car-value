from abc import ABC, abstractmethod
from ml.serving.models import PredictionResult

class ModelServerInterface(ABC):
    @abstractmethod
    def predict(self, model_name: str, features: dict) -> PredictionResult: ...
