from dataclasses import dataclass, field

@dataclass
class LifecycleConfig:
    min_retraining_interval_hours: float = 24.0
    approval_required: bool = True
    canary_required: bool = True
    canary_stable_period_seconds: float = 300.0
    auto_rollback_on_canary_failure: bool = True
    auto_rollback_on_monitoring_alert: bool = False
    cooldown_after_rollback_hours: float = 12.0
    max_concurrent_workflows: int = 3
