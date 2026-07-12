"""Deduplication engine — fingerprint matching, similarity scoring."""

from pipeline.history.models import ListingSnapshot, LifecycleState


class DeduplicationEngine:
    """Detects duplicate listings by fingerprint.

    Never deletes data — only marks duplicates.
    """

    def __init__(self, similarity_threshold: float = 0.85):
        self._threshold = similarity_threshold
        self._seen_fingerprints: set[str] = set()

    def is_duplicate(self, fingerprint: str) -> bool:
        """Check if a fingerprint has been seen before."""
        return fingerprint in self._seen_fingerprints

    def register(self, fingerprint: str) -> None:
        """Register a fingerprint as seen."""
        self._seen_fingerprints.add(fingerprint)

    def mark_duplicate(self, snapshot: ListingSnapshot) -> ListingSnapshot:
        """Mark a snapshot as duplicate."""
        snapshot.lifecycle_state = LifecycleState.DUPLICATE
        return snapshot

    def similarity(self, fp1: str, fp2: str) -> float:
        """Compute similarity between two fingerprints (simplified)."""
        if fp1 == fp2: return 1.0
        matches = sum(1 for a, b in zip(fp1, fp2) if a == b)
        return matches / max(len(fp1), len(fp2))
