"""Metric exporters — publish collected metrics to external systems.

Each exporter inherits from MetricExporter and implements export().
The registry knows nothing about exporters — they pull from the registry.

Future exporters:
    PrometheusExporter  — serve /metrics endpoint (P0018)
    CloudWatchExporter  — publish to AWS CloudWatch
    DatadogExporter     — publish to Datadog
    OTelExporter        — publish via OpenTelemetry
    LogExporter         — write metrics to structured logs
    FileExporter        — write metrics to a file (debugging)
"""

from src.core.metrics.exporters.base import MetricExporter

__all__ = ["MetricExporter"]
