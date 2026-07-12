"""Performance Monitor — latency, failures, fallback rate, cache usage, throughput."""

import threading

class PerformanceMonitor:
    def __init__(self):
        self._latencies: dict[str, list[float]] = {}
        self._failures: dict[str, int] = {}
        self._fallbacks: dict[str, int] = {}
        self._total: dict[str, int] = {}
        self._lock = threading.Lock()

    def record(self, model_name: str, latency_ms: float,
               success: bool = True, fallback: bool = False) -> None:
        with self._lock:
            self._total[model_name] = self._total.get(model_name, 0) + 1
            self._latencies.setdefault(model_name, []).append(latency_ms)
            if not success: self._failures[model_name] = self._failures.get(model_name, 0) + 1
            if fallback: self._fallbacks[model_name] = self._fallbacks.get(model_name, 0) + 1

    def stats(self, model_name: str = "") -> dict:
        with self._lock:
            total = self._total.get(model_name, 0)
            if total == 0: return {"total_requests": 0}
            lats = self._latencies.get(model_name, [])
            return {
                "total_requests": total,
                "avg_latency_ms": round(sum(lats) / len(lats), 2) if lats else 0,
                "p95_latency_ms": round(sorted(lats)[int(len(lats)*0.95)], 2) if lats else 0,
                "failure_rate": round(self._failures.get(model_name, 0) / total * 100, 2),
                "fallback_rate": round(self._fallbacks.get(model_name, 0) / total * 100, 2),
            }
