"""Test analytics query engine — aggregations, filters, trends, time-series, cache."""
import pytest
from storage.history.repository import HistoryRepository
from storage.history.models import CurrentListing
from pipeline.history.models import ListingHistory, ListingSnapshot, LifecycleState
from analytics.query.query_engine import QueryEngine
from analytics.query.models import FilterCriteria
from analytics.query.cache import QueryCache


@pytest.fixture
def repo():
    r = HistoryRepository()
    # Seed with sample data
    for i in range(5):
        fp = f"fp-{i}"
        snapshots = [ListingSnapshot(fingerprint=fp, captured_at=1000 + i * 100,
                                    price=50000 + i * 10000, currency="AED",
                                    mileage_km=50000 + i * 5000,
                                    lifecycle_state=LifecycleState.NEW,
                                    listing_id=f"l-{i}", marketplace="dubizzle",
                                    raw_data={"make": "Toyota", "model": "Camry", "year": 2020 + i})]
        history = ListingHistory(fingerprint=fp, listing_id=f"l-{i}", marketplace="dubizzle",
                                snapshots=snapshots, first_seen=1000, last_seen=2000)
        r.save(history)
    return r


class TestQueryEngine:
    def test_average_price(self, repo):
        engine = QueryEngine(repo)
        avg = engine.average_price()
        assert avg > 0

    def test_median_price(self, repo):
        engine = QueryEngine(repo)
        med = engine.median_price()
        assert med > 0

    def test_active_count(self, repo):
        engine = QueryEngine(repo)
        count = engine.active_count()
        assert count == 5


class TestFilters:
    def test_marketplace_filter(self, repo):
        engine = QueryEngine(repo)
        f = FilterCriteria(marketplace="dubizzle")
        result = engine._aggregator.aggregate("price", "marketplace", f)
        assert result.total_count > 0

    def test_make_filter(self, repo):
        engine = QueryEngine(repo)
        f = FilterCriteria(make="Toyota")
        result = engine._aggregator.aggregate("price", "marketplace", f)
        assert result.total_count > 0


class TestCache:
    def test_set_and_get(self):
        cache = QueryCache(ttl_seconds=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_expiry(self):
        cache = QueryCache(ttl_seconds=0.0)  # Instant expiry
        cache.set("key", "val")
        assert cache.get("key") is None

    def test_hit_rate(self):
        cache = QueryCache(ttl_seconds=60)
        cache.get("key")  # miss
        cache.set("key", "val")
        cache.get("key")  # hit
        assert cache.hit_rate == 0.5

    def test_invalidate(self):
        cache = QueryCache(ttl_seconds=60)
        cache.set("key", "val")
        cache.invalidate("key")
        assert cache.get("key") is None
