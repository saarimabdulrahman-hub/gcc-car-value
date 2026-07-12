"""Browser fingerprint data models."""

from dataclasses import dataclass, field
import uuid


@dataclass
class BrowserProfile:
    """A coherent browser identity. All fields must be internally consistent."""
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Browser
    browser_family: str = "Chrome"        # Chrome, Edge, Safari, Firefox
    browser_version: str = "131.0.0.0"

    # OS
    operating_system: str = "Windows"     # Windows, macOS, Linux
    operating_system_version: str = "10"
    architecture: str = "x64"

    # Locale
    locale: str = "en-AE"
    language: str = "en-US,en;q=0.9,ar;q=0.8"

    # Timezone
    timezone: str = "Asia/Dubai"
    country: str = "AE"

    # Screen
    viewport_width: int = 1920
    viewport_height: int = 1080
    screen_width: int = 1920
    screen_height: int = 1080
    color_depth: int = 24
    device_pixel_ratio: float = 1.0

    # Hardware
    hardware_concurrency: int = 8
    device_memory: int = 8              # GB

    # Capabilities
    touch_support: bool = False
    mobile: bool = False

    # Metadata
    platform: str = "Win32"
    description: str = ""

    @property
    def user_agent(self) -> str:
        """Generate a coherent User-Agent string."""
        if self.browser_family == "Chrome":
            return (
                f"Mozilla/5.0 ({self._os_ua_token}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{self.browser_version} Safari/537.36"
            )
        if self.browser_family == "Firefox":
            return (
                f"Mozilla/5.0 ({self._os_ua_token}; rv:{self.browser_version}) "
                f"Gecko/20100101 Firefox/{self.browser_version}"
            )
        return f"Mozilla/5.0 ({self._os_ua_token})"

    @property
    def _os_ua_token(self) -> str:
        if self.operating_system == "Windows":
            return f"Windows NT {self.operating_system_version}; Win64; x64"
        if self.operating_system == "macOS":
            return f"Macintosh; Intel Mac OS X {self.operating_system_version}"
        return f"X11; Linux {self.architecture}"

    @property
    def sec_ch_ua(self) -> str:
        """Sec-CH-UA header value."""
        return (
            f'"Chromium";v="{self.browser_version}", '
            f'"Google Chrome";v="{self.browser_version}", '
            f'"Not?A_Brand";v="99"'
        )

    @property
    def sec_ch_ua_platform(self) -> str:
        return f'"{self.operating_system}"'

    @property
    def sec_ch_ua_mobile(self) -> str:
        return "?1" if self.mobile else "?0"
