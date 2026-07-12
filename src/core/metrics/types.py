"""Metric type definitions — Counter, Gauge, Histogram, Timer.

All metric types share a common Metric base class. Types are thread-safe
for value accumulation but rely on the registry for registration safety.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
import threading
import time


class MetricType(StrEnum):
    COUNTER   = "counter"
    GAUGE     = "gauge"
    HISTOGRAM = "histogram"
    TIMER     = "timer"
    INFO      = "info"       # Static string metadata


@dataclass
class MetricValue:
    """A single observed value with optional tags."""
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Metric:
    """Base class for all metric types.

    Each metric has a unique name within its namespace and an optional
    description. Subclasses implement _collect() to return current values.
    """

    def __init__(self, name: str, description: str = "",
                 namespace: str = "", tags: dict[str, str] | None = None):
        self.name = name
        self.description = description
        self.namespace = namespace
        self.tags = tags or {}

    @property
    def full_name(self) -> str:
        """Fully qualified name: namespace.name"""
        if self.namespace:
            return f"{self.namespace}.{self.name}"
        return self.name

    def collect(self) -> list[MetricValue]:
        """Return current metric state. Called by exporters."""
        return self._collect()

    def _collect(self) -> list[MetricValue]:
        raise NotImplementedError


class Counter(Metric):
    """Monotonically increasing counter. Never decreases.

    Usage:
        c = Counter("requests", "Total API requests")
        c.inc()
        c.inc(5, tags={"status": "200"})
        total = c.value()
    """

    def __init__(self, name: str, description: str = "",
                 namespace: str = "", tags: dict[str, str] | None = None):
        super().__init__(name, description, namespace, tags)
        self._value: float = 0.0
        self._lock = threading.Lock()

    def inc(self, amount: float = 1.0,
            tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._value += amount

    def value(self) -> float:
        with self._lock:
            return self._value

    def _collect(self) -> list[MetricValue]:
        return [MetricValue(value=self.value(), tags=dict(self.tags))]


class Gauge(Metric):
    """Value that can go up or down. Represents a point-in-time measurement.

    Usage:
        g = Gauge("db_pool_size", "Connection pool size")
        g.set(10.0)
        g.inc(1.0)   # 11.0
        g.dec(3.0)   # 8.0
    """

    def __init__(self, name: str, description: str = "",
                 namespace: str = "", tags: dict[str, str] | None = None):
        super().__init__(name, description, namespace, tags)
        self._value: float = 0.0
        self._lock = threading.Lock()

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    def value(self) -> float:
        with self._lock:
            return self._value

    def _collect(self) -> list[MetricValue]:
        return [MetricValue(value=self.value(), tags=dict(self.tags))]


class Histogram(Metric):
    """Distribution of values across configurable buckets.

    Usage:
        h = Histogram("latency_ms", "API latency",
                      buckets=[10, 50, 100, 250, 500, 1000])
        h.observe(145.0)
        h.observe(32.0, tags={"endpoint": "/valuate"})
    """

    def __init__(self, name: str, description: str = "",
                 buckets: list[float] | None = None,
                 namespace: str = "", tags: dict[str, str] | None = None):
        super().__init__(name, description, namespace, tags)
        self.buckets = sorted(buckets) if buckets else [
            0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0,
        ]
        self._lock = threading.Lock()
        self._count: int = 0
        self._sum: float = 0.0
        self._bucket_counts: dict[float, int] = {
            b: 0 for b in self.buckets
        }
        self._bucket_counts[float("inf")] = 0

    def observe(self, value: float,
                tags: dict[str, str] | None = None) -> None:
        with self._lock:
            self._count += 1
            self._sum += value
            for bound in self.buckets:
                if value <= bound:
                    self._bucket_counts[bound] += 1
                    break
            else:
                self._bucket_counts[float("inf")] += 1

    def count(self) -> int:
        with self._lock:
            return self._count

    def sum(self) -> float:
        with self._lock:
            return self._sum

    def _collect(self) -> list[MetricValue]:
        with self._lock:
            base_tags = dict(self.tags)
            results = [
                MetricValue(value=float(self._count),
                           tags={**base_tags, "stat": "count"}),
                MetricValue(value=self._sum,
                           tags={**base_tags, "stat": "sum"}),
            ]
            for bound, count in self._bucket_counts.items():
                bucket_label = f"{bound}" if bound != float("inf") else "+Inf"
                results.append(MetricValue(
                    value=float(count),
                    tags={**base_tags, "le": bucket_label},
                ))
            return results


class Timer:
    """Context manager for recording operation duration.

    Usage:
        with Metrics.timer("valuation.duration_ms") as t:
            result = await valuate(...)
        # Automatically records elapsed_ms to the histogram

        # Or manually:
        t = Metrics.start_timer("valuation.duration_ms")
        result = await valuate(...)
        t.stop()
    """

    def __init__(self, registry: "MetricsRegistry", metric_name: str,
                 tags: dict[str, str] | None = None):
        self._registry = registry
        self._metric_name = metric_name
        self._tags = tags or {}
        self._start: float = 0.0
        self._elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args) -> None:
        self._elapsed = (time.perf_counter() - self._start) * 1000
        self._registry.observe(
            self._metric_name, self._elapsed, tags=self._tags
        )

    def stop(self) -> float:
        """Manual stop — returns elapsed ms."""
        self._elapsed = (time.perf_counter() - self._start) * 1000
        self._registry.observe(
            self._metric_name, self._elapsed, tags=self._tags
        )
        return self._elapsed

    @property
    def elapsed_ms(self) -> float:
        return self._elapsed


class Info(Metric):
    """Static string metadata — version, environment, etc.

    Usage:
        i = Info("app.version", "v1.2.3")
    """

    def __init__(self, name: str, description: str = "",
                 namespace: str = "", tags: dict[str, str] | None = None):
        super().__init__(name, description, namespace, tags)
        self._info: dict[str, str] = {}

    def set_info(self, **kwargs) -> None:
        self._info.update(kwargs)

    def _collect(self) -> list[MetricValue]:
        return [MetricValue(value=1.0, tags={**self.tags, **self._info})]
