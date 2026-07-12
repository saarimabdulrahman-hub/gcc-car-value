"""Traffic Router — 100% active, weighted, canary, A/B, deterministic routing."""

import hashlib, random
from ml.serving.models import DeploymentRecord, ABExperiment


class TrafficRouter:
    """Routes prediction requests to the correct model version.

    Supports:
        - 100% active model
        - Weighted routing between models
        - Canary deployment (incremental %)
        - A/B testing (50/50 split)
        - Deterministic routing by request key (same key → same model)
    """

    def __init__(self):
        self._active: dict[str, str] = {}         # model_name → "model:v1"
        self._canary_pct: dict[str, float] = {}   # model_name → canary %
        self._rng = random.Random(42)

    def set_active(self, model_name: str, version_id: str) -> None:
        self._active[model_name] = version_id

    def set_canary(self, model_name: str, pct: float) -> None:
        self._canary_pct[model_name] = min(max(pct, 0.0), 1.0)

    def route(self, model_name: str,
              request_key: str = "",
              ab_experiment: ABExperiment | None = None) -> str:
        """Return which model version to use for this request.

        Priority: A/B experiment > canary > active.

        Args:
            model_name: Name of the model family.
            request_key: Deterministic key for stable routing.
            ab_experiment: Active A/B experiment (if any).

        Returns:
            Model version identifier string (e.g., "model:v2").
        """
        # 1. A/B testing: deterministic split based on request key
        if ab_experiment and ab_experiment.status == "running":
            if request_key:
                bucket = int(hashlib.md5(request_key.encode()).hexdigest()[:8], 16) % 100
            else:
                bucket = self._rng.randint(0, 99)

            if bucket < ab_experiment.traffic_split * 100:
                return ab_experiment.candidate_model
            return ab_experiment.control_model

        # 2. Canary: probabilistic routing
        canary = self._canary_pct.get(model_name, 0.0)
        if canary > 0:
            if request_key:
                bucket = int(hashlib.md5(request_key.encode()).hexdigest()[:8], 16) % 100
            else:
                bucket = self._rng.randint(0, 99)

            if bucket < canary * 100:
                active_id = self._active.get(model_name, "")
                return f"{active_id}-canary"

        # 3. Active model
        return self._active.get(model_name, f"{model_name}:default")
