"""Session policies — ephemeral, persistent, authenticated, guest, readonly, disposable."""

from browser.session.models import SessionPolicy


class SessionPolicies:
    """Central policy definitions. Each marketplace can be assigned a policy."""

    _marketplace_policies: dict[str, SessionPolicy] = {}

    @classmethod
    def set_policy(cls, marketplace: str, policy: SessionPolicy) -> None:
        cls._marketplace_policies[marketplace] = policy

    @classmethod
    def get_policy(cls, marketplace: str) -> SessionPolicy:
        return cls._marketplace_policies.get(marketplace, SessionPolicy.EPHEMERAL)

    @classmethod
    def is_reusable(cls, policy: SessionPolicy) -> bool:
        """Check if a session with this policy can be reused."""
        return policy in (SessionPolicy.PERSISTENT, SessionPolicy.AUTHENTICATED)
