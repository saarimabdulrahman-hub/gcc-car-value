"""Playwright Chromium driver configuration."""

from dataclasses import dataclass, field


@dataclass
class PlaywrightChromiumConfig:
    """Configuration for launching Chromium via Playwright."""
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    locale: str = "en-AE"
    timezone: str = "Asia/Dubai"
    proxy: str | None = None
    downloads_path: str | None = None
    user_data_dir: str | None = None
    ignore_https_errors: bool = False   # Only enable for dev/staging with self-signed certs
    args: list[str] = field(default_factory=lambda: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ])
    permissions: list[str] = field(default_factory=list)
    extra_launch_options: dict = field(default_factory=dict)
