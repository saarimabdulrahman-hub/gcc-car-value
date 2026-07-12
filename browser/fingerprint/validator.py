"""Fingerprint Validator — reject impossible profile combinations."""

from browser.fingerprint.models import BrowserProfile
from browser.fingerprint.errors import InconsistentProfileError

# Known-valid OS + browser family combinations
VALID_COMBINATIONS = {
    ("Windows", "Chrome"), ("Windows", "Edge"), ("Windows", "Firefox"),
    ("macOS", "Chrome"), ("macOS", "Safari"), ("macOS", "Firefox"),
    ("Linux", "Chrome"), ("Linux", "Firefox"),
}

# Timezone → country mapping (enforces locale/timezone consistency)
COUNTRY_TIMEZONES: dict[str, list[str]] = {
    "AE": ["Asia/Dubai"],
    "SA": ["Asia/Riyadh"],
    "KW": ["Asia/Kuwait"],
    "QA": ["Asia/Qatar"],
    "BH": ["Asia/Bahrain"],
    "OM": ["Asia/Muscat"],
}

# Country → expected locale prefix
COUNTRY_LOCALES: dict[str, list[str]] = {
    "AE": ["en-AE", "ar-AE"],
    "SA": ["ar-SA", "en-SA"],
    "KW": ["en-KW", "ar-KW"],
    "QA": ["en-QA", "ar-QA"],
    "BH": ["en-BH", "ar-BH"],
    "OM": ["en-OM", "ar-OM"],
}


class FingerprintValidator:
    """Validate BrowserProfiles for internal consistency."""

    def validate(self, profile: BrowserProfile) -> list[str]:
        """Return list of validation errors. Empty list = valid."""
        errors = []

        # OS + browser family
        combo = (profile.operating_system, profile.browser_family)
        if combo not in VALID_COMBINATIONS:
            errors.append(
                f"Invalid OS/browser: {profile.operating_system} + {profile.browser_family}"
            )

        # Screen dimensions cannot exceed viewport
        if profile.viewport_width > profile.screen_width:
            errors.append("Viewport width exceeds screen width")
        if profile.viewport_height > profile.screen_height:
            errors.append("Viewport height exceeds screen height")

        # Mobile has touch
        if profile.mobile and not profile.touch_support:
            errors.append("Mobile device must have touch support")

        # Color depth
        if profile.color_depth not in (24, 30, 32):
            errors.append(f"Invalid color depth: {profile.color_depth}")

        # Timezone must match country
        valid_zones = COUNTRY_TIMEZONES.get(profile.country, [])
        if valid_zones and profile.timezone not in valid_zones:
            errors.append(
                f"Timezone '{profile.timezone}' does not match country '{profile.country}'. "
                f"Expected: {valid_zones}"
            )

        # Locale must match country
        valid_locales = COUNTRY_LOCALES.get(profile.country, [])
        if valid_locales:
            locale_match = any(
                profile.locale.startswith(prefix) for prefix in valid_locales
            )
            if not locale_match:
                errors.append(
                    f"Locale '{profile.locale}' does not match country '{profile.country}'"
                )

        # Device memory
        if profile.device_memory not in (2, 4, 8, 16, 32):
            errors.append(f"Unrealistic device memory: {profile.device_memory}GB")

        # Hardware concurrency
        if profile.hardware_concurrency < 1 or profile.hardware_concurrency > 64:
            errors.append(f"Unrealistic hardware concurrency: {profile.hardware_concurrency}")

        return errors

    def validate_or_raise(self, profile: BrowserProfile) -> None:
        errors = self.validate(profile)
        if errors:
            raise InconsistentProfileError("; ".join(errors))
