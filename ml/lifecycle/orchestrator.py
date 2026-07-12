"""Lifecycle Orchestrator — coordinates all ML systems into one workflow."""

import time
from ml.lifecycle.config import LifecycleConfig
from ml.lifecycle.workflow import WorkflowEngine
from ml.lifecycle.scheduler import RetrainingScheduler
from ml.lifecycle.approval import ApprovalWorkflow
from ml.lifecycle.models import WorkflowRecord, WorkflowStage, TriggerSource
from ml.lifecycle.history import LifecycleHistory
from ml.lifecycle.statistics import LifecycleStatistics


class LifecycleOrchestrator:
    """Coordinates the complete ML model lifecycle.

    This is the capstone module — it orchestrates all previously-built
    systems without duplicating their logic.

    Usage:
        orch = LifecycleOrchestrator()
        wf = orch.start("valuation", trigger=TriggerSource.DRIFT_ALERT)
        orch.approve(wf.workflow_id, approver="ml-engineer")
        orch.promote(wf.workflow_id)
        orch.complete(wf.workflow_id)
    """

    def __init__(self, config: LifecycleConfig | None = None):
        self.config = config or LifecycleConfig()
        self._workflow = WorkflowEngine()
        self._scheduler = RetrainingScheduler(self.config)
        self._approval = ApprovalWorkflow()
        self._history = LifecycleHistory()
        self._stats = LifecycleStatistics()

    # ------------------------------------------------------------------
    # Start workflow
    # ------------------------------------------------------------------

    def start(self, model_name: str,
              trigger: TriggerSource = TriggerSource.MANUAL) -> WorkflowRecord | None:
        """Start a new retraining/deployment workflow."""
        can_start, reason = self._scheduler.should_trigger(
            trigger, self.config.max_concurrent_workflows
        )
        if not can_start:
            return None  # Silently skip — scheduler says no

        self._scheduler.increment_active()

        wf = self._workflow.create(model_name, trigger=trigger.value)
        self._workflow.transition(wf.workflow_id, WorkflowStage.DATASET_SELECTED)
        self._history.record(wf)

        self._stats.record_workflow()
        return wf

    # ------------------------------------------------------------------
    # Training pipeline stages
    # ------------------------------------------------------------------

    def training_started(self, workflow_id: str) -> WorkflowRecord:
        return self._workflow.transition(workflow_id, WorkflowStage.TRAINING)

    def training_completed(self, workflow_id: str,
                           experiment_id: str = "",
                           model_version: int = 0) -> WorkflowRecord:
        wf = self._workflow.transition(workflow_id, WorkflowStage.EVALUATING)
        wf.experiment_id = experiment_id
        wf.model_version = model_version
        return self._workflow.transition(workflow_id, WorkflowStage.REGISTERED,
                                         experiment_id=experiment_id)

    # ------------------------------------------------------------------
    # Approval
    # ------------------------------------------------------------------

    def request_approval(self, workflow_id: str) -> WorkflowRecord:
        wf = self._workflow.transition(workflow_id, WorkflowStage.WAITING_APPROVAL)
        self._approval.request(wf)
        return wf

    def approve(self, workflow_id: str, approver: str = "",
                comment: str = "") -> WorkflowRecord:
        if not self._approval.is_pending(workflow_id):
            self.request_approval(workflow_id)
        self._approval.approve(workflow_id, approver, comment)
        return self._workflow.transition(workflow_id, WorkflowStage.APPROVED,
                                         approver=approver)

    def reject(self, workflow_id: str, approver: str = "",
               reason: str = "") -> WorkflowRecord:
        self._approval.reject(workflow_id, approver, reason)
        self._scheduler.decrement_active()
        return self._workflow.transition(workflow_id, WorkflowStage.REJECTED,
                                         reason=reason)

    # ------------------------------------------------------------------
    # Deployment & Canary
    # ------------------------------------------------------------------

    def deploy(self, workflow_id: str,
               deployment_id: str = "") -> WorkflowRecord:
        wf = self._workflow.transition(workflow_id, WorkflowStage.DEPLOYING)
        wf.deployment_id = deployment_id
        return wf

    def start_canary(self, workflow_id: str,
                     start_pct: float = 0.01) -> WorkflowRecord:
        wf = self._workflow.transition(workflow_id, WorkflowStage.CANARY,
                                       canary_pct=start_pct)
        wf.canary_pct = start_pct
        return wf

    def promote(self, workflow_id: str) -> WorkflowRecord:
        return self._workflow.transition(workflow_id, WorkflowStage.ACTIVE)

    # ------------------------------------------------------------------
    # Monitoring & Completion
    # ------------------------------------------------------------------

    def start_monitoring(self, workflow_id: str) -> WorkflowRecord:
        return self._workflow.transition(workflow_id, WorkflowStage.MONITORING)

    def complete(self, workflow_id: str) -> WorkflowRecord:
        self._scheduler.decrement_active()
        wf = self._workflow.transition(workflow_id, WorkflowStage.COMPLETED)
        self._stats.record_completion()
        return wf

    # ------------------------------------------------------------------
    # Rollback & Failure
    # ------------------------------------------------------------------

    def rollback(self, workflow_id: str,
                 reason: str = "") -> WorkflowRecord:
        self._scheduler.decrement_active()
        wf = self._workflow.transition(workflow_id, WorkflowStage.ROLLED_BACK,
                                       reason=reason)
        wf.rollback_reason = reason
        self._stats.record_rollback()
        return wf

    def fail(self, workflow_id: str, error: str = "") -> WorkflowRecord:
        self._scheduler.decrement_active()
        wf = self._workflow.transition(workflow_id, WorkflowStage.FAILED,
                                       error=error)
        wf.error = error
        self._stats.record_failure()
        return wf

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_workflow(self, workflow_id: str) -> WorkflowRecord | None:
        return self._workflow.get(workflow_id)

    def list_active(self) -> list[WorkflowRecord]:
        return self._workflow.list_active()

    def list_pending_approval(self) -> list[WorkflowRecord]:
        return self._approval.list_pending()

    @property
    def history(self) -> "LifecycleHistory": return self._history

    @property
    def stats(self) -> dict: return self._stats.snapshot()

    @property
    def scheduler(self) -> RetrainingScheduler: return self._scheduler
