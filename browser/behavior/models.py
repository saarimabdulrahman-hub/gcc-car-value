"""Behaviour data models."""

from dataclasses import dataclass, field
import uuid


@dataclass
class BehaviourProfile:
    """A human-like interaction profile. All timings in milliseconds."""

    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "default"

    # Typing (ms)
    typing_speed_min: int = 80      # Min ms between keystrokes
    typing_speed_max: int = 200     # Max ms between keystrokes
    typing_variance: float = 0.3    # Random variance factor (0-1)

    # Scrolling (ms)
    scroll_step_px: int = 300       # Pixels per scroll step
    scroll_pause_min: int = 200     # Min ms between scrolls
    scroll_pause_max: int = 800     # Max ms between scrolls

    # Mouse (ms)
    mouse_move_min: int = 100       # Min ms for mouse movement
    mouse_move_max: int = 400       # Max ms for mouse movement
    hover_delay_min: int = 100      # Min ms before click after hover
    hover_delay_max: int = 300      # Max ms before click after hover

    # Reading (ms per 1000px of scrollable height)
    reading_speed_ms_per_1k: int = 3000   # 3s per 1000px of content
    reading_variance: float = 0.5

    # Navigation (ms)
    page_settle_min: int = 500      # Min ms after page load
    page_settle_max: int = 2000     # Max ms after page load
    post_click_wait_min: int = 300
    post_click_wait_max: int = 1500
    post_form_wait_min: int = 500
    post_form_wait_max: int = 2000

    # Idle (%)
    brief_idle_probability: float = 0.1   # 10% chance of 1-5s idle
    brief_idle_min: int = 1000
    brief_idle_max: int = 5000
    medium_idle_probability: float = 0.02  # 2% chance of 5-30s idle
    medium_idle_min: int = 5000
    medium_idle_max: int = 30000

    # Session style
    session_style: str = "normal"   # normal, fast, thorough, relaxed
    interaction_frequency: float = 1.0  # Multiplier for all timings
