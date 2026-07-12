"""Metric collectors — gather metric values from application internals.

Collectors are responsible for gathering data points and feeding them
into the registry. They are the bridge between instrumentation points
and exported metrics.

Future collectors:
    ProcessCollector     — CPU, memory, thread count
    DatabaseCollector    — Connection pool stats, query latency
    APICollector         — Request counts, status codes, latency
    SchedulerCollector   — Job execution counts, durations
    CacheCollector       — Hit rates, evictions
"""

from src.core.metrics.collectors.base import MetricCollector

__all__ = ["MetricCollector"]
