"""Inference Pipeline — validate → snapshot → predict → audit → lineage."""

import hashlib, json, time, uuid
from ml.serving.server import ModelServer
from ml.inference.validator import RequestValidator
from ml.inference.models import FeatureSnapshot, AuditRecord
from ml.inference.audit import AuditStore
from ml.inference.feedback import FeedbackCollector
from ml.inference.lineage import LineageTracker
from ml.inference.config import InferenceConfig


class InferencePipeline:
    """Production online inference pipeline.

    Every prediction is:
        1. Validated
        2. Feature-snapshotted (immutable)
        3. Predicted via Model Server
        4. Audited (immutable record)
        5. Lineage-tracked
        6. Returned with full metadata

    Usage:
        pipeline = InferencePipeline(server)
        result = pipeline.predict("valuation", {"make":"Toyota","year":2018,"mileage_km":120000})
    """

    def __init__(self, server: ModelServer,
                 config: InferenceConfig | None = None):
        self._server = server
        self.config = config or InferenceConfig()
        self._validator = RequestValidator()
        self._audit = AuditStore()
        self._feedback = FeedbackCollector()
        self._lineage = LineageTracker()

    # ------------------------------------------------------------------
    # Predict
    # ------------------------------------------------------------------

    def predict(self, model_name: str, features: dict,
                request_key: str = "") -> dict:
        """Execute a full inference request with audit trail.

        Returns dict with prediction + complete metadata.
        """
        start = time.perf_counter()
        prediction_id = str(uuid.uuid4())

        # 1. Validate
        self._validator.validate_or_raise(features)

        # 2. Feature snapshot (immutable)
        snapshot = FeatureSnapshot.from_features(features)
        request_hash = hashlib.sha256(
            json.dumps(features, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

        # 3. Predict via Model Server
        result = self._server.predict(model_name, features, cache_key=request_key)

        # 4. Audit record (immutable)
        audit = AuditRecord(
            prediction_id=prediction_id,
            request_hash=request_hash,
            snapshot_id=snapshot.snapshot_id,
            prediction=result.prediction,
            confidence=result.confidence,
            model_version=result.model_version,
            model_name=result.model_name,
            experiment_id=result.experiment_id,
            latency_ms=(time.perf_counter() - start) * 1000,
            fallback_used=result.fallback_used,
            feature_schema_version=result.feature_schema_version,
        )
        self._audit.save(audit)

        # 5. Lineage
        self._lineage.record(prediction_id,
                            feature_snapshot_id=snapshot.snapshot_id,
                            model_version=result.model_version,
                            experiment_id=result.experiment_id)

        # 6. Return
        return {
            "prediction_id": prediction_id,
            "prediction": result.prediction,
            "confidence": result.confidence,
            "model_version": result.model_version,
            "model_name": result.model_name,
            "experiment_id": result.experiment_id,
            "dataset_version": audit.dataset_version,
            "feature_schema_version": audit.feature_schema_version,
            "latency_ms": audit.latency_ms,
            "fallback_used": audit.fallback_used,
            "timestamp": audit.timestamp,
        }

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    def attach_feedback(self, prediction_id: str,
                        actual_price: float | None = None,
                        operator_correction: float | None = None,
                        **kwargs) -> None:
        self._feedback.attach(prediction_id,
                            actual_selling_price=actual_price,
                            operator_correction=operator_correction,
                            **kwargs)
        self._lineage.update_feedback(prediction_id, prediction_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_audit(self, prediction_id: str) -> AuditRecord | None:
        return self._audit.get(prediction_id)

    def get_lineage(self, prediction_id: str) -> dict | None:
        lineage = self._lineage.get(prediction_id)
        return {
            "prediction_id": lineage.prediction_id,
            "dataset_version": lineage.dataset_version,
            "feature_snapshot_id": lineage.feature_snapshot_id,
            "model_version": lineage.model_version,
            "experiment_id": lineage.experiment_id,
            "deployment_id": lineage.deployment_id,
            "feedback_id": lineage.feedback_id,
        } if lineage else None

    @property
    def stats(self) -> dict:
        return {
            "total_predictions": self._audit.count(),
            "feedback_received": self._feedback.count(),
            "lineages_tracked": self._lineage.count(),
        }
