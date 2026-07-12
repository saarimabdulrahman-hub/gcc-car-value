"""Prediction Lineage — complete traceability chain for every prediction."""

from ml.inference.models import PredictionLineage


class LineageTracker:
    """Tracks complete lineage: dataset → snapshot → model → experiment → deployment → prediction → feedback."""

    def __init__(self):
        self._lineages: dict[str, PredictionLineage] = {}

    def record(self, prediction_id: str, **kwargs) -> PredictionLineage:
        lineage = PredictionLineage(prediction_id=prediction_id, **kwargs)
        self._lineages[prediction_id] = lineage
        return lineage

    def get(self, prediction_id: str) -> PredictionLineage | None:
        return self._lineages.get(prediction_id)

    def update_feedback(self, prediction_id: str,
                        feedback_id: str) -> None:
        lineage = self._lineages.get(prediction_id)
        if lineage:
            lineage.feedback_id = feedback_id

    def count(self) -> int:
        return len(self._lineages)
