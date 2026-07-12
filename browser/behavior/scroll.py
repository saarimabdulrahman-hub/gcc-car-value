"""Scroll behaviour — small/large/incremental with pauses."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class ScrollBehaviour:
    """Simulates human scrolling patterns.

    Usage:
        scroll = ScrollBehaviour(profile, timing)
        steps = scroll.steps_for_distance(1200)  # Scroll 1200px
        for step_px in steps:
            delay = scroll.step_delay()
            await asyncio.sleep(delay / 1000)
            await page.evaluate(f"window.scrollBy(0, {step_px})")
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def steps_for_distance(self, distance_px: int) -> list[int]:
        """Break a scroll distance into human-like steps."""
        if distance_px <= 0:
            return []
        step = self._profile.scroll_step_px
        steps: list[int] = []
        remaining = abs(distance_px)
        while remaining > 0:
            # Vary step size slightly
            actual = self._timing.jitter(step, pct=0.3)
            actual = min(actual, remaining)
            actual = int(actual)
            steps.append(actual)
            remaining -= actual
        return steps

    def step_delay(self) -> float:
        """Delay between scroll steps in ms."""
        return self._timing.profile_range(
            self._profile.scroll_pause_min,
            self._profile.scroll_pause_max,
            multiplier=self._profile.interaction_frequency,
        )

    def scroll_to_element_delay(self) -> float:
        """Delay after scrolling to an element before interacting."""
        return self._timing.range_ms(
            self._profile.hover_delay_min,
            self._profile.hover_delay_max,
        )
