"""Freshness engine — compute listing freshness scores."""

import time
from pipeline.history.models import ListingHistory


class FreshnessEngine:
    """Computes freshness scores for listings.

    Freshness = 1.0 for listings seen in the last hour, decaying to 0.0
    after freshness_decay_days.
    """

    def __init__(self, decay_days: float = 14.0):
        self._decay_seconds = decay_days * 86400.0

    def score(self, history: ListingHistory) -> float:
        """Compute freshness score (0.0–1.0)."""
        if history.last_seen <= 0: return 0.0
        elapsed = time.time() - history.last_seen
        if elapsed <= 0: return 1.0
        if elapsed >= self._decay_seconds: return 0.0
        return 1.0 - (elapsed / self._decay_seconds)

    def hours_since_last_seen(self, history: ListingHistory) -> float:
        if history.last_seen <= 0: return float("inf")
        return (time.time() - history.last_seen) / 3600.0

    def is_stale(self, history: ListingHistory, max_hours: float = 48.0) -> bool:
        return self.hours_since_last_seen(history) > max_hours
