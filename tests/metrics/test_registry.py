"""Test MetricsRegistry — registration, lookup, mutation, thread safety."""
import pytest
import threading
from src.core.metrics.registry import (
    MetricsRegistry, DuplicateMetricError, MetricNotFoundError,
)
from src.core.metrics.types import Counter, Gauge, Histogram


@pytest.fixture
def registry():
    """Fresh registry for each test."""
    return MetricsRegistry()


class TestRegistration:
    def test_register_counter(self, registry):
        c = registry.counter("test.requests", "Test counter")
        assert isinstance(c, Counter)
        assert c.full_name == "test.requests"

    def test_register_gauge(self, registry):
        g = registry.gauge("test.temp", "Test gauge")
        assert isinstance(g, Gauge)
        assert g.full_name == "test.temp"

    def test_register_histogram(self, registry):
        h = registry.histogram("test.latency", "Test histogram",
                               buckets=[10, 50, 100])
        assert isinstance(h, Histogram)
        assert h.buckets == [10, 50, 100]

    def test_duplicate_registration_raises(self, registry):
        registry.counter("test.dup")
        with pytest.raises(DuplicateMetricError, match="test.dup"):
            registry.counter("test.dup")

    def test_duplicate_message_mentions_get(self, registry):
        registry.counter("test.dup2")
        with pytest.raises(DuplicateMetricError, match="get"):
            registry.gauge("test.dup2")

    def test_namespace_produces_unique_name(self, registry):
        registry.counter("requests", namespace="api")
        registry.counter("requests", namespace="db")
        names = registry.list_names()
        assert "api.requests" in names
        assert "db.requests" in names


class TestLookup:
    def test_get_existing(self, registry):
        registry.counter("test.exists")
        m = registry.get("test.exists")
        assert isinstance(m, Counter)

    def test_get_missing_raises(self, registry):
        with pytest.raises(MetricNotFoundError, match="test.missing"):
            registry.get("test.missing")

    def test_get_or_register_creates_once(self, registry):
        def factory():
            return Counter("test.gor", "GOR test")

        m1 = registry.get_or_register("test.gor", factory)
        m2 = registry.get_or_register("test.gor", factory)
        assert m1 is m2

    def test_list_names(self, registry):
        registry.counter("a.one")
        registry.gauge("b.two")
        registry.histogram("c.three", buckets=[1, 5])
        names = registry.list_names()
        assert len(names) == 3
        assert "a.one" in names

    def test_list_names_filtered_by_namespace(self, registry):
        registry.counter("api.requests")
        registry.counter("api.errors")
        registry.counter("db.connections")
        api_names = registry.list_names(namespace="api")
        assert len(api_names) == 2
        assert "api.requests" in api_names
        assert "api.errors" in api_names
        assert "db.connections" not in api_names

    def test_metric_count(self, registry):
        assert registry.metric_count() == 0
        registry.counter("a.one")
        registry.gauge("b.two")
        assert registry.metric_count() == 2


class TestMutation:
    def test_increment_counter(self, registry):
        registry.counter("test.ctr")
        registry.increment("test.ctr", 5.0)
        c = registry.get("test.ctr")
        assert isinstance(c, Counter)
        assert c.value() == 5.0

    def test_increment_gauge(self, registry):
        registry.gauge("test.g")
        registry.increment("test.g", 3.0)
        g = registry.get("test.g")
        assert isinstance(g, Gauge)
        assert g.value() == 3.0

    def test_set_gauge(self, registry):
        registry.gauge("test.g2")
        registry.set_gauge("test.g2", 42.0)
        assert registry.get("test.g2").value() == 42.0

    def test_decrement_gauge(self, registry):
        registry.gauge("test.g3")
        registry.set_gauge("test.g3", 10.0)
        registry.decrement("test.g3", 4.0)
        assert registry.get("test.g3").value() == 6.0

    def test_observe_histogram(self, registry):
        registry.histogram("test.h", buckets=[1, 10, 100])
        registry.observe("test.h", 55.0)
        h = registry.get("test.h")
        assert isinstance(h, Histogram)
        assert h.count() == 1

    def test_increment_on_histogram_raises(self, registry):
        registry.histogram("test.h2", buckets=[1])
        with pytest.raises(TypeError):
            registry.increment("test.h2")

    def test_observe_on_counter_raises(self, registry):
        registry.counter("test.c2")
        with pytest.raises(TypeError):
            registry.observe("test.c2", 5.0)


class TestCollect:
    def test_collect_all(self, registry):
        registry.counter("a.one")
        registry.gauge("b.two")
        metrics = registry.collect_all()
        assert len(metrics) == 2

    def test_collect_by_namespace(self, registry):
        registry.counter("api.requests")
        registry.counter("db.pool")
        api_metrics = registry.collect_by_namespace("api")
        assert len(api_metrics) == 1
        assert api_metrics[0].full_name == "api.requests"


class TestConcurrency:
    def test_concurrent_counter_increments(self):
        """Multiple threads incrementing the same counter."""
        registry = MetricsRegistry()
        registry.counter("test.concurrent")
        iterations = 1000
        threads = 4

        def worker():
            for _ in range(iterations):
                registry.increment("test.concurrent")

        ts = [threading.Thread(target=worker) for _ in range(threads)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()

        c = registry.get("test.concurrent")
        assert isinstance(c, Counter)
        assert c.value() == float(iterations * threads)

    def test_concurrent_get_or_register(self):
        """get_or_register is thread-safe."""
        registry = MetricsRegistry()
        results = []

        def worker():
            m = registry.get_or_register(
                "test.gor.concurrent",
                lambda: Counter("test.gor.concurrent"),
            )
            results.append(id(m))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads got the same object
        assert len(set(results)) == 1
