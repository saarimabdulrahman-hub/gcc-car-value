"""Recovery Manager — executes policies, coordinates retries, reports outcomes."""

import asyncio
import time
import structlog

from browser.challenge.models import (
    Challenge, RecoveryAction, RecoveryResult,
)
from browser.challenge.policies import PolicyEngine
from browser.challenge.errors import RecoveryExhaustedError

logger = structlog.get_logger()


class RecoveryManager:
    """Executes recovery actions for a detected challenge.

    Walks through the policy's action list in order, executing each action
    until one succeeds or all are exhausted. Does NOT implement bypass logic.

    Usage:
        recovery = RecoveryManager()
        result = await recovery.recover(challenge, session_id="s1")
        if result.success:
            print("Recovered!")
    """

    def __init__(self, policy_engine: PolicyEngine | None = None,
                 max_retries: int = 3, retry_delay: float = 5.0,
                 max_time: float = 120.0):
        self._policies = policy_engine or PolicyEngine()
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._max_time = max_time

    async def recover(self, challenge: Challenge, session_id: str = "",
                      marketplace: str = "",
                      on_action: callable | None = None) -> RecoveryResult:
        """Execute recovery actions until success or exhaustion.

        on_action: Optional async callback(action, attempt) called before each action.
        """
        start = time.monotonic()
        actions = self._policies.get_policy(challenge.challenge_type, marketplace)
        retry_count = 0

        for action in actions:
            if time.monotonic() - start > self._max_time:
                return RecoveryResult(
                    success=False, action=RecoveryAction.ABORT,
                    retry_count=retry_count, max_retries=self._max_retries,
                    final_challenge=challenge,
                    message="Recovery time exceeded",
                    duration_ms=(time.monotonic() - start) * 1000,
                )

            if on_action:
                try:
                    await on_action(action, retry_count)
                except Exception:
                    pass

            result = await self._execute(action, retry_count)

            if result.success:
                result.duration_ms = (time.monotonic() - start) * 1000
                return result

            retry_count = result.retry_count

        return RecoveryResult(
            success=False, action=RecoveryAction.ABORT,
            retry_count=retry_count, max_retries=self._max_retries,
            final_challenge=challenge,
            message=f"All {len(actions)} recovery actions exhausted",
            duration_ms=(time.monotonic() - start) * 1000,
        )

    async def _execute(self, action: RecoveryAction,
                       retry_count: int) -> RecoveryResult:
        """Execute a single recovery action."""
        if action == RecoveryAction.WAIT:
            await asyncio.sleep(self._retry_delay)
            return RecoveryResult(
                success=True, action=action, retry_count=retry_count,
                message="Waited before retry",
            )

        if action == RecoveryAction.RETRY:
            if retry_count >= self._max_retries:
                return RecoveryResult(
                    success=False, action=action,
                    retry_count=retry_count, max_retries=self._max_retries,
                    message="Max retries reached",
                )
            await asyncio.sleep(self._retry_delay)
            retry_count += 1
            return RecoveryResult(
                success=True, action=action,
                retry_count=retry_count, max_retries=self._max_retries,
                message=f"Retry {retry_count}/{self._max_retries}",
            )

        if action == RecoveryAction.REFRESH:
            return RecoveryResult(
                success=True, action=action,
                retry_count=retry_count,
                message="Page refreshed",
            )

        if action == RecoveryAction.RESTART_BROWSER:
            return RecoveryResult(
                success=True, action=action,
                retry_count=retry_count,
                message="Browser restarted (simulated)",
            )

        if action == RecoveryAction.RESTART_SESSION:
            return RecoveryResult(
                success=True, action=action,
                retry_count=retry_count,
                message="Session restarted (simulated)",
            )

        if action == RecoveryAction.ESCALATE:
            logger.warning("challenge_escalated",
                          retry_count=retry_count)
            return RecoveryResult(
                success=False, action=action,
                retry_count=retry_count,
                message="Escalated for manual review",
            )

        # ABORT
        return RecoveryResult(
            success=False, action=RecoveryAction.ABORT,
            retry_count=retry_count,
            message="Recovery aborted",
        )
