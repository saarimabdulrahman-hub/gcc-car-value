"""Timing engine — deterministic and ranged delays."""

import random


class TimingEngine:
    """Centralized timing with optional seeded randomness.

    When seed is None, uses system randomness. When a seed is set,
    delays are deterministic and reproducible — useful for testing.
    """

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed) if seed is not None else random.Random()

    def fixed(self, ms: float) -> float:
        """Return a fixed delay."""
        return max(0.0, ms)

    def range_ms(self, min_ms: float, max_ms: float) -> float:
        """Return a random delay in [min_ms, max_ms]."""
        if min_ms >= max_ms:
            return max(0.0, min_ms)
        return self._rng.uniform(min_ms, max_ms)

    def profile_range(self, min_ms: float, max_ms: float,
                      multiplier: float = 1.0,
                      variance: float = 0.0) -> float:
        """Return a delay scaled by interaction frequency with optional variance."""
        base = self.range_ms(min_ms, max_ms)
        # Apply interaction frequency multiplier
        base *= multiplier
        # Apply random variance
        if variance > 0:
            v = self._rng.uniform(-variance, variance)
            base *= (1.0 + v)
        return max(0.0, base)

    def should_trigger(self, probability: float) -> bool:
        """Return True with the given probability (0.0-1.0)."""
        return self._rng.random() < probability

    def jitter(self, base_ms: float, pct: float = 0.2) -> float:
        """Add ±pct jitter to a base delay."""
        factor = 1.0 + self._rng.uniform(-pct, pct)
        return max(0.0, base_ms * factor)
