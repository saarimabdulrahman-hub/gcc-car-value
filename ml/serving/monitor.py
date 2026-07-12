"""Production Monitor — prediction count, latency, model usage, errors, cache."""

import threading

class ServingMonitor:
    def __init__(self):
        self._counts: dict[str, int] = {}      # model_name → predictions
        self._errors: dict[str, int] = {}
        self._latency_sum: dict[str, float] = {}
        self._lock = threading.Lock()

    def record_prediction(self, model_name: str, latency_ms: float) -> None:
        with self._lock:
            self._counts[model_name] = self._counts.get(model_name, 0) + 1
            self._latency_sum[model_name] = self._latency_sum.get(model_name, 0.0) + latency_ms

    def record_error(self, model_name: str) -> None:
        with self._lock:
            self._errors[model_name] = self._errors.get(model_name, 0) + 1

    def avg_latency(self, model_name: str) -> float:
        count = self._counts.get(model_name, 0)
        if count == 0: return 0.0
        return self._latency_sum.get(model_name, 0.0) / count

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "predictions": dict(self._counts),
                "errors": dict(self._errors),
                "avg_latency_ms": {k: self.avg_latency(k) for k in self._counts},
                "total_predictions": sum(self._counts.values()),
            }
