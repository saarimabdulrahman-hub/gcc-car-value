"""Browser configuration and session models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrowserConfig:
    """Configuration for a browser instance."""
    headless: bool = True
    viewport: dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    timezone: str = "Asia/Dubai"
    locale: str = "en-AE"
    language: str = "en-US"
    proxy: str | None = None
    downloads_path: str | None = None
    cache_enabled: bool = True
    user_data_dir: str | None = None
    permissions: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationOptions:
    """Options for page navigation."""
    timeout: float = 30.0
    wait_until: str = "load"  # load | domcontentloaded | networkidle
    referer: str | None = None


@dataclass
class ScreenshotOptions:
    """Options for page screenshots."""
    full_page: bool = False
    clip: dict[str, float] | None = None
    type: str = "png"  # png | jpeg
    quality: int = 80   # jpeg only


@dataclass
class DownloadInfo:
    """Information about a downloaded file."""
    url: str = ""
    suggested_filename: str = ""
    path: str = ""
    size_bytes: int = 0
    mime_type: str = ""
