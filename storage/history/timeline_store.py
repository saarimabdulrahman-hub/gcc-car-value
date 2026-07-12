"""Timeline Store — exposes chronological history for listings."""

from storage.history.snapshot_store import SnapshotStore
from storage.history.models import TimelineEntry


class TimelineStore:
    """Builds and queries chronological timelines from snapshot data."""

    def __init__(self, snapshot_store: SnapshotStore):
        self._snapshots = snapshot_store

    def get_timeline(self, fingerprint: str) -> list[TimelineEntry]:
        """Return the full chronological timeline for a listing."""
        snapshots = self._snapshots.get_all(fingerprint)
        return [TimelineEntry(
            timestamp=s.captured_at, snapshot_id=s.snapshot_id,
            price=s.price, mileage_km=s.mileage_km,
            lifecycle_state=s.lifecycle_state.value if s.lifecycle_state else "",
            seller_name=s.seller_name, image_count=s.image_count,
        ) for s in snapshots]

    def get_price_timeline(self, fingerprint: str) -> list[dict]:
        """Return price-only timeline entries."""
        snapshots = self._snapshots.get_all(fingerprint)
        return [{"price": s.price, "currency": s.currency, "at": s.captured_at}
                for s in snapshots if s.price > 0]

    def get_mileage_timeline(self, fingerprint: str) -> list[dict]:
        snapshots = self._snapshots.get_all(fingerprint)
        return [{"mileage_km": s.mileage_km, "at": s.captured_at}
                for s in snapshots]

    def get_lifecycle_timeline(self, fingerprint: str) -> list[dict]:
        snapshots = self._snapshots.get_all(fingerprint)
        return [{"state": s.lifecycle_state.value, "at": s.captured_at}
                for s in snapshots if s.lifecycle_state]
