"""Alert Engine — generate alerts at INFO/WARNING/CRITICAL levels."""

import uuid
from ml.monitoring.models import Alert, AlertLevel, DriftEvent


class AlertEngine:
    def __init__(self): self._alerts: list[Alert] = []

    def from_drift(self, event: DriftEvent) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4())[:12],
            level=event.alert_level,
            title=f"{event.drift_type.value}_drift",
            message=event.details,
        )
        self._alerts.append(alert)
        return alert

    def info(self, title: str, message: str) -> Alert:
        a = Alert(alert_id=str(uuid.uuid4())[:12], level=AlertLevel.INFO,
                  title=title, message=message)
        self._alerts.append(a); return a

    def warning(self, title: str, message: str) -> Alert:
        a = Alert(alert_id=str(uuid.uuid4())[:12], level=AlertLevel.WARNING,
                  title=title, message=message)
        self._alerts.append(a); return a

    def critical(self, title: str, message: str) -> Alert:
        a = Alert(alert_id=str(uuid.uuid4())[:12], level=AlertLevel.CRITICAL,
                  title=title, message=message)
        self._alerts.append(a); return a

    def list_all(self) -> list[Alert]: return list(self._alerts)

    def list_by_level(self, level: AlertLevel) -> list[Alert]:
        return [a for a in self._alerts if a.level == level]
