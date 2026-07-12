"""Test monitoring — data drift, model drift, alerts, PSI, retraining signals, reports."""
import pytest
from ml.monitoring.data_drift import DataDriftDetector
from ml.monitoring.model_drift import ModelDriftDetector
from ml.monitoring.alerts import AlertEngine, AlertLevel
from ml.monitoring.retraining import RetrainingSignals
from ml.monitoring.report import ReportGenerator
from ml.monitoring.monitor import MonitoringEngine
from ml.monitoring.performance_monitor import PerformanceMonitor
from ml.monitoring.models import DriftEvent, DriftType


class TestDataDrift:
    def test_psi_identical(self):
        detector = DataDriftDetector()
        vals = [1.0, 2.0, 3.0, 4.0, 5.0] * 10
        psi = detector.psi(vals, vals)
        assert abs(psi) < 0.01  # Identical distributions have near-zero PSI

    def test_psi_different(self):
        detector = DataDriftDetector()
        expected = [1.0, 2.0, 3.0] * 20
        actual = [10.0, 20.0, 30.0] * 20
        psi = detector.psi(expected, actual)
        assert psi > 0  # Different distributions have positive PSI

    def test_check_mean_shift(self):
        detector = DataDriftDetector()
        detector.set_baseline("price", [50000.0] * 100)
        events = detector.check("price", [75000.0] * 100)
        assert len(events) > 0  # Mean shifted by 50%

    def test_check_no_shift(self):
        detector = DataDriftDetector()
        detector.set_baseline("price", [50000.0] * 100)
        events = detector.check("price", [51000.0] * 100)
        assert len(events) == 0  # Tiny shift within threshold


class TestModelDrift:
    def test_mae_degradation(self):
        detector = ModelDriftDetector()
        detector.set_baseline_mae("valuation", 5000.0)
        for _ in range(200):
            detector.add_feedback("valuation", predicted=100000, actual=120000)  # Error = 20000
        events = detector.check("valuation")
        assert len(events) > 0


class TestAlertEngine:
    def test_generate_alerts(self):
        engine = AlertEngine()
        engine.warning("test", "test warning")
        engine.critical("critical", "test critical")
        assert len(engine.list_by_level(AlertLevel.WARNING)) == 1
        assert len(engine.list_by_level(AlertLevel.CRITICAL)) == 1

    def test_from_drift(self):
        engine = AlertEngine()
        event = DriftEvent(alert_level=AlertLevel.CRITICAL, details="test")
        alert = engine.from_drift(event)
        assert alert.level == AlertLevel.CRITICAL


class TestRetrainingSignals:
    def test_recommendation_with_drift(self):
        rs = RetrainingSignals()
        events = [DriftEvent(), DriftEvent(), DriftEvent()]  # 3 drift events
        result = rs.evaluate(events, {})
        assert result["recommended"]

    def test_no_recommendation_without_drift(self):
        rs = RetrainingSignals()
        result = rs.evaluate([], {})
        assert not result["recommended"]


class TestPerformanceMonitor:
    def test_stats(self):
        pm = PerformanceMonitor()
        pm.record("v1", 45.0); pm.record("v1", 55.0)
        stats = pm.stats("v1")
        assert stats["total_requests"] == 2
        assert stats["avg_latency_ms"] == 50.0


class TestMonitoringEngine:
    def test_full_run(self):
        engine = MonitoringEngine()
        engine.set_baseline("price", [50000] * 100)
        engine.set_baseline_mae("valuation", 5000)
        engine.set_baseline_mape("valuation", 4.5)

        # Record some observations
        for _ in range(200):
            engine.record_feature("price", 50000)
            engine.add_feedback("valuation", 100000, 101000)
            engine.record_performance("valuation", 45.0)

        report = engine.run("valuation")
        assert report.model_health_score >= 0
        assert report.total_predictions == 200
