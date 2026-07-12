"""Client Hints — generate consistent Sec-CH-UA headers matching the profile."""

from browser.fingerprint.models import BrowserProfile


def build_client_hints_headers(profile: BrowserProfile) -> dict[str, str]:
    """Generate all Client Hints headers for a profile."""
    return {
        "Sec-CH-UA": profile.sec_ch_ua,
        "Sec-CH-UA-Mobile": profile.sec_ch_ua_mobile,
        "Sec-CH-UA-Platform": profile.sec_ch_ua_platform,
    }


def validate_client_hints_consistency(profile: BrowserProfile) -> list[str]:
    """Check that Client Hints are internally consistent with the profile."""
    errors = []
    if profile.browser_family == "Chrome":
        if "Chromium" not in profile.sec_ch_ua:
            errors.append("Chrome profile must include 'Chromium' in Sec-CH-UA")
    if profile.mobile and profile.sec_ch_ua_mobile != "?1":
        errors.append("Mobile profile must have Sec-CH-UA-Mobile=?1")
    if not profile.mobile and profile.sec_ch_ua_mobile != "?0":
        errors.append("Desktop profile must have Sec-CH-UA-Mobile=?0")
    return errors
