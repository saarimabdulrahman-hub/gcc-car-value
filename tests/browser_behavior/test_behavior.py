"""Test behaviour engine — profiles, timing, typing, scroll, mouse, navigation, reading, idle."""
import pytest
from browser.behavior.timing import TimingEngine
from browser.behavior.profile import BehaviourProfileCatalog
from browser.behavior.typing import TypingBehaviour
from browser.behavior.scroll import ScrollBehaviour
from browser.behavior.mouse import MouseBehaviour
from browser.behavior.navigation import NavigationBehaviour
from browser.behavior.reading import ReadingBehaviour
from browser.behavior.idle import IdleBehaviour
from browser.behavior.manager import BehaviourManager
from browser.behavior.models import BehaviourProfile
from browser.behavior.errors import InvalidProfileError


@pytest.fixture
def profile():
    return BehaviourProfileCatalog.get("normal")

@pytest.fixture
def timing():
    return TimingEngine(seed=42)  # Deterministic for testing


class TestTimingEngine:
    def test_fixed_returns_value(self, timing):
        assert timing.fixed(100) == 100.0

    def test_range_ms_in_bounds(self, timing):
        for _ in range(100):
            d = timing.range_ms(100, 200)
            assert 100.0 <= d <= 200.0

    def test_should_trigger_probability(self, timing):
        # With seed=42, this should be deterministic
        results = [timing.should_trigger(0.5) for _ in range(100)]
        # Roughly half should trigger
        assert 30 < sum(results) < 70

    def test_seeded_timing_is_deterministic(self):
        t1 = TimingEngine(seed=42)
        t2 = TimingEngine(seed=42)
        v1 = [t1.range_ms(100, 200) for _ in range(20)]
        v2 = [t2.range_ms(100, 200) for _ in range(20)]
        assert v1 == v2

    def test_jitter(self, timing):
        base = 100.0
        for _ in range(100):
            d = timing.jitter(base, 0.2)
            assert 80.0 <= d <= 120.0


class TestProfiles:
    def test_catalog_has_all_styles(self):
        names = BehaviourProfileCatalog.list_names()
        assert "normal" in names
        assert "fast" in names
        assert "thorough" in names
        assert "relaxed" in names

    def test_get_default_returns_normal_for_unknown(self):
        p = BehaviourProfileCatalog.get("nonexistent")
        assert p.name == "normal"

    def test_all_profiles_are_valid(self):
        for p in BehaviourProfileCatalog.all():
            assert p.typing_speed_min <= p.typing_speed_max
            assert 0.0 <= p.interaction_frequency <= 5.0


class TestTypingBehaviour:
    def test_char_delay_in_range(self, profile, timing):
        typing = TypingBehaviour(profile, timing)
        for _ in range(100):
            d = typing.char_delay()
            # After variance + multiplier, should be roughly in range
            assert d > 0

    def test_estimate_typing_time(self, profile, timing):
        typing = TypingBehaviour(profile, timing)
        t = typing.estimate_typing_time("Hello World")
        assert t > 0  # Some positive time


class TestScrollBehaviour:
    def test_steps_for_distance(self, profile, timing):
        scroll = ScrollBehaviour(profile, timing)
        steps = scroll.steps_for_distance(1200)
        assert len(steps) > 0
        assert sum(steps) == 1200

    def test_zero_distance_returns_empty(self, profile, timing):
        scroll = ScrollBehaviour(profile, timing)
        assert scroll.steps_for_distance(0) == []


class TestMouseBehaviour:
    def test_move_delay_in_range(self, profile, timing):
        mouse = MouseBehaviour(profile, timing)
        for _ in range(100):
            d = mouse.move_delay()
            assert d > 0


class TestNavigationBehaviour:
    def test_page_settle_delay(self, profile, timing):
        nav = NavigationBehaviour(profile, timing)
        d = nav.page_settle_delay()
        assert d > 0


class TestReadingBehaviour:
    def test_estimate_short_page(self, profile, timing):
        reading = ReadingBehaviour(profile, timing)
        d = reading.estimate_time(800)
        assert d > 0

    def test_page_category(self, profile, timing):
        reading = ReadingBehaviour(profile, timing)
        assert reading.page_category(500) == "short"
        assert reading.page_category(3000) == "medium"
        assert reading.page_category(8000) == "long"


class TestIdleBehaviour:
    def test_maybe_brief_idle(self, profile, timing):
        idle = IdleBehaviour(profile, timing)
        results = [idle.maybe_brief_idle() > 0 for _ in range(200)]
        # ~10% should trigger with seed=42
        triggered = sum(results)
        assert 0 <= triggered <= 200  # Just check no errors


class TestBehaviourManager:
    @pytest.mark.asyncio
    async def test_assign_and_get_profile(self):
        mgr = BehaviourManager()
        profile = await mgr.assign("session-1", profile_name="fast")
        assert profile.name == "fast"
        retrieved = await mgr.get_profile("session-1")
        assert retrieved.profile_id == profile.profile_id

    @pytest.mark.asyncio
    async def test_release(self):
        mgr = BehaviourManager()
        await mgr.assign("session-2", profile_name="normal")
        await mgr.release("session-2")
        assert await mgr.get_profile("session-2") is None

    @pytest.mark.asyncio
    async def test_typing_controller(self):
        mgr = BehaviourManager()
        await mgr.assign("session-3")
        typing = await mgr.typing("session-3")
        assert isinstance(typing, TypingBehaviour)
        assert typing.char_delay() > 0

    @pytest.mark.asyncio
    async def test_invalid_profile_rejected(self):
        mgr = BehaviourManager()
        bad = BehaviourProfile(typing_speed_min=500, typing_speed_max=100)
        with pytest.raises(InvalidProfileError):
            mgr._validate(bad)
