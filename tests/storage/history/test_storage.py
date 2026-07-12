"""Test storage layer — current store, snapshot store, timeline, repository, queries."""
import time
import pytest
from storage.history.current_store import CurrentListingStore
from storage.history.snapshot_store import SnapshotStore
from storage.history.timeline_store import TimelineStore
from storage.history.repository import HistoryRepository
from storage.history.query import QueryAPI
from storage.history.models import CurrentListing, PartitionKey
from pipeline.history.models import ListingHistory, ListingSnapshot, LifecycleState


@pytest.fixture
def snapshot():
    return ListingSnapshot(fingerprint="fp-abc", listing_id="l-1", marketplace="test",
                          price=75000, currency="AED", mileage_km=50000,
                          lifecycle_state=LifecycleState.NEW, captured_at=time.time())


class TestCurrentStore:
    def test_save_and_get(self, snapshot):
        store = CurrentListingStore()
        entry = CurrentListing(fingerprint="fp-abc", listing_id="l-1", marketplace="test", price=75000)
        store.save(entry)
        assert store.get("fp-abc").price == 75000

    def test_soft_delete(self, snapshot):
        store = CurrentListingStore()
        store.save(CurrentListing(fingerprint="fp-abc", listing_id="l-1", marketplace="test", price=75000))
        store.soft_delete("fp-abc")
        assert store.get("fp-abc").status == "removed"

    def test_list_active_excludes_removed(self):
        store = CurrentListingStore()
        store.save(CurrentListing(fingerprint="fp-1", listing_id="l-1", marketplace="test", price=100))
        store.save(CurrentListing(fingerprint="fp-2", listing_id="l-2", marketplace="test", price=200))
        store.soft_delete("fp-2")
        assert len(store.list_active()) == 1

    def test_list_by_marketplace(self):
        store = CurrentListingStore()
        store.save(CurrentListing(fingerprint="fp-1", listing_id="l-1", marketplace="dubizzle", price=1))
        store.save(CurrentListing(fingerprint="fp-2", listing_id="l-2", marketplace="haraj", price=2))
        assert len(store.list_by_marketplace("dubizzle")) == 1


class TestSnapshotStore:
    def test_save_and_get_all(self, snapshot):
        store = SnapshotStore()
        store.save(snapshot)
        snapshots = store.get_all("fp-abc")
        assert len(snapshots) == 1

    def test_multiple_snapshots_ordered(self):
        store = SnapshotStore()
        s1 = ListingSnapshot(fingerprint="fp", captured_at=100, price=100)
        s2 = ListingSnapshot(fingerprint="fp", captured_at=200, price=200)
        s3 = ListingSnapshot(fingerprint="fp", captured_at=300, price=300)
        store.save(s2); store.save(s3); store.save(s1)
        snapshots = store.get_all("fp")
        assert snapshots[0].captured_at == 100
        assert snapshots[-1].captured_at == 300

    def test_partition_distribution(self):
        store = SnapshotStore()
        store.save(ListingSnapshot(fingerprint="fp", marketplace="dubizzle", captured_at=time.time()))
        dist = store.partition_distribution()
        assert len(dist) > 0

    def test_never_deletes(self):
        store = SnapshotStore()
        store.save(ListingSnapshot(fingerprint="fp", captured_at=1))
        store.save(ListingSnapshot(fingerprint="fp", captured_at=2))
        assert store.count_for_listing("fp") == 2


class TestTimelineStore:
    def test_price_timeline(self):
        snap_store = SnapshotStore()
        snap_store.save(ListingSnapshot(fingerprint="fp", captured_at=1, price=100, lifecycle_state=LifecycleState.NEW))
        snap_store.save(ListingSnapshot(fingerprint="fp", captured_at=2, price=90, lifecycle_state=LifecycleState.UPDATED))
        tl = TimelineStore(snap_store)
        prices = tl.get_price_timeline("fp")
        assert len(prices) == 2
        assert prices[0]["price"] == 100
        assert prices[1]["price"] == 90

    def test_lifecycle_timeline(self):
        snap_store = SnapshotStore()
        snap_store.save(ListingSnapshot(fingerprint="fp", captured_at=1, lifecycle_state=LifecycleState.NEW))
        snap_store.save(ListingSnapshot(fingerprint="fp", captured_at=2, lifecycle_state=LifecycleState.REMOVED))
        tl = TimelineStore(snap_store)
        lc = tl.get_lifecycle_timeline("fp")
        assert lc[0]["state"] == "new"
        assert lc[1]["state"] == "removed"


class TestRepository:
    def test_save_and_query(self):
        repo = HistoryRepository()
        snapshots = [
            ListingSnapshot(fingerprint="fp-r", captured_at=1, price=100, currency="AED",
                          lifecycle_state=LifecycleState.NEW, listing_id="l-1", marketplace="test"),
            ListingSnapshot(fingerprint="fp-r", captured_at=2, price=95, currency="AED",
                          lifecycle_state=LifecycleState.UPDATED, listing_id="l-1", marketplace="test"),
        ]
        history = ListingHistory(fingerprint="fp-r", listing_id="l-1", marketplace="test",
                                snapshots=snapshots, first_seen=1, last_seen=2)
        repo.save(history)

        current = repo.get_current("fp-r")
        assert current.price == 95
        assert current.snapshot_count == 2

        snapshots = repo.get_snapshots("fp-r")
        assert len(snapshots) == 2

    def test_query_api(self):
        repo = HistoryRepository()
        snapshots = [ListingSnapshot(fingerprint="fp-q", captured_at=1, price=50000, currency="AED",
                                    lifecycle_state=LifecycleState.NEW, listing_id="l-1", marketplace="test")]
        repo.save(ListingHistory(fingerprint="fp-q", listing_id="l-1", marketplace="test",
                                snapshots=snapshots, first_seen=1, last_seen=1))

        q = QueryAPI(repo)
        result = q.latest("fp-q")
        assert result["price"] == 50000
        assert q.price_history("fp-q")[0]["price"] == 50000


class TestPartitionKey:
    def test_from_timestamp(self):
        pk = PartitionKey.from_timestamp("dubizzle", 1750000000.0)  # ~2025-06-15
        assert pk.marketplace == "dubizzle"
        assert pk.year_month.startswith("2025")

    def test_current_month(self):
        pk = PartitionKey.from_timestamp("test", time.time())
        import datetime
        expected = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")
        assert pk.year_month == expected
