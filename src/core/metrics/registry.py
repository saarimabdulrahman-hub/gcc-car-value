"""MetricsRegistry — thread-safe singleton for all platform metrics.

The registry is the central coordination point. All metric registration
and lookup flows through it. Application code uses the global Metrics
singleton (imported from src.core.metrics).

Thread safety: all registration and mutation operations use a reentrant lock.
"""

from __future__ import annotations

import threading
from typing import Any, Callable

from src.core.metrics.types import (
    Metric, Counter, Gauge, Histogram, Timer, Info,
    MetricType, MetricValue,
)


class DuplicateMetricError(ValueError):
    """Raised when registering a metric with an already-registered name."""


class MetricNotFoundError(KeyError):
    """Raised when accessing a metric that hasn't been registered."""


class MetricsRegistry:
    """Thread-safe registry for all application metrics.

    Singleton pattern — use `from src.core.metrics import Metrics` to
    access the global instance.

    Usage:
        registry = MetricsRegistry()

        # Register
        registry.counter("api.requests", "Total API requests")
        registry.gauge("db.pool.size", "Connection pool size")
        registry.histogram("api.latency_ms", "API latency",
                          buckets=[10, 50, 100, 250, 500])

        # Mutate
        registry.increment("api.requests", tags={"status": "200"})
        registry.set_gauge("db.pool.size", 10.0)

        # Collect (for exporters)
        for metric in registry.collect_all():
            for value in metric.collect():
                print(metric.full_name, value.value, value.tags)
    """

    def __init__(self):
        self._metrics: dict[str, Metric] = {}
        self._lock = threading.RLock()
        self._exporters: list[Any] = []  # MetricExporter instances

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def counter(self, name: str, description: str = "",
                namespace: str = "",
                tags: dict[str, str] | None = None) -> Counter:
        """Register and return a Counter metric.

        Raises DuplicateMetricError if name is already registered.
        """
        return self._register(
            Counter(name, description, namespace, tags)
        )

    def gauge(self, name: str, description: str = "",
              namespace: str = "",
              tags: dict[str, str] | None = None) -> Gauge:
        """Register and return a Gauge metric."""
        return self._register(
            Gauge(name, description, namespace, tags)
        )

    def histogram(self, name: str, description: str = "",
                  buckets: list[float] | None = None,
                  namespace: str = "",
                  tags: dict[str, str] | None = None) -> Histogram:
        """Register and return a Histogram metric."""
        return self._register(
            Histogram(name, description, buckets, namespace, tags)
        )

    def info(self, name: str, description: str = "",
             namespace: str = "",
             tags: dict[str, str] | None = None) -> Info:
        """Register and return an Info metric (static metadata)."""
        return self._register(
            Info(name, description, namespace, tags)
        )

    def _register(self, metric: Metric) -> Metric:
        """Register a metric. Thread-safe, prevents duplicates."""
        key = metric.full_name
        with self._lock:
            if key in self._metrics:
                raise DuplicateMetricError(
                    f"Metric '{key}' is already registered. "
                    f"Use get('{key}') to retrieve an existing metric."
                )
            self._metrics[key] = metric
        return metric

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> Metric:
        """Retrieve a registered metric by full name.

        Raises MetricNotFoundError if not found.
        """
        with self._lock:
            if name not in self._metrics:
                raise MetricNotFoundError(
                    f"Metric '{name}' not found. Register it first with "
                    f"Metrics.counter/gauge/histogram('{name}', ...)."
                )
            return self._metrics[name]

    def get_or_register(self, name: str, factory: Callable[[], Metric]) -> Metric:
        """Get an existing metric or register a new one.

        Safe to call concurrently — only one instance is created.
        """
        with self._lock:
            if name in self._metrics:
                return self._metrics[name]
            metric = factory()
            self._metrics[name] = metric
            return metric

    def list_names(self, namespace: str | None = None) -> list[str]:
        """List all registered metric names, optionally filtered by namespace."""
        with self._lock:
            names = list(self._metrics.keys())
        if namespace:
            prefix = f"{namespace}."
            names = [n for n in names if n.startswith(prefix)]
        return sorted(names)

    # ------------------------------------------------------------------
    # Mutation (convenience methods — look up metric, then mutate)
    # ------------------------------------------------------------------

    def increment(self, name: str, amount: float = 1.0,
                  tags: dict[str, str] | None = None) -> None:
        """Increment a counter by amount."""
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.inc(amount, tags)
        elif isinstance(metric, Gauge):
            metric.inc(amount)
        else:
            raise TypeError(
                f"Metric '{name}' is a {type(metric).__name__}, "
                f"not a Counter or Gauge."
            )

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge to an absolute value."""
        metric = self.get(name)
        if isinstance(metric, Gauge):
            metric.set(value)
        else:
            raise TypeError(
                f"Metric '{name}' is a {type(metric).__name__}, not a Gauge."
            )

    def decrement(self, name: str, amount: float = 1.0) -> None:
        """Decrement a gauge by amount."""
        metric = self.get(name)
        if isinstance(metric, Gauge):
            metric.dec(amount)
        else:
            raise TypeError(
                f"Metric '{name}' is a {type(metric).__name__}, not a Gauge."
            )

    def observe(self, name: str, value: float,
                tags: dict[str, str] | None = None) -> None:
        """Record an observation in a histogram."""
        metric = self.get(name)
        if isinstance(metric, Histogram):
            metric.observe(value, tags)
        else:
            raise TypeError(
                f"Metric '{name}' is a {type(metric).__name__}, "
                f"not a Histogram."
            )

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------

    def timer(self, name: str,
              tags: dict[str, str] | None = None) -> Timer:
        """Create a Timer context manager for recording duration.

        The metric must already be registered as a histogram before
        calling timer(). The timer records elapsed milliseconds.

        Usage:
            with Metrics.timer("api.latency_ms"):
                result = await compute()
        """
        # Ensure the histogram exists
        self.get(name)  # raises if not registered
        return Timer(self, name, tags)

    def start_timer(self, name: str,
                    tags: dict[str, str] | None = None) -> Timer:
        """Create a Timer for manual start/stop.

        Usage:
            t = Metrics.start_timer("api.latency_ms")
            result = await compute()
            t.stop()
        """
        self.get(name)
        t = Timer(self, name, tags)
        t._start = __import__('time').perf_counter()
        return t

    # ------------------------------------------------------------------
    # Collection (for exporters)
    # ------------------------------------------------------------------

    def collect_all(self) -> list[Metric]:
        """Return all registered metrics for export.

        Exporters call this to get current metric state.
        """
        with self._lock:
            return list(self._metrics.values())

    def collect_by_namespace(self, namespace: str) -> list[Metric]:
        """Return metrics filtered by namespace prefix."""
        prefix = f"{namespace}."
        with self._lock:
            return [
                m for name, m in self._metrics.items()
                if name.startswith(prefix)
            ]

    def metric_count(self) -> int:
        """Return total number of registered metrics."""
        with self._lock:
            return len(self._metrics)
