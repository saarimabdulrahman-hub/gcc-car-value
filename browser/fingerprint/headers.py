"""Generate coherent HTTP headers for a BrowserProfile."""

from browser.fingerprint.models import BrowserProfile


def generate_headers(profile: BrowserProfile) -> dict[str, str]:
    """Generate a complete set of HTTP headers matching the profile.

    All headers are consistent with the profile's browser family, version,
    OS, locale, and platform. Used when creating Playwright contexts.
    """
    return {
        "User-Agent": profile.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": profile.language,
        "Sec-CH-UA": profile.sec_ch_ua,
        "Sec-CH-UA-Mobile": profile.sec_ch_ua_mobile,
        "Sec-CH-UA-Platform": profile.sec_ch_ua_platform,
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
    }


def generate_client_hints(profile: BrowserProfile) -> dict[str, str]:
    """Generate only the Client Hints headers."""
    return {
        "Sec-CH-UA": profile.sec_ch_ua,
        "Sec-CH-UA-Mobile": profile.sec_ch_ua_mobile,
        "Sec-CH-UA-Platform": profile.sec_ch_ua_platform,
    }
