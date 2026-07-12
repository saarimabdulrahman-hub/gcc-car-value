"""Inference data models — audit records, feature snapshots, feedback."""

from dataclasses import dataclass, field
import time, uuid, hashlib, json


@dataclass(frozen=True)
class FeatureSnapshot:
    """Immutable snapshot of the feature vector used for a prediction."""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    features: str = ""                    # JSON-serialized feature dict (immutable)
    feature_checksum: str = ""            # SHA-256 of features
    feature_schema_version: int = 0
    created_at: float = field(default_factory=time.time)

    @classmethod
    def from_features(cls, features: dict, schema_version: int = 0) -> "FeatureSnapshot":
        features_json = json.dumps(features, sort_keys=True, default=str)
        checksum = hashlib.sha256(features_json.encode()).hexdigest()[:16]
        return cls(features=features_json, feature_checksum=checksum,
                   feature_schema_version=schema_version)


@dataclass(frozen=True)
class AuditRecord:
    """Immutable prediction audit record."""
    prediction_id: str
    request_hash: str = ""
    snapshot_id: str = ""
    prediction: float = 0.0
    confidence: float = 0.0
    model_version: str = ""
    model_name: str = ""
    experiment_id: str = ""
    deployment_id: str = ""
    dataset_version: str = ""
    feature_schema_version: int = 0
    latency_ms: float = 0.0
    fallback_used: bool = False
    canary_pct: float = 0.0
    ab_experiment_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class PredictionFeedback:
    """Optional feedback attached after prediction."""
    prediction_id: str = ""
    actual_selling_price: float | None = None
    operator_correction: float | None = None
    user_rating: int = 0           # 1-5
    confidence_override: float | None = None
    notes: str = ""
    status: str = "pending"        # pending | received | reviewed
    received_at: float = 0.0


@dataclass
class PredictionLineage:
    """Complete lineage chain for a prediction."""
    prediction_id: str = ""
    dataset_version: str = ""
    feature_snapshot_id: str = ""
    model_version: str = ""
    experiment_id: str = ""
    deployment_id: str = ""
    feedback_id: str = ""
