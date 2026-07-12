"""Behaviour Manager — assigns profiles to sessions and provides interaction controllers."""

import asyncio
import structlog

from browser.behavior.models import BehaviourProfile
from browser.behavior.profile import BehaviourProfileCatalog
from browser.behavior.timing import TimingEngine
from browser.behavior.typing import TypingBehaviour
from browser.behavior.scroll import ScrollBehaviour
from browser.behavior.mouse import MouseBehaviour
from browser.behavior.navigation import NavigationBehaviour
from browser.behavior.reading import ReadingBehaviour
from browser.behavior.idle import IdleBehaviour
from browser.behavior.config import BehaviourConfig
from browser.behavior.errors import InvalidProfileError

logger = structlog.get_logger()


class BehaviourManager:
    """Central manager for human-like interaction behaviour.

    Assigns a BehaviourProfile to each session. Provides interaction
    controllers (typing, scroll, mouse, etc.) pre-configured with the
    session's profile. All timings are deterministic within a seeded
    timing engine.

    Usage:
        mgr = BehaviourManager()
        session = await mgr.acquire("session-1", profile_name="normal")
        typing = session.typing
        delay = typing.char_delay()
    """

    def __init__(self, config: BehaviourConfig | None = None):
        self.config = config or BehaviourConfig()
        self._catalog = BehaviourProfileCatalog()
        self._assignments: dict[str, BehaviourProfile] = {}
        self._timers: dict[str, TimingEngine] = {}
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Session assignment
    # ------------------------------------------------------------------

    async def assign(self, session_id: str,
                     profile_name: str | None = None) -> BehaviourProfile:
        """Assign a behaviour profile to a session."""
        name = profile_name or self.config.default_profile_name
        profile = self._catalog.get(name)
        self._validate(profile)

        async with self._lock:
            self._assignments[session_id] = profile
            self._timers[session_id] = TimingEngine(seed=self.config.seed)

        return profile

    async def get_profile(self, session_id: str) -> BehaviourProfile | None:
        async with self._lock:
            return self._assignments.get(session_id)

    async def release(self, session_id: str) -> None:
        async with self._lock:
            self._assignments.pop(session_id, None)
            self._timers.pop(session_id, None)

    # ------------------------------------------------------------------
    # Interaction controllers (for a given session)
    # ------------------------------------------------------------------

    async def typing(self, session_id: str) -> TypingBehaviour:
        profile = await self._get_or_default(session_id)
        return TypingBehaviour(profile, self._get_timer(session_id))

    async def scroll(self, session_id: str) -> ScrollBehaviour:
        profile = await self._get_or_default(session_id)
        return ScrollBehaviour(profile, self._get_timer(session_id))

    async def mouse(self, session_id: str) -> MouseBehaviour:
        profile = await self._get_or_default(session_id)
        return MouseBehaviour(profile, self._get_timer(session_id))

    async def navigation(self, session_id: str) -> NavigationBehaviour:
        profile = await self._get_or_default(session_id)
        return NavigationBehaviour(profile, self._get_timer(session_id))

    async def reading(self, session_id: str) -> ReadingBehaviour:
        profile = await self._get_or_default(session_id)
        return ReadingBehaviour(profile, self._get_timer(session_id))

    async def idle(self, session_id: str) -> IdleBehaviour:
        profile = await self._get_or_default(session_id)
        return IdleBehaviour(profile, self._get_timer(session_id))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _get_or_default(self, session_id: str) -> BehaviourProfile:
        profile = await self.get_profile(session_id)
        if profile is None:
            return self._catalog.get(self.config.default_profile_name)
        return profile

    def _get_timer(self, session_id: str) -> TimingEngine:
        timer = self._timers.get(session_id)
        if timer is None:
            timer = TimingEngine(seed=self.config.seed)
            self._timers[session_id] = timer
        return timer

    @staticmethod
    def _validate(profile: BehaviourProfile) -> None:
        if profile.typing_speed_min < 0 or profile.typing_speed_max < 0:
            raise InvalidProfileError("Typing speeds must be non-negative")
        if profile.typing_speed_min > profile.typing_speed_max:
            raise InvalidProfileError("Min typing speed cannot exceed max")
        if not (0.0 <= profile.interaction_frequency <= 5.0):
            raise InvalidProfileError("Interaction frequency must be 0-5")
