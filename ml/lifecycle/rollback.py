"""Rollback Workflow — triggers on canary failure, operator request, critical alert."""

from ml.lifecycle.orchestrator import LifecycleOrchestrator


class RollbackWorkflow:
    def __init__(self, orchestrator: LifecycleOrchestrator):
        self._orch = orchestrator

    def execute(self, workflow_id: str,
                reason: str = "operator_request") -> None:
        self._orch.rollback(workflow_id, reason=reason)
