"""PrometheusExporter — publishes registry metrics in Prometheus text format.

Uses the PrometheusFormatter to serialize all registered metrics into the
Prometheus exposition format. Called by the /metrics endpoint on each scrape.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.metrics.exporters.base import MetricExporter
from src.core.metrics.prometheus_formatter import format_metrics, CONTENT_TYPE

if TYPE_CHECKING:
    from src.core.metrics.registry import MetricsRegistry


class PrometheusExporter(MetricExporter):
    """Pull-based Prometheus exporter.

    Does NOT push metrics on a schedule. Instead, the /metrics endpoint
    calls export() on each scrape request. This is the standard Prometheus
    pull model — the exporter formats metrics on-demand.

    Usage:
        exporter = PrometheusExporter(Metrics)
        text = await exporter.export()  # Returns (content_type, body)
    """

    def __init__(self, registry: "MetricsRegistry"):
        super().__init__(registry)

    def format_name(self) -> str:
        return "prometheus"

    async def export(self) -> tuple[str, str]:
        """Export all registered metrics in Prometheus text format.

        Returns:
            Tuple of (content_type, response_body).
        """
        metrics = self.registry.collect_all()
        body = format_metrics(metrics)
        return CONTENT_TYPE, body

    def export_sync(self) -> tuple[str, str]:
        """Synchronous export — for use in non-async contexts.

        Since format_metrics() is pure CPU work (no I/O), it's safe to
        call synchronously. The /metrics endpoint uses this to avoid
        unnecessary async overhead.
        """
        metrics = self.registry.collect_all()
        body = format_metrics(metrics)
        return CONTENT_TYPE, body
