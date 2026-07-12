"""Enterprise metrics framework — registry, types, collectors, exporters.

Provides a centralized abstraction for all platform metrics.
Application code publishes metrics through this package without
knowing which exporter (Prometheus, CloudWatch, etc.) is active.

Usage:
    from src.core.metrics import Metrics

    # Counter
    Metrics.counter("valuation.requests", "Total valuation requests")
    Metrics.increment("valuation.requests", tags={"confidence": "high"})

    # Gauge
    Metrics.gauge("db.pool.size", "Database connection pool size")
    Metrics.set_gauge("db.pool.size", 8.0)

    # Histogram
    Metrics.histogram("api.latency_ms", "API request latency",
                      buckets=[10, 50, 100, 250, 500, 1000])

    # Timer
    with Metrics.timer("valuation.duration_ms"):
        result = await valuate(...)

    # Record observation
    Metrics.observe("api.latency_ms", 145.0)
"""

from src.core.metrics.registry import MetricsRegistry
from src.core.metrics.types import (
    MetricType, MetricValue, Metric,
    Counter, Gauge, Histogram, Timer,
)

# Global singleton — all application code uses this
Metrics = MetricsRegistry()


# Register application lifecycle metrics at import time
Metrics.info("app.version", "Application version")
Metrics.info("app.environment", "Deployment environment")
Metrics.counter("app.startups", "Application startup count")
