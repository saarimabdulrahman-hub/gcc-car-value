"""Idle behaviour — brief, medium, session-level idle with configurable probability."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class IdleBehaviour:
    """Simulates human idle periods between interactions.

    Usage:
        idle = IdleBehaviour(profile, timing)
        delay = idle.maybe_brief_idle()  # Returns ms or 0 if idle doesn't trigger
        if delay > 0:
            await asyncio.sleep(delay / 1000)
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def maybe_brief_idle(self) -> float:
        """Return a brief idle delay (ms) or 0 if idle doesn't trigger."""
        if self._timing.should_trigger(self._profile.brief_idle_probability):
            return self._timing.profile_range(
                self._profile.brief_idle_min,
                self._profile.brief_idle_max,
                multiplier=self._profile.interaction_frequency,
            )
        return 0.0

    def maybe_medium_idle(self) -> float:
        """Return a medium idle delay (ms) or 0 if idle doesn't trigger."""
        if self._timing.should_trigger(self._profile.medium_idle_probability):
            return self._timing.profile_range(
                self._profile.medium_idle_min,
                self._profile.medium_idle_max,
                multiplier=self._profile.interaction_frequency,
            )
        return 0.0

    def session_idle(self, duration_ms: float | None = None) -> float:
        """Return a session-level idle delay. Use before closing the session."""
        if duration_ms is not None:
            return duration_ms
        return self._timing.range_ms(1000, 5000)
