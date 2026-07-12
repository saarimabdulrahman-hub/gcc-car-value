from abc import ABC, abstractmethod
from ml.training.models import Experiment

class Trainer(ABC):
    @abstractmethod
    def run(self, data: list[dict], model_train_fn, model_predict_fn, **kwargs) -> Experiment: ...
