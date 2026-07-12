"""Lifecycle History — persist workflow records for audit trail."""

from ml.lifecycle.models import WorkflowRecord


class LifecycleHistory:
    def __init__(self): self._records: dict[str, WorkflowRecord] = {}

    def record(self, wf: WorkflowRecord) -> None:
        self._records[wf.workflow_id] = wf

    def get(self, workflow_id: str) -> WorkflowRecord | None:
        return self._records.get(workflow_id)

    def list_by_model(self, model_name: str) -> list[WorkflowRecord]:
        return [r for r in self._records.values() if r.model_name == model_name]

    def list_all(self) -> list[WorkflowRecord]:
        return list(self._records.values())

    def count(self) -> int: return len(self._records)
