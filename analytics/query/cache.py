"""Query cache — TTL, invalidation, thread-safe."""

import threading, time


class QueryCache:
    def __init__(self, ttl_seconds: float = 300.0):
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> object | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None: self._misses += 1; return None
            ts, val = entry
            if time.monotonic() - ts > self._ttl:
                del self._store[key]; self._misses += 1; return None
            self._hits += 1; return val

    def set(self, key: str, value: object) -> None:
        with self._lock:
            self._store[key] = (time.monotonic(), value)

    def invalidate(self, key: str = "") -> None:
        with self._lock:
            if key: self._store.pop(key, None)
            else: self._store.clear()

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
