"""Retraining Coordinator — receives monitoring recommendations, triggers workflow."""

from ml.lifecycle.orchestrator import LifecycleOrchestrator
from ml.lifecycle.models import TriggerSource, WorkflowRecord


class RetrainingCoordinator:
    """Listens to monitoring recommendations and triggers workflows."""
    def __init__(self, orchestrator: LifecycleOrchestrator):
        self._orch = orchestrator

    def on_recommendation(self, model_name: str,
                          recommended: bool) -> WorkflowRecord | None:
        """Handle a monitoring recommendation."""
        if not recommended:
            return None
        return self._orch.start(model_name, trigger=TriggerSource.DRIFT_ALERT)
