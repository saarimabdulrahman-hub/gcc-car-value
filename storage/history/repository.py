"""History Repository — clean interface for save/load/query across stores."""

import time
from pipeline.history.models import ListingHistory, ListingSnapshot, LifecycleState
from storage.history.current_store import CurrentListingStore
from storage.history.snapshot_store import SnapshotStore
from storage.history.timeline_store import TimelineStore
from storage.history.models import CurrentListing


class HistoryRepository:
    """Unified interface to the historical dataset storage.

    Usage:
        repo = HistoryRepository()
        repo.save(history)  # Stores current + all snapshots + timeline
        current = repo.get_current(fingerprint)
        timeline = repo.get_price_timeline(fingerprint)
    """

    def __init__(self):
        self._current = CurrentListingStore()
        self._snapshots = SnapshotStore()
        self._timeline = TimelineStore(self._snapshots)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, history: ListingHistory) -> None:
        """Save a complete ListingHistory — current + all snapshots."""
        # Save current
        latest = history.snapshots[-1] if history.snapshots else None
        if latest:
            self._current.save(CurrentListing(
                fingerprint=history.fingerprint,
                listing_id=history.listing_id,
                marketplace=history.marketplace,
                price=latest.price, currency=latest.currency,
                mileage_km=latest.mileage_km,
                seller_name=latest.seller_name,
                status=latest.status,
                lifecycle_state=history.lifecycle_state,
                last_updated=history.last_seen,
                snapshot_count=len(history.snapshots),
                data=latest.raw_data,
            ))

        # Save all snapshots
        for snapshot in history.snapshots:
            self._snapshots.save(snapshot)

    def save_current(self, entry: CurrentListing) -> None:
        self._current.save(entry)

    def save_snapshot(self, snapshot: ListingSnapshot) -> None:
        self._snapshots.save(snapshot)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_current(self, fingerprint: str) -> CurrentListing | None:
        return self._current.get(fingerprint)

    def get_snapshots(self, fingerprint: str) -> list[ListingSnapshot]:
        return self._snapshots.get_all(fingerprint)

    def get_latest_snapshot(self, fingerprint: str) -> ListingSnapshot | None:
        return self._snapshots.get_latest(fingerprint)

    # --- Timeline queries ---

    def get_timeline(self, fingerprint: str) -> list:
        return self._timeline.get_timeline(fingerprint)

    def get_price_timeline(self, fingerprint: str) -> list[dict]:
        return self._timeline.get_price_timeline(fingerprint)

    def get_mileage_timeline(self, fingerprint: str) -> list[dict]:
        return self._timeline.get_mileage_timeline(fingerprint)

    def get_lifecycle_timeline(self, fingerprint: str) -> list[dict]:
        return self._timeline.get_lifecycle_timeline(fingerprint)

    # --- Filtered queries ---

    def list_active(self) -> list[CurrentListing]:
        return self._current.list_active()

    def list_removed(self) -> list[CurrentListing]:
        return self._current.list_by_lifecycle("removed")

    def list_by_marketplace(self, marketplace: str) -> list[CurrentListing]:
        return self._current.list_by_marketplace(marketplace)

    def list_recently_updated(self, max_age_seconds: float = 3600.0) -> list[CurrentListing]:
        now = time.time()
        return [e for e in self._current.list_active()
                if (now - e.last_updated) < max_age_seconds]

    # --- Statistics ---

    @property
    def stats(self) -> dict:
        return {
            "current_listings": self._current.count(),
            "active_listings": self._current.count_active(),
            "total_snapshots": self._snapshots.total_snapshots(),
            "listings_with_history": self._snapshots.total_listings(),
            "partition_distribution": self._snapshots.partition_distribution(),
        }
