"""Monitoring data models — drift events, alerts, reports."""

from dataclasses import dataclass, field
from enum import StrEnum
import time


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    RETRAINING_RECOMMENDED = "retraining_recommended"
    MODEL_DEGRADED = "model_degraded"
    DATA_QUALITY = "data_quality"


class DriftType(StrEnum):
    FEATURE = "feature"
    MODEL = "model"
    DATA_QUALITY = "data_quality"
    PERFORMANCE = "performance"


@dataclass
class DriftEvent:
    """A detected drift event."""
    event_id: str = ""
    drift_type: DriftType = DriftType.FEATURE
    feature_name: str = ""
    model_name: str = ""
    alert_level: AlertLevel = AlertLevel.INFO
    metric: str = ""
    baseline_value: float = 0.0
    current_value: float = 0.0
    threshold: float = 0.0
    detected_at: float = field(default_factory=time.time)
    details: str = ""


@dataclass
class Alert:
    """A generated alert."""
    alert_id: str = ""
    level: AlertLevel = AlertLevel.INFO
    title: str = ""
    message: str = ""
    generated_at: float = field(default_factory=time.time)
    acknowledged: bool = False


@dataclass
class MonitoringReport:
    """A monitoring run report."""
    report_id: str = ""
    report_type: str = "daily"     # daily, weekly, monthly
    generated_at: float = field(default_factory=time.time)
    total_predictions: int = 0
    alerts: list[Alert] = field(default_factory=list)
    drift_events: list[DriftEvent] = field(default_factory=list)
    retraining_recommended: bool = False
    retraining_reason: str = ""
    model_health_score: float = 100.0
    feature_drift_summary: dict = field(default_factory=dict)
