"""Typing behaviour — character-by-character typing with realistic delays."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class TypingBehaviour:
    """Simulates human typing with per-character delays.

    Usage:
        typing = TypingBehaviour(profile, TimingEngine())
        for char in "Hello":
            delay = typing.char_delay()
            await asyncio.sleep(delay / 1000)
            await page.keyboard.type(char)  # in Playwright driver
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def char_delay(self) -> float:
        """Return delay in ms before typing the next character."""
        return self._timing.profile_range(
            self._profile.typing_speed_min,
            self._profile.typing_speed_max,
            multiplier=self._profile.interaction_frequency,
            variance=self._profile.typing_variance,
        )

    def word_delay(self) -> float:
        """Return delay in ms between words (space + extra pause)."""
        return self.char_delay() * 3.0

    def field_delay(self) -> float:
        """Return delay in ms between form fields (tab navigation)."""
        return self._timing.range_ms(
            self._profile.post_form_wait_min // 3,
            self._profile.post_form_wait_max // 3,
        )

    def estimate_typing_time(self, text: str) -> float:
        """Estimate total ms to type a string."""
        chars = len(text)
        spaces = text.count(" ")
        avg_delay = (self._profile.typing_speed_min + self._profile.typing_speed_max) / 2
        return (chars * avg_delay + spaces * avg_delay * 2) * self._profile.interaction_frequency
