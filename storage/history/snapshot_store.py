"""Snapshot Store — stores every historical snapshot, never overwrites, never deletes."""

import threading
from pipeline.history.models import ListingSnapshot
from storage.history.models import PartitionKey


class SnapshotStore:
    """Append-only store for listing snapshots. Keyed by (fingerprint, timestamp).

    Supports partition-aware storage — snapshots can be grouped by month + marketplace.
    Never overwrites or deletes — historical data is immutable.
    """

    def __init__(self):
        self._store: dict[str, dict[float, ListingSnapshot]] = {}  # fingerprint → {timestamp → snapshot}
        self._lock = threading.Lock()
        self._total_inserts = 0

    def save(self, snapshot: ListingSnapshot) -> None:
        """Store a snapshot. Idempotent — same (fingerprint, timestamp) overwrites."""
        with self._lock:
            if snapshot.fingerprint not in self._store:
                self._store[snapshot.fingerprint] = {}
            self._store[snapshot.fingerprint][snapshot.captured_at] = snapshot
            self._total_inserts += 1

    def get_all(self, fingerprint: str) -> list[ListingSnapshot]:
        """Return all snapshots for a listing, chronologically."""
        with self._lock:
            entries = self._store.get(fingerprint, {})
            return sorted(entries.values(), key=lambda s: s.captured_at)

    def get_latest(self, fingerprint: str) -> ListingSnapshot | None:
        snapshots = self.get_all(fingerprint)
        return snapshots[-1] if snapshots else None

    def count_for_listing(self, fingerprint: str) -> int:
        with self._lock:
            return len(self._store.get(fingerprint, {}))

    def total_snapshots(self) -> int:
        with self._lock: return self._total_inserts

    def total_listings(self) -> int:
        with self._lock: return len(self._store)

    def get_by_partition(self, marketplace: str, year_month: str) -> list[ListingSnapshot]:
        """Return all snapshots in a given partition."""
        results = []
        with self._lock:
            for entries in self._store.values():
                for ts, snapshot in entries.items():
                    pk = PartitionKey.from_timestamp(marketplace, ts)
                    if pk.marketplace == marketplace and pk.year_month == year_month:
                        results.append(snapshot)
        return results

    def partition_distribution(self) -> dict[str, int]:
        """Count of snapshots per partition."""
        dist: dict[str, int] = {}
        with self._lock:
            for entries in self._store.values():
                for ts, snapshot in entries.items():
                    pk = PartitionKey.from_timestamp(snapshot.marketplace, ts)
                    key = f"{pk.marketplace}/{pk.year_month}"
                    dist[key] = dist.get(key, 0) + 1
        return dist
