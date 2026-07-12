"""Current Listing Store — maintains exactly one latest version per listing."""

import threading
from storage.history.models import CurrentListing
from storage.history.errors import ListingNotFoundError


class CurrentListingStore:
    """Thread-safe store for the latest version of each listing.

    Keyed by fingerprint. Supports insert, update, lookup, soft delete.
    """

    def __init__(self):
        self._store: dict[str, CurrentListing] = {}
        self._lock = threading.Lock()

    def save(self, entry: CurrentListing) -> None:
        """Insert or update the current listing."""
        with self._lock:
            self._store[entry.fingerprint] = entry

    def get(self, fingerprint: str) -> CurrentListing | None:
        with self._lock:
            return self._store.get(fingerprint)

    def get_or_raise(self, fingerprint: str) -> CurrentListing:
        entry = self.get(fingerprint)
        if entry is None: raise ListingNotFoundError(fingerprint)
        return entry

    def soft_delete(self, fingerprint: str) -> None:
        """Mark as removed — never actually delete."""
        with self._lock:
            if fingerprint in self._store:
                self._store[fingerprint].status = "removed"

    def list_active(self) -> list[CurrentListing]:
        with self._lock:
            return [e for e in self._store.values() if e.status != "removed"]

    def list_by_marketplace(self, marketplace: str) -> list[CurrentListing]:
        with self._lock:
            return [e for e in self._store.values() if e.marketplace == marketplace]

    def list_by_lifecycle(self, state: str) -> list[CurrentListing]:
        with self._lock:
            return [e for e in self._store.values() if e.lifecycle_state == state]

    def count(self) -> int:
        with self._lock: return len(self._store)

    def count_active(self) -> int:
        return len(self.list_active())
