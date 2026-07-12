"""Audit Store — immutable prediction audit records."""

import threading
from ml.inference.models import AuditRecord, PredictionFeedback


class AuditStore:
    """Immutable store for prediction audit records. Thread-safe."""

    def __init__(self):
        self._records: dict[str, AuditRecord] = {}
        self._lock = threading.Lock()

    def save(self, record: AuditRecord) -> None:
        with self._lock:
            self._records[record.prediction_id] = record

    def get(self, prediction_id: str) -> AuditRecord | None:
        with self._lock:
            return self._records.get(prediction_id)

    def count(self) -> int:
        with self._lock: return len(self._records)

    def list_by_model(self, model_name: str) -> list[AuditRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.model_name == model_name]

    def recent(self, limit: int = 100) -> list[AuditRecord]:
        with self._lock:
            sorted_recs = sorted(self._records.values(),
                               key=lambda r: r.timestamp, reverse=True)
            return sorted_recs[:limit]
