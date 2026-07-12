"""BehaviourProfile catalog — curated interaction profiles."""

from browser.behavior.models import BehaviourProfile


# Curated profiles for different session styles
PROFILES: dict[str, BehaviourProfile] = {
    "normal": BehaviourProfile(
        name="normal",
        typing_speed_min=80, typing_speed_max=200,
        scroll_step_px=300, scroll_pause_min=200, scroll_pause_max=800,
        mouse_move_min=100, mouse_move_max=400,
        hover_delay_min=100, hover_delay_max=300,
        reading_speed_ms_per_1k=3000,
        page_settle_min=500, page_settle_max=2000,
        post_click_wait_min=300, post_click_wait_max=1500,
        post_form_wait_min=500, post_form_wait_max=2000,
        brief_idle_probability=0.1, medium_idle_probability=0.02,
        session_style="normal",
    ),
    "fast": BehaviourProfile(
        name="fast",
        typing_speed_min=40, typing_speed_max=100,
        scroll_step_px=500, scroll_pause_min=100, scroll_pause_max=300,
        mouse_move_min=50, mouse_move_max=150,
        hover_delay_min=50, hover_delay_max=150,
        reading_speed_ms_per_1k=1000,
        page_settle_min=200, page_settle_max=800,
        post_click_wait_min=100, post_click_wait_max=500,
        post_form_wait_min=200, post_form_wait_max=800,
        brief_idle_probability=0.03, medium_idle_probability=0.0,
        session_style="fast",
        interaction_frequency=0.5,
    ),
    "thorough": BehaviourProfile(
        name="thorough",
        typing_speed_min=100, typing_speed_max=300,
        scroll_step_px=200, scroll_pause_min=500, scroll_pause_max=1500,
        mouse_move_min=150, mouse_move_max=500,
        hover_delay_min=200, hover_delay_max=500,
        reading_speed_ms_per_1k=5000,
        page_settle_min=1000, page_settle_max=4000,
        post_click_wait_min=500, post_click_wait_max=3000,
        post_form_wait_min=1000, post_form_wait_max=4000,
        brief_idle_probability=0.15, medium_idle_probability=0.05,
        session_style="thorough",
        interaction_frequency=1.5,
    ),
    "relaxed": BehaviourProfile(
        name="relaxed",
        typing_speed_min=150, typing_speed_max=400,
        scroll_step_px=200, scroll_pause_min=800, scroll_pause_max=2000,
        mouse_move_min=200, mouse_move_max=600,
        hover_delay_min=200, hover_delay_max=600,
        reading_speed_ms_per_1k=6000,
        page_settle_min=1500, page_settle_max=5000,
        post_click_wait_min=500, post_click_wait_max=3000,
        post_form_wait_min=1000, post_form_wait_max=5000,
        brief_idle_probability=0.2, medium_idle_probability=0.08,
        session_style="relaxed",
        interaction_frequency=2.0,
    ),
}


class BehaviourProfileCatalog:
    """Curated catalog of behaviour profiles."""

    @staticmethod
    def get(name: str) -> BehaviourProfile:
        """Get a profile by name. Returns 'normal' as default if not found."""
        return PROFILES.get(name, PROFILES["normal"])

    @staticmethod
    def list_names() -> list[str]:
        return sorted(PROFILES.keys())

    @staticmethod
    def all() -> list[BehaviourProfile]:
        return list(PROFILES.values())
