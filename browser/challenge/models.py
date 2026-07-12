"""Challenge detection models."""

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class ChallengeType(StrEnum):
    CAPTCHA = "captcha"
    SECURITY_INTERSTITIAL = "security_interstitial"
    ACCESS_DENIED = "access_denied"
    RATE_LIMITED = "rate_limited"
    JAVASCRIPT_CHALLENGE = "javascript_challenge"
    UNKNOWN = "unknown"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(StrEnum):
    RETRY = "retry"
    WAIT = "wait"
    REFRESH = "refresh"
    RESTART_BROWSER = "restart_browser"
    RESTART_SESSION = "restart_session"
    ESCALATE = "escalate"
    ABORT = "abort"


@dataclass
class Challenge:
    """A detected browser challenge."""
    challenge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    challenge_type: ChallengeType = ChallengeType.UNKNOWN
    severity: Severity = Severity.MEDIUM
    confidence: float = 0.0          # 0.0-1.0
    detected_at: float = field(default_factory=time.time)
    url: str = ""
    session_id: str = ""
    detector_name: str = ""
    page_title: str = ""
    http_status: int = 0
    indicators: list[str] = field(default_factory=list)  # Which patterns matched
    metadata: dict = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Outcome of a recovery attempt."""
    success: bool = False
    action: RecoveryAction = RecoveryAction.ABORT
    retry_count: int = 0
    max_retries: int = 3
    final_challenge: Challenge | None = None
    message: str = ""
    duration_ms: float = 0.0
