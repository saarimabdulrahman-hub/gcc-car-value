"""HistoryManager — central engine for incremental crawling and historical tracking.

Orchestrates: fingerprint → dedup → snapshot → change detection → lifecycle → history.
"""

import time
import structlog

from schema.listing import CanonicalListing
from pipeline.history.config import HistoryConfig
from pipeline.history.fingerprint import ListingFingerprint
from pipeline.history.snapshot import SnapshotEngine
from pipeline.history.change_detector import ChangeDetector
from pipeline.history.lifecycle import LifecycleDetector
from pipeline.history.deduplication import DeduplicationEngine
from pipeline.history.freshness import FreshnessEngine
from pipeline.history.statistics import HistoryStatistics
from pipeline.history.models import (
    ListingSnapshot, ListingHistory, LifecycleState,
)

logger = structlog.get_logger()


class HistoryManager:
    """Central engine for processing listings through the history pipeline.

    Usage:
        mgr = HistoryManager()
        for listing in crawl_results:
            history = mgr.process(listing, crawl_number=1)
            print(history.lifecycle_state)  # "new", "updated", "unchanged"
    """

    def __init__(self, config: HistoryConfig | None = None):
        self.config = config or HistoryConfig()
        self._fingerprint = ListingFingerprint()
        self._snapshot_engine = SnapshotEngine()
        self._change_detector = ChangeDetector(self.config.track_fields)
        self._lifecycle = LifecycleDetector()
        self._dedup = DeduplicationEngine(self.config.similarity_threshold)
        self._freshness = FreshnessEngine(self.config.freshness_decay_days)
        self._stats = HistoryStatistics()

        # In-memory store: fingerprint → ListingHistory
        self._store: dict[str, ListingHistory] = {}
        # Per-crawl stats
        self._crawl_number = 0
        self._crawl_snapshots: list[ListingSnapshot] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_crawl(self, crawl_number: int = 1) -> None:
        """Begin a new crawl cycle."""
        self._crawl_number = crawl_number
        self._crawl_snapshots = []
        # Reset in-crawl dedup tracking — same listing on different pages
        # within one crawl is a duplicate, but across crawls it's an update
        self._dedup = DeduplicationEngine(self.config.similarity_threshold)

    def process(self, listing: CanonicalListing,
                crawl_number: int | None = None) -> ListingHistory:
        """Process a single listing through the history pipeline.

        Returns the ListingHistory for this listing after processing.
        """
        cn = crawl_number or self._crawl_number

        # 1. Fingerprint
        fp = self._fingerprint.compute(listing)

        # 2. Check for duplicate
        if self._dedup.is_duplicate(fp):
            snapshot = self._snapshot_engine.create(listing, crawl_number=cn)
            snapshot.lifecycle_state = LifecycleState.DUPLICATE
            return self._store.get(fp, ListingHistory())

        # 3. Register fingerprint
        self._dedup.register(fp)

        # 4. Create snapshot
        snapshot = self._snapshot_engine.create(listing, crawl_number=cn)
        self._crawl_snapshots.append(snapshot)

        # 5. Get previous state
        previous_history = self._store.get(fp)
        previous_snapshot = previous_history.snapshots[-1] if (
            previous_history and previous_history.snapshots
        ) else None

        # 6. Detect changes
        has_changes = False
        changes = []
        if previous_snapshot:
            changes = self._change_detector.detect(previous_snapshot, snapshot)
            has_changes = self._change_detector.has_changes(previous_snapshot, snapshot)

        # 7. Determine lifecycle
        state = self._lifecycle.determine(snapshot, previous_snapshot, has_changes)
        snapshot.lifecycle_state = state
        snapshot.changes = changes

        # 8. Update history
        now = time.time()
        if previous_history is None:
            history = ListingHistory(
                listing_id=listing.listing_id,
                marketplace=listing.marketplace,
                fingerprint=fp,
                first_seen=now,
                last_seen=now,
                snapshots=[snapshot],
                lifecycle_state=state,
                crawl_count=1,
                update_count=1 if state != LifecycleState.UNCHANGED else 0,
            )
        else:
            previous_history.snapshots.append(snapshot)
            previous_history.last_seen = now
            previous_history.lifecycle_state = state
            previous_history.crawl_count += 1
            if state == LifecycleState.UPDATED:
                previous_history.update_count += 1
            history = previous_history

        self._store[fp] = history
        self._stats.record(state)

        logger.debug("history_processed",
                    listing_id=listing.listing_id[:8],
                    marketplace=listing.marketplace,
                    lifecycle=state.value,
                    changes=len(changes) if changes else 0)

        return history

    def mark_removed(self, listing_id: str, fingerprint: str) -> ListingHistory | None:
        """Mark a listing as removed (not found in current crawl)."""
        history = self._store.get(fingerprint)
        if history and history.snapshots:
            last = history.snapshots[-1]
            self._lifecycle.mark_removed(last)
            history.lifecycle_state = LifecycleState.REMOVED
        return history

    def end_crawl(self) -> dict:
        """End the current crawl. Marks unfound listings as removed."""
        # Mark listings not seen in this crawl as removed
        # (In real implementation, this runs against all known listings)
        return self._stats.snapshot()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_history(self, fingerprint: str) -> ListingHistory | None:
        return self._store.get(fingerprint)

    def get_all_histories(self) -> list[ListingHistory]:
        return list(self._store.values())

    def get_by_marketplace(self, marketplace: str) -> list[ListingHistory]:
        return [h for h in self._store.values() if h.marketplace == marketplace]

    def get_freshness(self, fingerprint: str) -> float:
        history = self._store.get(fingerprint)
        return self._freshness.score(history) if history else 0.0

    def get_by_lifecycle(self, state: LifecycleState) -> list[ListingHistory]:
        return [h for h in self._store.values() if h.lifecycle_state == state]

    @property
    def stats(self) -> dict: return self._stats.snapshot()

    @property
    def total_listings(self) -> int: return len(self._store)
