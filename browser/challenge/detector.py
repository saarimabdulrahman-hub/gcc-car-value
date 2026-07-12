"""Challenge Detector — inspects page content for challenge indicators.

Detection is modular: each detector checks a specific signal (HTML, title,
URL, HTTP status) and returns a Challenge if a known pattern is found.
Detectors can be composed for layered detection.
"""

from __future__ import annotations

from browser.challenge.models import Challenge, ChallengeType, Severity


class ChallengeDetector:
    """Composite detector that runs all registered signal checks.

    Usage:
        detector = ChallengeDetector()
        challenge = detector.detect(
            html="<html>...", title="Access Denied",
            url="https://example.com/blocked", http_status=403,
        )
        if challenge:
            print(challenge.challenge_type)  # "access_denied"
    """

    def __init__(self):
        self._checks: list[callable] = [
            _check_html_indicators,
            _check_page_title,
            _check_url_patterns,
            _check_http_status,
        ]

    def detect(self, html: str = "", title: str = "",
               url: str = "", http_status: int = 0,
               session_id: str = "") -> Challenge | None:
        """Run all detection checks. Returns the highest-confidence Challenge found,
        or None if no challenge is detected."""
        best: Challenge | None = None

        for check in self._checks:
            result = check(html, title, url, http_status)
            if result and (best is None or result.confidence > best.confidence):
                best = result

        if best:
            best.url = url
            best.session_id = session_id

        return best


# ------------------------------------------------------------------
# Detection signal checks (each returns Challenge | None)
# ------------------------------------------------------------------

def _check_html_indicators(html: str, title: str, url: str,
                           http_status: int) -> Challenge | None:
    """Detect challenge patterns in HTML content."""
    if not html:
        return None
    html_lower = html.lower()

    # CAPTCHA indicators
    captcha_patterns = [
        "captcha", "recaptcha", "hcaptcha", "g-recaptcha",
        "cf-turnstile", "arkose", "funcaptcha",
    ]
    captcha_hits = [p for p in captcha_patterns if p in html_lower]
    if captcha_hits:
        return Challenge(
            challenge_type=ChallengeType.CAPTCHA,
            severity=Severity.HIGH, confidence=0.95,
            detector_name="html_captcha",
            indicators=captcha_hits,
        )

    # JavaScript challenge
    js_patterns = [
        "cf-browser-verify", "checking your browser",
        "enable javascript", "javascript is required",
        "ddos-guard", "sucuri",
    ]
    js_hits = [p for p in js_patterns if p in html_lower]
    if js_hits:
        return Challenge(
            challenge_type=ChallengeType.JAVASCRIPT_CHALLENGE,
            severity=Severity.HIGH, confidence=0.90,
            detector_name="html_js_challenge",
            indicators=js_hits,
        )

    # Security interstitial
    security_patterns = [
        "pardon our interruption", "security check",
        "verify you are human", "are you a robot",
        "unusual traffic", "automated access",
    ]
    sec_hits = [p for p in security_patterns if p in html_lower]
    if sec_hits:
        return Challenge(
            challenge_type=ChallengeType.SECURITY_INTERSTITIAL,
            severity=Severity.MEDIUM, confidence=0.85,
            detector_name="html_security",
            indicators=sec_hits,
        )

    return None


def _check_page_title(html: str, title: str, url: str,
                      http_status: int) -> Challenge | None:
    """Detect challenges from page title."""
    if not title:
        return None
    title_lower = title.lower()

    indicators = []
    if any(t in title_lower for t in ["access denied", "blocked", "forbidden"]):
        indicators.append("title_blocked")
    if any(t in title_lower for t in ["captcha", "verify", "challenge"]):
        indicators.append("title_challenge")
    if "rate limit" in title_lower:
        indicators.append("title_rate_limit")

    if not indicators:
        return None

    ctype = ChallengeType.ACCESS_DENIED
    if "captcha" in title_lower:
        ctype = ChallengeType.CAPTCHA
    elif "rate limit" in title_lower:
        ctype = ChallengeType.RATE_LIMITED

    return Challenge(
        challenge_type=ctype,
        severity=Severity.MEDIUM, confidence=0.70,
        detector_name="title",
        page_title=title,
        indicators=indicators,
    )


def _check_url_patterns(html: str, title: str, url: str,
                        http_status: int) -> Challenge | None:
    """Detect challenges from URL patterns."""
    if not url:
        return None
    url_lower = url.lower()

    indicators = []
    if any(p in url_lower for p in ["/blocked", "/captcha", "/challenge", "/verify"]):
        indicators.append("url_challenge_path")
    if "/429" in url or "rate-limit" in url_lower:
        indicators.append("url_rate_limit")

    if not indicators:
        return None

    return Challenge(
        challenge_type=ChallengeType.RATE_LIMITED if "rate" in url_lower
        else ChallengeType.UNKNOWN,
        severity=Severity.LOW, confidence=0.50,
        detector_name="url",
        indicators=indicators,
    )


def _check_http_status(html: str, title: str, url: str,
                       http_status: int) -> Challenge | None:
    """Detect challenges from HTTP status codes."""
    if http_status == 0:
        return None

    if http_status == 429:
        return Challenge(
            challenge_type=ChallengeType.RATE_LIMITED,
            severity=Severity.MEDIUM, confidence=0.90,
            detector_name="http_status",
            http_status=http_status,
            indicators=["status_429"],
        )
    if http_status == 403:
        return Challenge(
            challenge_type=ChallengeType.ACCESS_DENIED,
            severity=Severity.MEDIUM, confidence=0.80,
            detector_name="http_status",
            http_status=http_status,
            indicators=["status_403"],
        )
    if http_status == 503:
        return Challenge(
            challenge_type=ChallengeType.UNKNOWN,
            severity=Severity.LOW, confidence=0.50,
            detector_name="http_status",
            http_status=http_status,
            indicators=["status_503"],
        )
    return None
