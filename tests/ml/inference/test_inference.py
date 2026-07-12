"""Test inference pipeline — validation, snapshot, audit, lineage, feedback."""
import pytest
from ml.inference.validator import RequestValidator
from ml.inference.models import FeatureSnapshot, AuditRecord
from ml.inference.audit import AuditStore
from ml.inference.feedback import FeedbackCollector
from ml.inference.lineage import LineageTracker
from ml.inference.errors import ValidationError


class TestValidator:
    def test_valid_passes(self):
        v = RequestValidator()
        errors = v.validate({"make": "Toyota", "model": "Camry", "year": 2020})
        assert len(errors) == 0

    def test_missing_required(self):
        v = RequestValidator()
        errors = v.validate({"make": "Toyota"})  # missing model, year
        assert len(errors) > 0

    def test_range_violation(self):
        v = RequestValidator()
        errors = v.validate({"make": "Toyota", "model": "Camry", "year": 3000})
        assert any("year" in e for e in errors)

    def test_validate_or_raise(self):
        v = RequestValidator()
        with pytest.raises(ValidationError):
            v.validate_or_raise({"make": ""})


class TestFeatureSnapshot:
    def test_snapshot_is_immutable(self):
        snap = FeatureSnapshot.from_features({"make": "Toyota", "year": 2020})
        with pytest.raises(Exception):
            snap.snapshot_id = "new-id"  # Frozen dataclass

    def test_checksum_stable(self):
        s1 = FeatureSnapshot.from_features({"make": "Toyota", "year": 2020})
        s2 = FeatureSnapshot.from_features({"make": "Toyota", "year": 2020})
        assert s1.feature_checksum == s2.feature_checksum

    def test_different_features_different_checksum(self):
        s1 = FeatureSnapshot.from_features({"make": "Toyota"})
        s2 = FeatureSnapshot.from_features({"make": "Nissan"})
        assert s1.feature_checksum != s2.feature_checksum


class TestAuditStore:
    def test_save_and_get(self):
        store = AuditStore()
        record = AuditRecord(prediction_id="p-1", prediction=125000.0, model_name="v1")
        store.save(record)
        assert store.get("p-1").prediction == 125000.0

    def test_list_by_model(self):
        store = AuditStore()
        store.save(AuditRecord(prediction_id="p-1", model_name="v1"))
        store.save(AuditRecord(prediction_id="p-2", model_name="v2"))
        store.save(AuditRecord(prediction_id="p-3", model_name="v1"))
        assert len(store.list_by_model("v1")) == 2


class TestFeedback:
    def test_attach_feedback(self):
        fc = FeedbackCollector()
        fc.attach("p-1", actual_selling_price=120000.0)
        fb = fc.get("p-1")
        assert fb.actual_selling_price == 120000.0
        assert fb.status == "received"


class TestLineage:
    def test_record_and_get(self):
        lt = LineageTracker()
        lt.record("p-1", dataset_version="v3", feature_snapshot_id="snap-1",
                 model_version="lightgbm:v2", experiment_id="exp-1")
        lineage = lt.get("p-1")
        assert lineage.model_version == "lightgbm:v2"
        assert lineage.experiment_id == "exp-1"

    def test_update_feedback(self):
        lt = LineageTracker()
        lt.record("p-1")
        lt.update_feedback("p-1", "fb-1")
        assert lt.get("p-1").feedback_id == "fb-1"
