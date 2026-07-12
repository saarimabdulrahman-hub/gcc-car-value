"""Prediction Cache — TTL, thread-safe, invalidation, hit statistics."""

import threading, time
from ml.serving.models import PredictionResult


class PredictionCache:
    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 10000):
        self._ttl = ttl_seconds
        self._max = max_size
        self._store: dict[str, tuple[float, PredictionResult]] = {}
        self._lock = threading.Lock()
        self._hits = 0; self._misses = 0

    def get(self, key: str) -> PredictionResult | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None: self._misses += 1; return None
            ts, result = entry
            if time.monotonic() - ts > self._ttl:
                del self._store[key]; self._misses += 1; return None
            self._hits += 1; return result

    def set(self, key: str, result: PredictionResult) -> None:
        with self._lock:
            if len(self._store) >= self._max:
                # Evict oldest entry
                oldest = min(self._store.keys(), key=lambda k: self._store[k][0])
                del self._store[oldest]
            self._store[key] = (time.monotonic(), result)

    def invalidate(self, key: str = "") -> None:
        with self._lock:
            if key: self._store.pop(key, None)
            else: self._store.clear()

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / max(total, 1)

    def size(self) -> int:
        with self._lock: return len(self._store)
