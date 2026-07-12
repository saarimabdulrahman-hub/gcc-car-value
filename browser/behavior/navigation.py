"""Navigation behaviour — page settle, post-click, post-form delays."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class NavigationBehaviour:
    """Simulates human navigation timing patterns.

    Usage:
        nav = NavigationBehaviour(profile, timing)
        delay = nav.page_settle_delay()
        await asyncio.sleep(delay / 1000)
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def page_settle_delay(self) -> float:
        """Delay after page load to simulate reading/scanning."""
        return self._timing.profile_range(
            self._profile.page_settle_min,
            self._profile.page_settle_max,
            multiplier=self._profile.interaction_frequency,
        )

    def post_click_delay(self) -> float:
        """Delay after clicking before next action."""
        return self._timing.profile_range(
            self._profile.post_click_wait_min,
            self._profile.post_click_wait_max,
            multiplier=self._profile.interaction_frequency,
        )

    def post_form_delay(self) -> float:
        """Delay after submitting a form."""
        return self._timing.profile_range(
            self._profile.post_form_wait_min,
            self._profile.post_form_wait_max,
            multiplier=self._profile.interaction_frequency,
        )

    def refresh_delay(self) -> float:
        """Delay before refreshing a page."""
        return self._timing.range_ms(1000, 3000)
