"""Reading behaviour — time estimates based on page length."""

from browser.behavior.models import BehaviourProfile
from browser.behavior.timing import TimingEngine


class ReadingBehaviour:
    """Estimates reading time based on scrollable page height.

    Usage:
        reading = ReadingBehaviour(profile, timing)
        scroll_height = await page.evaluate("document.body.scrollHeight")
        delay = reading.estimate_time(scroll_height)
        await asyncio.sleep(delay / 1000)
    """

    def __init__(self, profile: BehaviourProfile, timing: TimingEngine):
        self._profile = profile
        self._timing = timing

    def estimate_time(self, scroll_height_px: int) -> float:
        """Estimate reading time in ms for a page of given scroll height.

        Longer pages get more reading time. The base rate is ms per 1000px.
        """
        if scroll_height_px <= 0:
            return 0.0

        base_ms = (scroll_height_px / 1000.0) * self._profile.reading_speed_ms_per_1k
        # Apply variance
        varied = self._timing.jitter(base_ms, self._profile.reading_variance)
        # Apply interaction frequency
        return max(0.0, varied * self._profile.interaction_frequency)

    def page_category(self, scroll_height_px: int) -> str:
        """Categorize a page by height."""
        if scroll_height_px < 1500:
            return "short"
        if scroll_height_px < 5000:
            return "medium"
        return "long"
