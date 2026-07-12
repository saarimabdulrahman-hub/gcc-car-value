"""Mouse behaviour — move, hover, click with timing."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class MouseBehaviour:
    """Simulates human mouse interaction timing.

    Usage:
        mouse = MouseBehaviour(profile, timing)
        delay = mouse.move_delay()
        await asyncio.sleep(delay / 1000)
        await page.click(selector)
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def move_delay(self) -> float:
        """Delay for mouse movement to a target in ms."""
        return self._timing.profile_range(
            self._profile.mouse_move_min,
            self._profile.mouse_move_max,
            multiplier=self._profile.interaction_frequency,
        )

    def hover_delay(self) -> float:
        """Delay between hovering over an element and clicking it."""
        return self._timing.profile_range(
            self._profile.hover_delay_min,
            self._profile.hover_delay_max,
            multiplier=self._profile.interaction_frequency,
        )

    def click_delay(self) -> float:
        """Delay between clicks (e.g., for double-click or multi-click)."""
        return self._timing.range_ms(50, 150)

    def focus_delay(self) -> float:
        """Delay after focusing an element before typing."""
        return self._timing.range_ms(100, 300)
