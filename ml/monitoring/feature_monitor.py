"""Feature Monitor — track price, mileage, age, country, marketplace distributions."""

from collections import Counter
from ml.monitoring.data_drift import DataDriftDetector


class FeatureMonitor:
    def __init__(self, drift_detector: DataDriftDetector):
        self._drift = drift_detector
        self._history: dict[str, list[float]] = {}  # feature_name → values

    def record(self, feature_name: str, value: float) -> None:
        self._history.setdefault(feature_name, []).append(value)

    def set_baselines(self) -> None:
        for name, values in self._history.items():
            self._drift.set_baseline(name, values)

    def check_all(self, model_name: str = "") -> list:
        events = []
        for name, values in self._history.items():
            events.extend(self._drift.check(name, values[-1000:], model_name))
        return events

    def distribution(self, feature_name: str, top_n: int = 10) -> dict:
        """Return value distribution for a feature."""
        vals = self._history.get(feature_name, [])
        return dict(Counter(str(v) for v in vals).most_common(top_n))
