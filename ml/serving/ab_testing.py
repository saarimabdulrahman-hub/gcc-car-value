"""A/B Testing — control/candidate, traffic split, winner promotion."""

import uuid, time
from ml.serving.models import ABExperiment, ABStatus


class ABTesting:
    def __init__(self):
        self._experiments: dict[str, ABExperiment] = {}

    def start(self, control: str, candidate: str,
              traffic_split: float = 0.5) -> ABExperiment:
        exp = ABExperiment(
            experiment_id=str(uuid.uuid4())[:12],
            control_model=control, candidate_model=candidate,
            traffic_split=traffic_split,
        )
        self._experiments[exp.experiment_id] = exp
        return exp

    def complete(self, experiment_id: str,
                 winner: str = "") -> ABExperiment:
        exp = self._experiments.get(experiment_id)
        if exp:
            exp.status = ABStatus.COMPLETED
            exp.results["winner"] = winner
        return exp

    def get(self, experiment_id: str) -> ABExperiment | None:
        return self._experiments.get(experiment_id)

    def get_active(self) -> list[ABExperiment]:
        return [e for e in self._experiments.values()
               if e.status == ABStatus.RUNNING]
