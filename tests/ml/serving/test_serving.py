"""Test model serving — router, cache, deployment, A/B testing, canary, monitor."""
import pytest
from ml.serving.router import TrafficRouter
from ml.serving.cache import PredictionCache
from ml.serving.deployment import DeploymentManager
from ml.serving.ab_testing import ABTesting
from ml.serving.canary import CanaryController
from ml.serving.monitor import ServingMonitor
from ml.serving.models import PredictionResult, ABExperiment, DeploymentStatus
from ml.training.registry import ModelRegistry


class TestRouter:
    def test_active_routing(self):
        router = TrafficRouter()
        router.set_active("valuation", "valuation:v1")
        assert router.route("valuation") == "valuation:v1"

    def test_deterministic_routing(self):
        router = TrafficRouter()
        router.set_active("test", "test:v1")
        r1 = router.route("test", request_key="user-abc")
        r2 = router.route("test", request_key="user-abc")
        assert r1 == r2  # Same key → same route

    def test_ab_routing(self):
        router = TrafficRouter()
        router.set_active("test", "test:v1")
        ab = ABExperiment(
            experiment_id="ab-1", control_model="test:v1",
            candidate_model="test:v2", traffic_split=1.0,  # 100% to candidate
        )
        assert router.route("test", request_key="key1", ab_experiment=ab) == "test:v2"


class TestPredictionCache:
    def test_set_and_get(self):
        cache = PredictionCache(ttl_seconds=60)
        result = PredictionResult(prediction=125000.0, model_name="v1")
        cache.set("key1", result)
        cached = cache.get("key1")
        assert cached.prediction == 125000.0

    def test_miss(self):
        cache = PredictionCache()
        assert cache.get("nonexistent") is None

    def test_hit_rate(self):
        cache = PredictionCache(ttl_seconds=60)
        cache.get("k")  # miss
        cache.set("k", PredictionResult())
        cache.get("k")  # hit
        assert cache.hit_rate == 0.5


class TestDeploymentManager:
    def test_deploy_and_activate(self):
        mgr = DeploymentManager()
        dep_id = mgr.deploy("lightgbm", version=2)
        mgr.activate("lightgbm", dep_id)
        records = mgr.get_history("lightgbm")
        assert records[0].status == DeploymentStatus.ACTIVE
        assert records[0].traffic_pct == 100.0

    def test_rollback(self):
        mgr = DeploymentManager()
        d1 = mgr.deploy("lightgbm", version=1)
        mgr.activate("lightgbm", d1)
        d2 = mgr.deploy("lightgbm", version=2)
        mgr.activate("lightgbm", d2)
        mgr.rollback("lightgbm", "worse performance")
        records = mgr.get_history("lightgbm")
        assert records[1].status == DeploymentStatus.ROLLED_BACK  # v2 rolled back
        assert records[0].status == DeploymentStatus.ACTIVE  # v1 re-activated


class TestABTesting:
    def test_start_and_complete(self):
        ab = ABTesting()
        exp = ab.start("model:v1", "model:v2", traffic_split=0.3)
        assert exp.traffic_split == 0.3
        assert len(ab.get_active()) == 1

        ab.complete(exp.experiment_id, winner="model:v2")
        assert ab.get(exp.experiment_id).status == "completed"


class TestCanary:
    def test_canary_progression(self):
        cc = CanaryController()
        pct = cc.start("lightgbm", start_pct=0.01)
        assert pct == 0.01

        pct = cc.increase("lightgbm", increment=0.05)
        assert abs(pct - 0.06) < 0.001

    def test_auto_rollback_check(self):
        cc = CanaryController()
        assert cc.should_rollback("model", error_rate=0.10, threshold=0.05)


class TestMonitor:
    def test_record_and_snapshot(self):
        mon = ServingMonitor()
        mon.record_prediction("v1", 45.0)
        mon.record_prediction("v1", 55.0)
        snap = mon.snapshot()
        assert snap["predictions"]["v1"] == 2
        assert snap["avg_latency_ms"]["v1"] == 50.0
        assert snap["total_predictions"] == 2
