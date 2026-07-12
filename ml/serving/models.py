"""Serving data models."""

from dataclasses import dataclass, field
from enum import StrEnum
import time


class DeploymentStatus(StrEnum):
    DEPLOYED = "deployed"
    ACTIVE = "active"
    CANARY = "canary"
    SHADOW = "shadow"
    ROLLED_BACK = "rolled_back"
    ARCHIVED = "archived"


class ABStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"


@dataclass
class PredictionResult:
    """Result of a single prediction."""
    prediction: float = 0.0
    model_version: str = ""
    model_name: str = ""
    experiment_id: str = ""
    latency_ms: float = 0.0
    confidence: float = 0.0
    fallback_used: bool = False
    feature_schema_version: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class DeploymentRecord:
    """A deployment event."""
    deployment_id: str = ""
    model_name: str = ""
    version: int = 0
    status: DeploymentStatus = DeploymentStatus.DEPLOYED
    traffic_pct: float = 0.0
    deployed_at: float = field(default_factory=time.time)
    activated_at: float = 0.0
    rolled_back_at: float = 0.0
    rollback_reason: str = ""


@dataclass
class ABExperiment:
    """An A/B testing experiment."""
    experiment_id: str = ""
    control_model: str = ""        # Currently active model
    candidate_model: str = ""      # New model being tested
    traffic_split: float = 0.5     # Fraction going to candidate
    status: ABStatus = ABStatus.RUNNING
    started_at: float = field(default_factory=time.time)
    results: dict = field(default_factory=dict)
