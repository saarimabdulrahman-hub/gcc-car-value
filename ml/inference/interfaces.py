from abc import ABC, abstractmethod

class InferenceEngine(ABC):
    @abstractmethod
    def predict(self, model_name: str, features: dict) -> dict: ...
