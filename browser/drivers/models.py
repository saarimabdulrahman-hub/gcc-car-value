"""Driver data models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DriverCapabilities:
    """What a browser driver supports."""
    browser_type: str = ""         # chromium, firefox, webkit
    headless: bool = True
    extensions: bool = False
    downloads: bool = True
    screenshots: bool = True
    pdf: bool = False
    video: bool = False
    har_recording: bool = False
    tracing: bool = False
    proxy_support: bool = True
    mobile_emulation: bool = False
    geolocation: bool = False
    permissions: bool = False
    network_interception: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class DriverInfo:
    """Metadata about a registered driver."""
    name: str
    version: str = "0.0.0"
    browser_type: str = ""
    capabilities: DriverCapabilities = field(default_factory=DriverCapabilities)
    healthy: bool = True
    launch_count: int = 0
    crash_count: int = 0
