"""Promotion Workflow — coordinates Registry → Deployment → Serving → Canary → Monitoring."""

from ml.lifecycle.orchestrator import LifecycleOrchestrator
from ml.lifecycle.models import WorkflowRecord


class PromotionWorkflow:
    """Coordinates promotion through the deployment pipeline."""
    def __init__(self, orchestrator: LifecycleOrchestrator):
        self._orch = orchestrator

    def execute(self, workflow_id: str,
                deployment_id: str = "",
                canary_pct: float = 0.0) -> WorkflowRecord:
        """Execute the full promotion pipeline."""
        self._orch.deploy(workflow_id, deployment_id=deployment_id)

        if canary_pct > 0:
            self._orch.start_canary(workflow_id, start_pct=canary_pct)
            # In production: wait for canary stable period,
            # check monitoring, then promote
        else:
            self._orch.promote(workflow_id)

        self._orch.start_monitoring(workflow_id)
        self._orch.complete(workflow_id)

        return self._orch.get_workflow(workflow_id)
