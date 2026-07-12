"""Training data models."""

from dataclasses import dataclass, field
from enum import StrEnum
import time


class ModelStatus(StrEnum):
    TRAINING = "training"
    EVALUATING = "evaluating"
    REGISTERED = "registered"
    ACTIVE = "active"
    ARCHIVED = "archived"
    ROLLED_BACK = "rolled_back"


@dataclass
class Experiment:
    """A single training experiment."""
    experiment_id: str
    dataset_version: str = ""
    feature_schema_version: int = 0
    model_type: str = ""
    random_seed: int = 42
    started_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    duration_seconds: float = 0.0
    status: str = "running"         # running | completed | failed
    hyperparameters: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    notes: str = ""


@dataclass
class ModelEntry:
    """A model registered in the Model Registry."""
    model_id: str
    model_name: str = ""
    model_type: str = ""
    version: int = 1
    status: ModelStatus = ModelStatus.TRAINING
    experiment_id: str = ""
    metrics: dict = field(default_factory=dict)
    feature_importance: dict = field(default_factory=dict)
    feature_names: list[str] = field(default_factory=list)
    artifact_path: str = ""
    created_at: float = field(default_factory=time.time)
    promoted_at: float = 0.0
    rolled_back_at: float = 0.0
    rollback_reason: str = ""


@dataclass
class EvaluationResult:
    """Result of model evaluation."""
    mae: float = 0.0
    rmse: float = 0.0
    mape: float = 0.0           # percentage
    r2: float = 0.0
    median_absolute_error: float = 0.0
    training_rows: int = 0
    holdout_rows: int = 0
    residual_stats: dict = field(default_factory=dict)
