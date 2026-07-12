"""Test Prometheus exporter and formatter."""
import pytest
from src.core.metrics.registry import MetricsRegistry
from src.core.metrics.types import Counter, Gauge, Histogram, Info
from src.core.metrics.prometheus_formatter import (
    format_metrics, format_metrics as _fmt,
    _prometheus_name, _format_value, CONTENT_TYPE,
)
from src.core.metrics.exporters.prometheus import PrometheusExporter


@pytest.fixture
def registry():
    reg = MetricsRegistry()
    reg.counter("api.requests", "API request count")
    reg.gauge("db.pool.size", "DB pool size")
    reg.histogram("api.latency_ms", "API latency",
                 buckets=[10, 50, 100, 250, 500])
    reg.info("app.version", "App version")
    return reg


class TestPrometheusNaming:
    def test_dots_become_underscores(self):
        c = Counter("api.requests", namespace="test")
        name = _prometheus_name(c, "_total")
        assert name == "test_api_requests_total"

    def test_no_namespace(self):
        c = Counter("requests")
        name = _prometheus_name(c)
        assert name == "requests"

    def test_suffix_appended(self):
        g = Gauge("temp", namespace="system")
        name = _prometheus_name(g)
        assert name == "system_temp"


class TestValueFormatting:
    def test_integer(self):
        assert _format_value(42.0) == "42"

    def test_float(self):
        assert _format_value(3.14) == "3.14"

    def test_inf(self):
        assert _format_value(float("inf")) == "+Inf"

    def test_neg_inf(self):
        assert _format_value(float("-inf")) == "-Inf"


class TestFormatter:
    def test_counter_format(self, registry):
        registry.increment("api.requests", 5.0)
        body = format_metrics(registry.collect_all())
        assert "api_requests_total" in body
        assert "# TYPE api_requests_total counter" in body
        assert "api_requests_total 5" in body

    def test_gauge_format(self, registry):
        registry.set_gauge("db.pool.size", 10.0)
        body = format_metrics(registry.collect_all())
        assert "db_pool_size" in body
        assert "# TYPE db_pool_size gauge" in body

    def test_histogram_format(self, registry):
        registry.observe("api.latency_ms", 55.0)
        body = format_metrics(registry.collect_all())
        assert "api_latency_ms" in body
        assert "# TYPE api_latency_ms histogram" in body
        assert "api_latency_ms_bucket" in body
        assert "api_latency_ms_sum" in body
        assert "api_latency_ms_count" in body

    def test_info_format(self, registry):
        info = registry.get("app.version")
        assert isinstance(info, Info)
        info.set_info(version="1.2.3")
        body = format_metrics(registry.collect_all())
        assert "app_version_info" in body

    def test_help_text_included(self, registry):
        body = format_metrics(registry.collect_all())
        assert "# HELP api_requests_total API request count" in body

    def test_counter_increment_reflected(self, registry):
        registry.increment("api.requests", 1.0)
        body1 = format_metrics(registry.collect_all())
        registry.increment("api.requests", 2.0)
        body2 = format_metrics(registry.collect_all())
        assert "api_requests_total 1" in body1
        assert "api_requests_total 3" in body2

    def test_histogram_bucket_labels(self, registry):
        registry.observe("api.latency_ms", 55.0)
        body = format_metrics(registry.collect_all())
        # 55 is in the 100 bucket
        assert 'le="100"' in body

    def test_empty_metrics_produces_newline(self, registry):
        empty = MetricsRegistry()
        body = format_metrics(empty.collect_all())
        assert body == "\n"

    def test_content_type(self):
        assert "text/plain" in CONTENT_TYPE
        assert "version=0.0.4" in CONTENT_TYPE


class TestPrometheusExporter:
    def test_export_returns_content_type_and_body(self, registry):
        exporter = PrometheusExporter(registry)
        content_type, body = exporter.export_sync()
        assert isinstance(content_type, str)
        assert isinstance(body, str)
        assert "text/plain" in content_type

    def test_export_sync_matches_async(self, registry):
        import asyncio
        exporter = PrometheusExporter(registry)
        ct_sync, body_sync = exporter.export_sync()
        ct_async, body_async = asyncio.run(exporter.export())
        assert body_sync == body_async

    def test_format_name(self, registry):
        exporter = PrometheusExporter(registry)
        assert exporter.format_name() == "prometheus"

    def test_labels_appear_in_output(self):
        reg = MetricsRegistry()
        c = reg.counter("valuation.requests", "Valuation count",
                        tags={"source": "api", "version": "v1"})
        c.inc(5.0)
        body = format_metrics(reg.collect_all())
        assert 'source="api"' in body
        assert 'version="v1"' in body

    def test_histogram_labels_appear(self):
        reg = MetricsRegistry()
        h = reg.histogram("api.latency_ms", "API latency",
                          buckets=[10, 100],
                          tags={"endpoint": "/valuate"})
        h.observe(55.0)
        body = format_metrics(reg.collect_all())
        assert 'endpoint="/valuate"' in body
