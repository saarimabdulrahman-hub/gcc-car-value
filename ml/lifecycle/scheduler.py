"""Retraining Scheduler — manual, cron, recommendation trigger, cooldown, dedup."""

import time
from ml.lifecycle.config import LifecycleConfig
from ml.lifecycle.models import TriggerSource


class RetrainingScheduler:
    def __init__(self, config: LifecycleConfig | None = None):
        self.config = config or LifecycleConfig()
        self._last_trigger: float = 0.0
        self._active_count = 0

    def should_trigger(self, trigger: TriggerSource,
                       max_concurrent: int | None = None) -> tuple[bool, str]:
        """Check if a new workflow should be triggered."""
        max_cc = max_concurrent or self.config.max_concurrent_workflows

        # Concurrent limit
        if self._active_count >= max_cc:
            return False, f"Max concurrent workflows ({max_cc}) reached"

        # Cooldown
        if trigger in (TriggerSource.SCHEDULED, TriggerSource.DRIFT_ALERT):
            elapsed_hours = (time.time() - self._last_trigger) / 3600
            if self._last_trigger > 0 and elapsed_hours < self.config.min_retraining_interval_hours:
                remaining = self.config.min_retraining_interval_hours - elapsed_hours
                return False, f"Cooldown: {remaining:.1f}h remaining"

        return True, "Ready"

    def record_trigger(self) -> None:
        self._last_trigger = time.time()

    def increment_active(self) -> None: self._active_count += 1
    def decrement_active(self) -> None: self._active_count = max(0, self._active_count - 1)

    @property
    def active_count(self) -> int: return self._active_count
