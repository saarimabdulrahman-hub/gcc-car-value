"""Challenge Classifier — categorizes detected challenges with confidence scoring."""

from browser.challenge.models import Challenge, ChallengeType, Severity


class ChallengeClassifier:
    """Classify a detected challenge with additional context.

    Can refine classification based on marketplace-specific knowledge.
    Extend by registering custom classification rules.
    """

    def __init__(self):
        self._rules: list[callable] = []

    def classify(self, challenge: Challenge, context: dict | None = None) -> Challenge:
        """Refine classification with additional rules. Returns the challenge
        (possibly with updated type/confidence)."""
        ctx = context or {}
        for rule in self._rules:
            challenge = rule(challenge, ctx)
        return challenge

    def add_rule(self, rule: callable) -> None:
        """Register a custom classification rule.

        A rule is a function: (Challenge, dict) -> Challenge
        """
        self._rules.append(rule)


def classify_severity(challenge: Challenge) -> Severity:
    """Map challenge type to default severity."""
    severity_map = {
        ChallengeType.CAPTCHA: Severity.HIGH,
        ChallengeType.JAVASCRIPT_CHALLENGE: Severity.HIGH,
        ChallengeType.ACCESS_DENIED: Severity.MEDIUM,
        ChallengeType.RATE_LIMITED: Severity.MEDIUM,
        ChallengeType.SECURITY_INTERSTITIAL: Severity.MEDIUM,
        ChallengeType.UNKNOWN: Severity.LOW,
    }
    return severity_map.get(challenge.challenge_type, Severity.MEDIUM)
