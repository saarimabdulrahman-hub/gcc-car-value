"""Retraining Signals — generate recommendations based on drift and performance."""

import time
from ml.monitoring.config import MonitoringConfig


class RetrainingSignals:
    def __init__(self, config: MonitoringConfig | None = None):
        self.config = config or MonitoringConfig()
        self._last_recommendation: float = 0.0

    def evaluate(self, drift_events: list,
                 model_performance: dict) -> dict:
        """Generate a retraining recommendation."""
        now = time.time()
        if self._last_recommendation > 0:
            elapsed_days = (now - self._last_recommendation) / 86400
            if elapsed_days < self.config.retraining_min_interval_days:
                return {"recommended": False, "reason": "Too soon since last recommendation"}

        reasons = []
        if len(drift_events) >= 3:
            reasons.append(f"{len(drift_events)} drift events detected")
        if model_performance.get("mae_degradation", 0) > self.config.mae_degradation_threshold:
            reasons.append("Model performance degraded beyond threshold")

        recommended = len(reasons) > 0
        if recommended:
            self._last_recommendation = now

        return {
            "recommended": recommended,
            "reasons": reasons if recommended else ["No issues detected"],
            "drift_event_count": len(drift_events),
        }
