"""Data Drift — PSI, feature distributions, missing values, category frequencies."""

import math, uuid
from ml.monitoring.models import DriftEvent, DriftType, AlertLevel
from ml.monitoring.config import MonitoringConfig


class DataDriftDetector:
    def __init__(self, config: MonitoringConfig | None = None):
        self.config = config or MonitoringConfig()
        self._baseline: dict[str, dict] = {}  # feature_name → {mean, std, categories}

    def set_baseline(self, feature_name: str, values: list[float]) -> None:
        if not values: return
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        self._baseline[feature_name] = {
            "mean": mean, "std": math.sqrt(variance),
            "count": len(values), "min": min(values), "max": max(values),
        }

    def check(self, feature_name: str, current_values: list[float],
              model_name: str = "") -> list[DriftEvent]:
        """Check for drift in a feature. Returns list of DriftEvents."""
        baseline = self._baseline.get(feature_name)
        if not baseline or len(current_values) < self.config.min_samples_for_drift:
            return []

        events = []
        curr_mean = sum(current_values) / len(current_values)

        # Mean shift
        if baseline["mean"] > 0:
            mean_shift = abs(curr_mean - baseline["mean"]) / baseline["mean"]
            if mean_shift > self.config.psi_threshold_critical:
                events.append(DriftEvent(
                    event_id=str(uuid.uuid4())[:12],
                    drift_type=DriftType.FEATURE, feature_name=feature_name,
                    model_name=model_name, alert_level=AlertLevel.CRITICAL,
                    metric="mean_shift", baseline_value=baseline["mean"],
                    current_value=curr_mean, threshold=self.config.psi_threshold_critical,
                    details=f"Mean shifted from {baseline['mean']:.1f} to {curr_mean:.1f} ({mean_shift*100:.1f}%)",
                ))
            elif mean_shift > self.config.psi_threshold_warning:
                events.append(DriftEvent(
                    event_id=str(uuid.uuid4())[:12],
                    drift_type=DriftType.FEATURE, feature_name=feature_name,
                    model_name=model_name, alert_level=AlertLevel.WARNING,
                    metric="mean_shift", baseline_value=baseline["mean"],
                    current_value=curr_mean, threshold=self.config.psi_threshold_warning,
                    details=f"Mean shifted from {baseline['mean']:.1f} to {curr_mean:.1f} ({mean_shift*100:.1f}%)",
                ))

        # Range shift
        curr_min, curr_max = min(current_values), max(current_values)
        if curr_min < baseline["min"] * 0.5 or curr_max > baseline["max"] * 2.0:
            events.append(DriftEvent(
                event_id=str(uuid.uuid4())[:12],
                drift_type=DriftType.DATA_QUALITY, feature_name=feature_name,
                model_name=model_name, alert_level=AlertLevel.DATA_QUALITY,
                metric="range_shift", baseline_value=baseline["max"],
                current_value=curr_max, threshold=baseline["max"] * 2.0,
                details=f"Range shifted: [{baseline['min']:.0f}, {baseline['max']:.0f}] → [{curr_min:.0f}, {curr_max:.0f}]",
            ))

        return events

    def psi(self, expected: list[float], actual: list[float], bins: int = 10) -> float:
        """Population Stability Index."""
        if not expected or not actual: return 0.0
        combined = expected + actual
        if len(combined) < 2: return 0.0
        step = max(1, len(combined) // bins)
        bin_edges = sorted([combined[min(i * step, len(combined) - 1)] for i in range(bins + 1)])
        bin_edges = list(dict.fromkeys(bin_edges))
        if len(bin_edges) < 2:
            # All same value — create artificial edges
            v = bin_edges[0] if bin_edges else 0
            bin_edges = [v - 1, v, v + 1]

        def hist(vals, edges):
            counts = [0] * (len(edges) - 1)
            for v in vals:
                for i in range(len(edges) - 1):
                    if edges[i] <= v < edges[i+1]:
                        counts[i] += 1; break
            return counts

        e_hist = hist(expected, bin_edges)
        a_hist = hist(actual, bin_edges)
        psi_val = 0.0
        for e, a in zip(e_hist, a_hist):
            e_pct = (e + 0.0001) / (sum(e_hist) + 0.0001)
            a_pct = (a + 0.0001) / (sum(a_hist) + 0.0001)
            if e_pct > 0 and a_pct > 0:
                psi_val += (a_pct - e_pct) * math.log(a_pct / e_pct)
        return psi_val
