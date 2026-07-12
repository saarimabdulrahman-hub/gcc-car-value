"""Lifecycle data models — workflow states, history records."""

from dataclasses import dataclass, field
from enum import StrEnum
import time, uuid


class WorkflowStage(StrEnum):
    QUEUED = "queued"
    DATASET_SELECTED = "dataset_selected"
    TRAINING = "training"
    EVALUATING = "evaluating"
    REGISTERED = "registered"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYING = "deploying"
    CANARY = "canary"
    ACTIVE = "active"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class TriggerSource(StrEnum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    DRIFT_ALERT = "drift_alert"
    MONITORING = "monitoring"


@dataclass
class WorkflowRecord:
    """A complete lifecycle workflow record."""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    trigger: TriggerSource = TriggerSource.MANUAL
    model_name: str = ""
    stage: WorkflowStage = WorkflowStage.QUEUED
    dataset_version: str = ""
    experiment_id: str = ""
    model_version: int = 0
    deployment_id: str = ""
    canary_pct: float = 0.0
    approver: str = ""
    approval_comment: str = ""
    approval_at: float = 0.0
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    error: str = ""
    rollback_reason: str = ""
    stages_history: list[dict] = field(default_factory=list)  # [{stage, at, duration_ms}]
