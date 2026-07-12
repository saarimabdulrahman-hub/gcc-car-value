"""Canary Deployment — incremental traffic increase with auto-rollback hooks."""

from ml.serving.config import ServingConfig


class CanaryController:
    def __init__(self, config: ServingConfig | None = None):
        self.config = config or ServingConfig()
        self._current_pct: dict[str, float] = {}
        self._stability: dict[str, float] = {}  # model_name → stable_since_ts

    def start(self, model_name: str,
              start_pct: float | None = None) -> float:
        pct = start_pct or self.config.canary_start_pct
        self._current_pct[model_name] = pct
        import time
        self._stability[model_name] = time.monotonic()
        return pct

    def increase(self, model_name: str,
                 increment: float | None = None) -> float:
        inc = increment or self.config.canary_increment
        current = self._current_pct.get(model_name, 0.0)
        new_pct = min(current + inc, 1.0)
        self._current_pct[model_name] = new_pct
        if new_pct >= 1.0:
            self.complete(model_name)
        return new_pct

    def complete(self, model_name: str) -> None:
        self._current_pct[model_name] = 0.0

    def should_rollback(self, model_name: str,
                        error_rate: float, threshold: float = 0.05) -> bool:
        """Auto-rollback if error rate exceeds threshold."""
        return error_rate > threshold

    def current_pct(self, model_name: str) -> float:
        return self._current_pct.get(model_name, 0.0)
