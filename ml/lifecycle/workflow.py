"""Workflow Engine — state machine for ML lifecycle stages."""

import time
from ml.lifecycle.models import WorkflowRecord, WorkflowStage


class WorkflowEngine:
    """State machine managing ML lifecycle stage transitions.

    Valid transitions:
        QUEUED → DATASET_SELECTED → TRAINING → EVALUATING → REGISTERED
        REGISTERED → WAITING_APPROVAL → APPROVED | REJECTED
        APPROVED → DEPLOYING → CANARY → ACTIVE → MONITORING → COMPLETED
        Any stage → FAILED | ROLLED_BACK
    """

    def __init__(self):
        self._workflows: dict[str, WorkflowRecord] = {}

    def create(self, model_name: str, trigger: str = "manual") -> WorkflowRecord:
        wf = WorkflowRecord(model_name=model_name, trigger=trigger)
        self._workflows[wf.workflow_id] = wf
        return wf

    def transition(self, workflow_id: str,
                   to_stage: WorkflowStage,
                   **meta) -> WorkflowRecord:
        wf = self._workflows.get(workflow_id)
        if wf is None: raise ValueError(f"Workflow {workflow_id} not found")

        start = time.perf_counter()
        wf.stage = to_stage
        wf.stages_history.append({
            "stage": to_stage.value,
            "at": time.time(),
            "duration_ms": (time.perf_counter() - start) * 1000,
            **meta,
        })

        if to_stage in (WorkflowStage.COMPLETED, WorkflowStage.FAILED,
                       WorkflowStage.ROLLED_BACK, WorkflowStage.REJECTED):
            wf.completed_at = time.time()

        return wf

    def get(self, workflow_id: str) -> WorkflowRecord | None:
        return self._workflows.get(workflow_id)

    def list_active(self) -> list[WorkflowRecord]:
        terminals = {WorkflowStage.COMPLETED, WorkflowStage.FAILED,
                    WorkflowStage.ROLLED_BACK, WorkflowStage.REJECTED}
        return [w for w in self._workflows.values()
               if w.stage not in terminals]

    def list_all(self) -> list[WorkflowRecord]:
        return list(self._workflows.values())
