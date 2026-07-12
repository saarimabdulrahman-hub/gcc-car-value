"""Monitoring Engine — orchestrates all drift detectors, alerts, and reports."""

import time, uuid
from ml.monitoring.config import MonitoringConfig
from ml.monitoring.data_drift import DataDriftDetector
from ml.monitoring.model_drift import ModelDriftDetector
from ml.monitoring.feature_monitor import FeatureMonitor
from ml.monitoring.performance_monitor import PerformanceMonitor
from ml.monitoring.alerts import AlertEngine
from ml.monitoring.retraining import RetrainingSignals
from ml.monitoring.report import ReportGenerator
from ml.monitoring.models import MonitoringReport


class MonitoringEngine:
    """Continuous ML monitoring — drift detection, performance, alerts, retraining signals.

    Usage:
        engine = MonitoringEngine()
        engine.set_baseline("price", [75000, 80000, 72000, ...])
        engine.set_baseline_mae("valuation", 4500.0)
        engine.add_feedback("valuation", predicted=120000, actual=118000)

        report = engine.run("valuation")
        if report.retraining_recommended:
            print("Retrain your model!")
    """

    def __init__(self, config: MonitoringConfig | None = None):
        self.config = config or MonitoringConfig()
        self._data_drift = DataDriftDetector(self.config)
        self._model_drift = ModelDriftDetector(self.config)
        self._feature_monitor = FeatureMonitor(self._data_drift)
        self._performance = PerformanceMonitor()
        self._alerts = AlertEngine()
        self._retraining = RetrainingSignals(self.config)
        self._reports = ReportGenerator()

    # ------------------------------------------------------------------
    # Baseline setup
    # ------------------------------------------------------------------

    def set_baseline(self, feature_name: str, values: list[float]) -> None:
        self._data_drift.set_baseline(feature_name, values)

    def set_baseline_mae(self, model_name: str, mae: float) -> None:
        self._model_drift.set_baseline_mae(model_name, mae)

    def set_baseline_mape(self, model_name: str, mape: float) -> None:
        self._model_drift._baseline_mape[model_name] = mape

    # ------------------------------------------------------------------
    # Record observations
    # ------------------------------------------------------------------

    def record_feature(self, feature_name: str, value: float) -> None:
        self._feature_monitor.record(feature_name, value)

    def add_feedback(self, model_name: str,
                     predicted: float, actual: float) -> None:
        """Record actual-vs-predicted for model drift detection."""
        self._model_drift.add_feedback(model_name, predicted, actual)

    def record_performance(self, model_name: str, latency_ms: float,
                           success: bool = True, fallback: bool = False) -> None:
        self._performance.record(model_name, latency_ms, success, fallback)

    # ------------------------------------------------------------------
    # Monitoring run
    # ------------------------------------------------------------------

    def run(self, model_name: str = "valuation") -> MonitoringReport:
        """Execute a full monitoring run. Returns a report."""
        all_events = []

        # 1. Feature drift
        feature_events = self._feature_monitor.check_all(model_name)
        all_events.extend(feature_events)

        # 2. Model drift
        model_events = self._model_drift.check(model_name)
        all_events.extend(model_events)

        # 3. Generate alerts
        alerts = []
        for event in all_events:
            alerts.append(self._alerts.from_drift(event))

        # 4. Performance stats
        perf_stats = self._performance.stats(model_name)

        # 5. Retraining recommendation
        retraining = self._retraining.evaluate(all_events, {
            "mae_degradation": 0.5 if any(e.metric == "mae_degradation" for e in all_events) else 0.0,
        })

        # 6. Build report
        model_health = max(0.0, 100.0 - len(all_events) * 10.0 - (
            30 if retraining["recommended"] else 0
        ))

        report = self._reports.generate(
            report_type="daily",
            total_predictions=perf_stats.get("total_requests", 0),
            alerts=alerts,
            drift_events=all_events,
            retraining_recommended=retraining["recommended"],
            retraining_reason="; ".join(retraining["reasons"]),
            model_health_score=model_health,
        )

        return report

    @property
    def performance(self) -> PerformanceMonitor: return self._performance
    @property
    def alerts(self) -> AlertEngine: return self._alerts
    @property
    def reports(self) -> ReportGenerator: return self._reports
