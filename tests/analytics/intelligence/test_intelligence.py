"""Test market intelligence engine — price index, depreciation, liquidity, health, benchmarks."""
import pytest
from storage.history.repository import HistoryRepository
from storage.history.models import CurrentListing
from pipeline.history.models import ListingHistory, ListingSnapshot, LifecycleState
from analytics.query.query_engine import QueryEngine
from analytics.intelligence.intelligence_engine import IntelligenceEngine


@pytest.fixture
def repo():
    r = HistoryRepository()
    for i in range(10):
        fp = f"fp-{i}"
        yr = 2015 + i  # 2015-2024
        snapshots = [ListingSnapshot(fingerprint=fp, captured_at=1000 + i * 100,
                                    price=30000 + i * 5000, currency="AED",
                                    mileage_km=50000 + i * 10000,
                                    lifecycle_state=LifecycleState.NEW,
                                    listing_id=f"l-{i}", marketplace="dubizzle",
                                    raw_data={"make": "Toyota", "model": "Camry", "year": yr})]
        r.save(ListingHistory(fingerprint=fp, listing_id=f"l-{i}", marketplace="dubizzle",
                             snapshots=snapshots, first_seen=1000, last_seen=2000))
    return r


class TestIntelligenceEngine:
    def test_price_index(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        idx = engine.price_index(make="Toyota", model="Camry")
        assert idx.current_index > 0
        assert idx.index_type == "model"
        assert "toyota_camry" in idx.segment.lower()

    def test_depreciation(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        curve = engine.depreciation("Toyota", "Camry")
        assert curve.make == "Toyota"
        assert curve.model == "Camry"
        assert len(curve.data_points) > 0

    def test_liquidity(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        liq = engine.liquidity()
        assert liq.days_to_sell_estimate >= 0

    def test_market_health(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        health = engine.market_health("dubizzle")
        assert health.stability_score >= 0

    def test_benchmark(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        bm = engine.benchmark("Toyota", "Camry")
        assert bm.make == "Toyota"
        assert bm.p50 > 0

    def test_forecast_inputs(self, repo):
        engine = IntelligenceEngine(QueryEngine(repo))
        fi = engine.forecast_inputs(make="Toyota", model="Camry")
        assert fi.ma_30d >= 0
