"""Experiment Tracker — experiment ID, metadata, timing, hyperparameters."""

import uuid, time
from ml.training.models import Experiment


class ExperimentTracker:
    def __init__(self):
        self._experiments: dict[str, Experiment] = {}

    def create(self, **kwargs) -> Experiment:
        exp_id = str(uuid.uuid4())[:12]
        exp = Experiment(experiment_id=exp_id, **kwargs)
        self._experiments[exp_id] = exp
        return exp

    def complete(self, exp_id: str, metrics: dict) -> Experiment:
        exp = self._experiments.get(exp_id)
        if exp:
            exp.completed_at = time.time()
            exp.duration_seconds = exp.completed_at - exp.started_at
            exp.metrics = metrics
            exp.status = "completed"
        return exp

    def fail(self, exp_id: str, error: str) -> Experiment:
        exp = self._experiments.get(exp_id)
        if exp:
            exp.status = "failed"
            exp.notes = error
        return exp

    def get(self, exp_id: str) -> Experiment | None:
        return self._experiments.get(exp_id)

    def list_all(self) -> list[Experiment]:
        return list(self._experiments.values())

    def count(self) -> int:
        return len(self._experiments)
