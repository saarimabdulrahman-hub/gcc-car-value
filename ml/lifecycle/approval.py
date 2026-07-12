"""Approval Workflow — manual approve/reject with comments, approver tracking."""

import time
from ml.lifecycle.models import WorkflowRecord, WorkflowStage
from ml.lifecycle.errors import ApprovalError


class ApprovalWorkflow:
    def __init__(self): self._pending: dict[str, WorkflowRecord] = {}

    def request(self, wf: WorkflowRecord) -> None:
        self._pending[wf.workflow_id] = wf

    def approve(self, workflow_id: str, approver: str = "",
                comment: str = "") -> WorkflowRecord:
        wf = self._pending.get(workflow_id)
        if wf is None: raise ApprovalError(f"Workflow {workflow_id} not pending approval")
        wf.approver = approver; wf.approval_comment = comment
        wf.approval_at = time.time()
        del self._pending[workflow_id]
        return wf

    def reject(self, workflow_id: str, approver: str = "",
               reason: str = "") -> WorkflowRecord:
        wf = self._pending.get(workflow_id)
        if wf is None: raise ApprovalError(f"Workflow {workflow_id} not pending approval")
        wf.approver = approver; wf.approval_comment = reason
        wf.approval_at = time.time()
        del self._pending[workflow_id]
        return wf

    def is_pending(self, workflow_id: str) -> bool:
        return workflow_id in self._pending

    def list_pending(self) -> list[WorkflowRecord]:
        return list(self._pending.values())
