from dataclasses import dataclass, field
from browser.challenge.models import RecoveryAction

@dataclass
class ChallengeConfig:
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    max_recovery_time: float = 120.0
    default_policy: list[RecoveryAction] = field(default_factory=lambda: [
        RecoveryAction.WAIT, RecoveryAction.RETRY,
        RecoveryAction.REFRESH, RecoveryAction.RESTART_BROWSER,
        RecoveryAction.RESTART_SESSION, RecoveryAction.ABORT,
    ])
