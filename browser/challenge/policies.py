"""Policy Engine — configurable recovery strategies per challenge type and marketplace."""

from browser.challenge.models import ChallengeType, RecoveryAction


class PolicyEngine:
    """Maps challenge types to recovery action sequences.

    Usage:
        engine = PolicyEngine()
        actions = engine.get_policy(ChallengeType.CAPTCHA)
        # → [WAIT, RETRY, RESTART_BROWSER, RESTART_SESSION, ABORT]
    """

    def __init__(self):
        self._policies: dict[ChallengeType, list[RecoveryAction]] = _default_policies()
        self._marketplace_overrides: dict[str, dict[ChallengeType, list[RecoveryAction]]] = {}

    def get_policy(self, challenge_type: ChallengeType,
                   marketplace: str = "") -> list[RecoveryAction]:
        """Return the ordered list of recovery actions for this challenge type."""
        if marketplace and marketplace in self._marketplace_overrides:
            mp = self._marketplace_overrides[marketplace]
            if challenge_type in mp:
                return list(mp[challenge_type])
        return list(self._policies.get(challenge_type, [RecoveryAction.ABORT]))

    def set_policy(self, challenge_type: ChallengeType,
                   actions: list[RecoveryAction],
                   marketplace: str = "") -> None:
        """Set a custom policy for a challenge type (optionally per marketplace)."""
        if marketplace:
            if marketplace not in self._marketplace_overrides:
                self._marketplace_overrides[marketplace] = {}
            self._marketplace_overrides[marketplace][challenge_type] = list(actions)
        else:
            self._policies[challenge_type] = list(actions)

    def list_policies(self, marketplace: str = "") -> dict[str, list[str]]:
        policies = self._marketplace_overrides.get(marketplace, {}) if marketplace else self._policies
        return {k.value: [a.value for a in v] for k, v in policies.items()}


def _default_policies() -> dict[ChallengeType, list[RecoveryAction]]:
    return {
        ChallengeType.CAPTCHA: [
            RecoveryAction.WAIT, RecoveryAction.RETRY,
            RecoveryAction.REFRESH, RecoveryAction.RESTART_BROWSER,
            RecoveryAction.RESTART_SESSION, RecoveryAction.ESCALATE,
            RecoveryAction.ABORT,
        ],
        ChallengeType.JAVASCRIPT_CHALLENGE: [
            RecoveryAction.WAIT, RecoveryAction.RETRY,
            RecoveryAction.REFRESH, RecoveryAction.RESTART_SESSION,
            RecoveryAction.ABORT,
        ],
        ChallengeType.ACCESS_DENIED: [
            RecoveryAction.RETRY, RecoveryAction.RESTART_SESSION,
            RecoveryAction.ESCALATE, RecoveryAction.ABORT,
        ],
        ChallengeType.RATE_LIMITED: [
            RecoveryAction.WAIT, RecoveryAction.WAIT,
            RecoveryAction.RETRY, RecoveryAction.ESCALATE,
        ],
        ChallengeType.SECURITY_INTERSTITIAL: [
            RecoveryAction.WAIT, RecoveryAction.RETRY,
            RecoveryAction.RESTART_SESSION, RecoveryAction.ESCALATE,
            RecoveryAction.ABORT,
        ],
        ChallengeType.UNKNOWN: [
            RecoveryAction.RETRY, RecoveryAction.RESTART_BROWSER,
            RecoveryAction.ESCALATE, RecoveryAction.ABORT,
        ],
    }
