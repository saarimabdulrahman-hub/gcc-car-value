"""Feedback Collector — attach actual selling price, corrections, ratings."""

import threading, time
from ml.inference.models import PredictionFeedback


class FeedbackCollector:
    def __init__(self):
        self._feedback: dict[str, PredictionFeedback] = {}
        self._lock = threading.Lock()

    def attach(self, prediction_id: str, **kwargs) -> PredictionFeedback:
        fb = PredictionFeedback(prediction_id=prediction_id, **kwargs)
        fb.received_at = time.time()
        fb.status = "received"
        with self._lock:
            self._feedback[prediction_id] = fb
        return fb

    def get(self, prediction_id: str) -> PredictionFeedback | None:
        with self._lock:
            return self._feedback.get(prediction_id)

    def count(self) -> int:
        with self._lock: return len(self._feedback)

    def list_pending(self) -> list[PredictionFeedback]:
        with self._lock:
            return [f for f in self._feedback.values() if f.status == "pending"]
