"""Fingerprint Catalog — curated, internally consistent browser profiles.

Profiles are organized by country. Each profile has matching OS, browser,
locale, timezone, and screen properties. No random generation — all
profiles are pre-defined and validated.
"""

from browser.fingerprint.models import BrowserProfile


# ------------------------------------------------------------------
# GCC-Curated Profiles
# ------------------------------------------------------------------

CATALOG: list[BrowserProfile] = [
    # --- UAE ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="en-AE", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Dubai", country="AE",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=8,
        platform="Win32",
        description="UAE — Windows 10 Chrome (Desktop 1080p)",
    ),
    BrowserProfile(
        browser_family="Chrome", browser_version="130.0.0.0",
        operating_system="macOS", operating_system_version="14.7",
        locale="en-AE", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Dubai", country="AE",
        viewport_width=1680, viewport_height=1050,
        screen_width=1680, screen_height=1050,
        hardware_concurrency=10, device_memory=16,
        platform="MacIntel",
        description="UAE — macOS Sonoma Chrome (MacBook Pro)",
    ),
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="en-AE", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Dubai", country="AE",
        viewport_width=2560, viewport_height=1440,
        screen_width=2560, screen_height=1440,
        hardware_concurrency=16, device_memory=32,
        platform="Win32",
        description="UAE — Windows 10 Chrome (Desktop 1440p)",
    ),

    # --- Saudi Arabia ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="ar-SA", language="ar,en-US;q=0.9,en;q=0.8",
        timezone="Asia/Riyadh", country="SA",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=8,
        platform="Win32",
        description="Saudi Arabia — Windows 10 Chrome Arabic",
    ),
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="macOS", operating_system_version="15.0",
        locale="ar-SA", language="ar,en-US;q=0.9,en;q=0.8",
        timezone="Asia/Riyadh", country="SA",
        viewport_width=1728, viewport_height=1117,
        screen_width=1728, screen_height=1117,
        hardware_concurrency=10, device_memory=16,
        platform="MacIntel",
        description="Saudi Arabia — macOS Sequoia Chrome Arabic",
    ),

    # --- Kuwait ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="11",
        locale="en-KW", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Kuwait", country="KW",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=16,
        platform="Win32",
        description="Kuwait — Windows 11 Chrome",
    ),

    # --- Qatar ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="en-QA", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Qatar", country="QA",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=16,
        platform="Win32",
        description="Qatar — Windows 10 Chrome",
    ),

    # --- Bahrain ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="en-BH", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Bahrain", country="BH",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=8,
        platform="Win32",
        description="Bahrain — Windows 10 Chrome",
    ),

    # --- Oman ---
    BrowserProfile(
        browser_family="Chrome", browser_version="131.0.0.0",
        operating_system="Windows", operating_system_version="10",
        locale="en-OM", language="en-US,en;q=0.9,ar;q=0.8",
        timezone="Asia/Muscat", country="OM",
        viewport_width=1920, viewport_height=1080,
        screen_width=1920, screen_height=1080,
        hardware_concurrency=8, device_memory=8,
        platform="Win32",
        description="Oman — Windows 10 Chrome",
    ),
]


class FingerprintCatalog:
    """Curated catalog of pre-defined browser profiles.

    Usage:
        catalog = FingerprintCatalog()
        profile = catalog.get_by_country("AE")
        profiles = catalog.list_by_country("SA")
    """

    def __init__(self):
        self._profiles: list[BrowserProfile] = list(CATALOG)

    def get_by_country(self, country: str) -> BrowserProfile | None:
        for p in self._profiles:
            if p.country == country:
                return p
        return None

    def list_by_country(self, country: str) -> list[BrowserProfile]:
        return [p for p in self._profiles if p.country == country]

    def get_by_id(self, profile_id: str) -> BrowserProfile | None:
        for p in self._profiles:
            if p.profile_id == profile_id:
                return p
        return None

    def list_all(self) -> list[BrowserProfile]:
        return list(self._profiles)

    def add(self, profile: BrowserProfile) -> None:
        self._profiles.append(profile)

    def count_by_country(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for p in self._profiles:
            counts[p.country] = counts.get(p.country, 0) + 1
        return counts
