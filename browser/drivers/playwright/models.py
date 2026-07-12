"""Playwright driver data models."""

from dataclasses import dataclass, field


@dataclass
class PlaywrightSession:
    """Tracks a Playwright browser session for health and metrics."""
    browser_type: str = "chromium"
    launch_ms: float = 0.0
    context_count: int = 0
    page_count: int = 0
    crash_count: int = 0
    healthy: bool = True
