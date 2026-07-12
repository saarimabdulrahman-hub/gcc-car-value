"""Report Generator — daily, weekly, monthly reports."""

import time, uuid
from ml.monitoring.models import MonitoringReport, Alert, DriftEvent


class ReportGenerator:
    def __init__(self): self._reports: list[MonitoringReport] = []

    def generate(self, report_type: str = "daily",
                 total_predictions: int = 0,
                 alerts: list[Alert] | None = None,
                 drift_events: list[DriftEvent] | None = None,
                 retraining_recommended: bool = False,
                 retraining_reason: str = "",
                 model_health_score: float = 100.0,
                 ) -> MonitoringReport:
        report = MonitoringReport(
            report_id=str(uuid.uuid4())[:12],
            report_type=report_type,
            total_predictions=total_predictions,
            alerts=alerts or [],
            drift_events=drift_events or [],
            retraining_recommended=retraining_recommended,
            retraining_reason=retraining_reason,
            model_health_score=model_health_score,
        )
        self._reports.append(report)
        return report

    def latest(self) -> MonitoringReport | None:
        return self._reports[-1] if self._reports else None

    def list_all(self) -> list[MonitoringReport]:
        return list(self._reports)
