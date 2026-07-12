"""Challenge Manager — coordinates detection, classification, and recovery."""

import asyncio
import structlog

from browser.challenge.models import Challenge, ChallengeType, RecoveryResult
from browser.challenge.detector import ChallengeDetector
from browser.challenge.classifier import ChallengeClassifier
from browser.challenge.policies import PolicyEngine
from browser.challenge.recovery import RecoveryManager
from browser.challenge.config import ChallengeConfig

logger = structlog.get_logger()


class ChallengeManager:
    """Central coordinator for challenge detection and recovery.

    Usage:
        mgr = ChallengeManager()
        challenge = mgr.detect(html="<html>...", title="Access Denied")
        if challenge:
            result = await mgr.recover(challenge, session_id="s1")
    """

    def __init__(self, config: ChallengeConfig | None = None):
        self.config = config or ChallengeConfig()
        self._detector = ChallengeDetector()
        self._classifier = ChallengeClassifier()
        self._policies = PolicyEngine()
        self._recovery = RecoveryManager(
            policy_engine=self._policies,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay_seconds,
            max_time=self.config.max_recovery_time,
        )
        self._history: dict[str, list[Challenge]] = {}  # session_id → challenges
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect(self, html: str = "", title: str = "",
               url: str = "", http_status: int = 0,
               session_id: str = "") -> Challenge | None:
        """Detect a challenge from page signals."""
        challenge = self._detector.detect(
            html=html, title=title, url=url,
            http_status=http_status, session_id=session_id,
        )
        if challenge:
            challenge = self._classifier.classify(challenge)
        return challenge

    async def detect_and_record(self, html: str = "", title: str = "",
                                url: str = "", http_status: int = 0,
                                session_id: str = "") -> Challenge | None:
        """Detect and record in session history."""
        challenge = self.detect(
            html=html, title=title, url=url,
            http_status=http_status, session_id=session_id,
        )
        if challenge:
            async with self._lock:
                if session_id not in self._history:
                    self._history[session_id] = []
                self._history[session_id].append(challenge)
            logger.info("challenge_detected",
                       challenge_type=challenge.challenge_type.value,
                       confidence=challenge.confidence,
                       session_id=session_id[:8],
                       indicators=challenge.indicators)
        return challenge

    # ------------------------------------------------------------------
    # Recovery
    # ------------------------------------------------------------------

    async def recover(self, challenge: Challenge,
                      session_id: str = "",
                      marketplace: str = "") -> RecoveryResult:
        """Execute recovery actions for a detected challenge."""
        result = await self._recovery.recover(
            challenge, session_id=session_id,
            marketplace=marketplace,
        )
        logger.info("recovery_completed",
                   success=result.success,
                   action=result.action.value,
                   retries=result.retry_count)
        return result

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    async def get_history(self, session_id: str) -> list[Challenge]:
        async with self._lock:
            return list(self._history.get(session_id, []))

    async def clear_history(self, session_id: str) -> None:
        async with self._lock:
            self._history.pop(session_id, None)

    async def stats(self) -> dict:
        """Return challenge statistics across all sessions."""
        async with self._lock:
            all_challenges = [
                c for challenges in self._history.values()
                for c in challenges
            ]
        type_counts: dict[str, int] = {}
        for c in all_challenges:
            type_counts[c.challenge_type.value] = type_counts.get(c.challenge_type.value, 0) + 1
        return {
            "total_challenges": len(all_challenges),
            "type_distribution": type_counts,
        }
