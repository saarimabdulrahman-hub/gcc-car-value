"""Test metric types — Counter, Gauge, Histogram, Timer, Info."""
import pytest
from src.core.metrics.types import (
    Counter, Gauge, Histogram, Timer, Info, MetricValue,
)


class TestCounter:
    def test_initial_value_is_zero(self):
        c = Counter("test.counter", "Test counter")
        assert c.value() == 0.0

    def test_inc_default(self):
        c = Counter("test.counter")
        c.inc()
        assert c.value() == 1.0

    def test_inc_amount(self):
        c = Counter("test.counter")
        c.inc(5.0)
        assert c.value() == 5.0

    def test_inc_multiple(self):
        c = Counter("test.counter")
        c.inc(1.0)
        c.inc(2.0)
        c.inc(3.0)
        assert c.value() == 6.0

    def test_never_decreases(self):
        c = Counter("test.counter")
        c.inc(10.0)
        c.inc(1.0)
        assert c.value() >= 10.0

    def test_collect_returns_metric_value(self):
        c = Counter("test.counter")
        c.inc(42.0)
        values = c.collect()
        assert len(values) == 1
        assert values[0].value == 42.0

    def test_full_name_includes_namespace(self):
        c = Counter("requests", namespace="api")
        assert c.full_name == "api.requests"


class TestGauge:
    def test_initial_value_is_zero(self):
        g = Gauge("test.gauge")
        assert g.value() == 0.0

    def test_set(self):
        g = Gauge("test.gauge")
        g.set(15.0)
        assert g.value() == 15.0

    def test_inc(self):
        g = Gauge("test.gauge")
        g.set(10.0)
        g.inc(5.0)
        assert g.value() == 15.0

    def test_dec(self):
        g = Gauge("test.gauge")
        g.set(10.0)
        g.dec(3.0)
        assert g.value() == 7.0

    def test_goes_negative(self):
        g = Gauge("test.gauge")
        g.set(5.0)
        g.dec(10.0)
        assert g.value() == -5.0


class TestHistogram:
    def test_initial_count_zero(self):
        h = Histogram("test.hist", buckets=[1, 5, 10])
        assert h.count() == 0
        assert h.sum() == 0.0

    def test_observe_increments_count(self):
        h = Histogram("test.hist", buckets=[1, 5, 10])
        h.observe(3.0)
        h.observe(7.0)
        assert h.count() == 2

    def test_observe_accumulates_sum(self):
        h = Histogram("test.hist", buckets=[1, 5, 10])
        h.observe(3.0)
        h.observe(7.0)
        assert h.sum() == 10.0

    def test_observe_falls_into_bucket(self):
        h = Histogram("test.hist", buckets=[1, 5, 10])
        h.observe(3.0)
        values = h.collect()
        # Find the bucket count for le="5" (3.0 is in the 5 bucket)
        bucket_value = [v for v in values if v.tags.get("le") == "5"]
        assert len(bucket_value) == 1, f"Expected bucket le=5, got values: {values}"
        assert bucket_value[0].value == 1.0

    def test_observe_above_all_buckets(self):
        h = Histogram("test.hist", buckets=[1, 5, 10])
        h.observe(999.0)
        values = h.collect()
        inf_value = [v for v in values if v.tags.get("le") == "+Inf"]
        assert len(inf_value) == 1
        assert inf_value[0].value == 1.0


class TestTimer:
    def test_timer_records_elapsed(self):
        """Timer context manager records duration."""
        import time
        from src.core.metrics import Metrics

        Metrics.histogram("test.timer.ms", buckets=[1, 10, 100, 1000])
        with Metrics.timer("test.timer.ms"):
            time.sleep(0.01)

        h = Metrics.get("test.timer.ms")
        assert isinstance(h, Histogram)
        assert h.count() == 1
        assert h.sum() > 0


class TestInfo:
    def test_info_metric(self):
        info = Info("app.version")
        info.set_info(version="1.0.0", env="test")
        values = info.collect()
        assert len(values) == 1
        assert values[0].tags.get("version") == "1.0.0"
        assert values[0].tags.get("env") == "test"
