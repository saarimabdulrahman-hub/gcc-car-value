"""Lifecycle detection — determines listing state transitions."""

from pipeline.history.models import LifecycleState, ListingSnapshot


class LifecycleDetector:
    """Determines lifecycle state for a listing based on its history.

    States:
        NEW       — First time seen
        UPDATED   — Previously seen, something changed
        UNCHANGED — Previously seen, nothing changed
        REMOVED   — Not found in current crawl (marked by caller)
        DUPLICATE — Matches an existing listing's fingerprint
        ARCHIVED  — Not seen for a long time
    """

    def determine(self, snapshot: ListingSnapshot,
                  previous: ListingSnapshot | None,
                  has_changes: bool) -> LifecycleState:
        """Determine the lifecycle state for a new snapshot."""
        if previous is None:
            return LifecycleState.NEW
        if has_changes:
            return LifecycleState.UPDATED
        return LifecycleState.UNCHANGED

    def mark_removed(self, snapshot: ListingSnapshot) -> ListingSnapshot:
        snapshot.lifecycle_state = LifecycleState.REMOVED
        snapshot.status = "removed"
        return snapshot

    def mark_archived(self, snapshot: ListingSnapshot) -> ListingSnapshot:
        snapshot.lifecycle_state = LifecycleState.ARCHIVED
        return snapshot

    def is_terminal(self, state: LifecycleState) -> bool:
        return state in (LifecycleState.REMOVED, LifecycleState.ARCHIVED)
