"""Test history engine — fingerprint, snapshot, change detection, lifecycle, dedup, freshness."""
import pytest
from schema.listing import CanonicalListing
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from pipeline.history.fingerprint import ListingFingerprint
from pipeline.history.snapshot import SnapshotEngine
from pipeline.history.change_detector import ChangeDetector
from pipeline.history.lifecycle import LifecycleDetector, LifecycleState
from pipeline.history.deduplication import DeduplicationEngine
from pipeline.history.freshness import FreshnessEngine
from pipeline.history.history_manager import HistoryManager
from pipeline.history.models import ListingSnapshot, ListingHistory


def make_listing(marketplace="test", external_id="1", make="Toyota",
                 model="Camry", year=2020, price=75000.0, mileage=50000, **kw):
    return CanonicalListing(
        marketplace=marketplace, marketplace_listing_id=external_id,
        listing_url=f"https://test.com/{external_id}",
        vehicle=Vehicle(make=make, model=model, year=year, mileage_km=mileage),
        pricing=Pricing(amount=price, currency="AED"),
    )


class TestFingerprint:
    def test_stable_across_crawls(self):
        """Same listing produces same fingerprint."""
        l1 = make_listing()
        l2 = make_listing(price=80000.0)  # Price changed — still same listing
        fp = ListingFingerprint()
        assert fp.compute(l1) == fp.compute(l2)

    def test_different_listings_different_fingerprints(self):
        fp = ListingFingerprint()
        f1 = fp.compute(make_listing(external_id="1"))
        f2 = fp.compute(make_listing(external_id="2"))
        assert f1 != f2

    def test_fingerprint_is_hex(self):
        fp = ListingFingerprint()
        f = fp.compute(make_listing())
        assert len(f) == 64
        assert all(c in "0123456789abcdef" for c in f)


class TestSnapshotEngine:
    def test_creates_snapshot(self):
        engine = SnapshotEngine()
        s = engine.create(make_listing(), crawl_number=1)
        assert s.price == 75000.0
        assert s.mileage_km == 50000
        assert s.crawl_number == 1
        assert len(s.fingerprint) == 64


class TestChangeDetector:
    def test_detects_price_change(self):
        detector = ChangeDetector()
        prev = ListingSnapshot(price=75000, mileage_km=50000)
        curr = ListingSnapshot(price=72500, mileage_km=50000)
        assert detector.has_changes(prev, curr)
        changes = detector.detect(prev, curr)
        price_change = [c for c in changes if c.field == "price"][0]
        assert price_change.changed

    def test_no_changes_when_same(self):
        detector = ChangeDetector()
        prev = ListingSnapshot(price=75000, mileage_km=50000)
        curr = ListingSnapshot(price=75000, mileage_km=50000)
        assert not detector.has_changes(prev, curr)


class TestLifecycle:
    def test_new_listing(self):
        detector = LifecycleDetector()
        s = ListingSnapshot()
        state = detector.determine(s, None, False)
        assert state == LifecycleState.NEW

    def test_updated_listing(self):
        detector = LifecycleDetector()
        prev = ListingSnapshot()
        curr = ListingSnapshot(price=80000)
        state = detector.determine(curr, prev, True)
        assert state == LifecycleState.UPDATED

    def test_unchanged_listing(self):
        detector = LifecycleDetector()
        s = ListingSnapshot()
        state = detector.determine(s, s, False)
        assert state == LifecycleState.UNCHANGED


class TestDeduplication:
    def test_first_seen_not_duplicate(self):
        engine = DeduplicationEngine()
        assert not engine.is_duplicate("abc")

    def test_second_seen_is_duplicate(self):
        engine = DeduplicationEngine()
        engine.register("abc")
        assert engine.is_duplicate("abc")

    def test_similarity(self):
        engine = DeduplicationEngine()
        assert engine.similarity("abc", "abc") == 1.0
        assert engine.similarity("abc", "xyz") < 0.5


class TestFreshness:
    def test_unseen_listing_score_zero(self):
        engine = FreshnessEngine()
        h = ListingHistory(last_seen=0)
        assert engine.score(h) == 0.0

    def test_recent_listing_high_score(self):
        import time
        engine = FreshnessEngine()
        h = ListingHistory(last_seen=time.time())
        assert engine.score(h) >= 0.99


class TestHistoryManager:
    def test_process_new_listing(self):
        mgr = HistoryManager()
        mgr.start_crawl(1)
        history = mgr.process(make_listing())
        assert history.lifecycle_state == LifecycleState.NEW
        assert history.crawl_count == 1

    def test_process_updated_listing(self):
        mgr = HistoryManager()
        mgr.start_crawl(1)
        mgr.process(make_listing(price=75000))
        mgr.start_crawl(2)
        history = mgr.process(make_listing(price=72500))  # Price dropped
        assert history.lifecycle_state == LifecycleState.UPDATED
        assert history.update_count > 0  # At least one update occurred

    def test_process_unchanged_listing(self):
        mgr = HistoryManager()
        mgr.start_crawl(1)
        mgr.process(make_listing(price=75000))
        mgr.start_crawl(2)
        history = mgr.process(make_listing(price=75000))  # No change
        assert history.lifecycle_state == LifecycleState.UNCHANGED

    def test_price_history_tracked(self):
        mgr = HistoryManager()
        mgr.start_crawl(1)
        mgr.process(make_listing(price=75000))
        mgr.start_crawl(2)
        history = mgr.process(make_listing(price=72500))
        assert len(history.price_history) == 2
        assert history.price_history[0]["price"] == 75000
        assert history.price_history[1]["price"] == 72500

    def test_days_active(self):
        import time
        mgr = HistoryManager()
        mgr.start_crawl(1)
        h = mgr.process(make_listing())
        # First seen just now, so days_active should be ~0
        assert h.days_active < 1.0

    def test_stats(self):
        mgr = HistoryManager()
        mgr.start_crawl(1)
        mgr.process(make_listing(external_id="1"))
        mgr.process(make_listing(external_id="2"))
        stats = mgr.stats
        assert stats["new"] == 2
        assert stats["total"] == 2
