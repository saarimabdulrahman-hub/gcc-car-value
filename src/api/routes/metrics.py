"""GET /metrics — Prometheus metrics endpoint.

Serves metrics in Prometheus text format through the PrometheusExporter.
The endpoint never accesses the registry directly — it delegates to the
exporter, which is the only component that serializes metric values.
"""

from fastapi import APIRouter, Response
from src.core.metrics import Metrics
from src.core.metrics.exporters.prometheus import PrometheusExporter

router = APIRouter()

# Singleton exporter — created once, reused across scrapes
_exporter = PrometheusExporter(Metrics)


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint.

    Returns all registered metrics in Prometheus exposition format.
    Called by Prometheus on its scrape interval (typically 15-60s).

    Updates the uptime gauge before each scrape so Prometheus always
    gets the current process uptime.
    """
    from src.api.main import _update_uptime
    _update_uptime()
    content_type, body = _exporter.export_sync()
    return Response(content=body, media_type=content_type)
