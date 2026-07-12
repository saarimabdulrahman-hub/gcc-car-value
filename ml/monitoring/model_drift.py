"""Model Drift — MAE/MAPE over time, error drift, rolling windows (feedback-driven)."""

import uuid, math
from ml.monitoring.models import DriftEvent, DriftType, AlertLevel
from ml.monitoring.config import MonitoringConfig


class ModelDriftDetector:
    def __init__(self, config: MonitoringConfig | None = None):
        self.config = config or MonitoringConfig()
        self._baseline_mae: dict[str, float] = {}   # model_name → baseline MAE
        self._feedback: dict[str, list[tuple[float, float]]] = {}  # model_name → [(predicted, actual)]

    def set_baseline_mae(self, model_name: str, mae: float) -> None:
        self._baseline_mae[model_name] = mae

    def add_feedback(self, model_name: str, predicted: float, actual: float) -> None:
        self._feedback.setdefault(model_name, []).append((predicted, actual))

    def check(self, model_name: str) -> list[DriftEvent]:
        """Check for model drift based on feedback. Returns list of DriftEvents."""
        feedback = self._feedback.get(model_name, [])
        if len(feedback) < self.config.min_samples_for_drift:
            return []

        baseline_mae = self._baseline_mae.get(model_name)
        if baseline_mae is None: return []

        # Current MAE
        errors = [abs(p - a) for p, a in feedback]
        current_mae = sum(errors) / len(errors)
        current_mape = sum(e / max(a, 1) * 100 for (p, a), e in zip(feedback, errors)) / len(feedback)

        events = []

        # MAE degradation
        if baseline_mae > 0:
            degradation = (current_mae - baseline_mae) / baseline_mae
            if degradation > self.config.mae_degradation_threshold:
                events.append(DriftEvent(
                    event_id=str(uuid.uuid4())[:12],
                    drift_type=DriftType.MODEL, model_name=model_name,
                    alert_level=AlertLevel.MODEL_DEGRADED,
                    metric="mae_degradation",
                    baseline_value=baseline_mae, current_value=current_mae,
                    threshold=self.config.mae_degradation_threshold,
                    details=f"MAE degraded {degradation*100:.1f}%: {baseline_mae:.0f} → {current_mae:.0f}",
                ))

        # MAPE degradation
        if self._baseline_mape.get(model_name, 0) > 0:
            baseline_mape = self._baseline_mape.get(model_name, 0)
            mape_degradation = (current_mape - baseline_mape) / baseline_mape
            if mape_degradation > self.config.mape_degradation_threshold:
                events.append(DriftEvent(
                    event_id=str(uuid.uuid4())[:12],
                    drift_type=DriftType.MODEL, model_name=model_name,
                    alert_level=AlertLevel.WARNING,
                    metric="mape_degradation",
                    baseline_value=baseline_mape, current_value=current_mape,
                    threshold=self.config.mape_degradation_threshold,
                    details=f"MAPE degraded {mape_degradation*100:.1f}%",
                ))

        return events

    _baseline_mape: dict[str, float] = {}
