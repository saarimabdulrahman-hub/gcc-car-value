"""Model Server — unified serving interface. Deploy, route, predict, monitor."""

from ml.training.registry import ModelRegistry
from ml.serving.model_loader import ModelLoader
from ml.serving.predictor import Predictor
from ml.serving.router import TrafficRouter
from ml.serving.deployment import DeploymentManager
from ml.serving.cache import PredictionCache
from ml.serving.monitor import ServingMonitor
from ml.serving.ab_testing import ABTesting
from ml.serving.models import PredictionResult, ABExperiment
from ml.serving.config import ServingConfig
from ml.serving.errors import ModelNotLoadedError


class ModelServer:
    """Production model server — deploys, routes, and serves predictions.

    Usage:
        server = ModelServer(training_registry)
        server.deploy("lightgbm_v2", version=1)
        result = server.predict("lightgbm_v2", {"mileage_km": 50000, "year": 2020})
    """

    def __init__(self, training_registry: ModelRegistry,
                 config: ServingConfig | None = None):
        self.config = config or ServingConfig()
        self._training_registry = training_registry
        self._loader = ModelLoader(training_registry)
        self._cache = PredictionCache(self.config.cache_ttl_seconds, self.config.cache_max_size)
        self._predictor = Predictor(self._loader, self._cache)
        self._router = TrafficRouter()
        self._deployment = DeploymentManager()
        self._monitor = ServingMonitor()
        self._ab = ABTesting()

    # ------------------------------------------------------------------
    # Deployment
    # ------------------------------------------------------------------

    def deploy(self, model_name: str, version: int | None = None) -> str:
        """Deploy a model version. Activates at 100% traffic."""
        entry = self._training_registry.get(model_name, version)
        if entry is None: raise ModelNotLoadedError(model_name)

        dep_id = self._deployment.deploy(model_name, entry.version)
        version_id = f"{model_name}:v{entry.version}"
        self._router.set_active(model_name, version_id)
        return dep_id

    def rollback(self, model_name: str, reason: str = "") -> str:
        """Rollback to the previous active model."""
        self._training_registry.rollback(model_name, reason)
        entry = self._training_registry.get(model_name)
        if entry:
            version_id = f"{model_name}:v{entry.version}"
            self._router.set_active(model_name, version_id)
            self._loader.reload(model_name)
        return self._deployment.rollback(model_name, reason)

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, model_name: str, features: dict,
                cache_key: str = "",
                ab_experiment: ABExperiment | None = None) -> PredictionResult:
        """Serve a prediction through the active model."""
        start_ts = __import__('time').perf_counter()

        try:
            result = self._predictor.predict(model_name, features, cache_key)
            self._monitor.record_prediction(model_name, result.latency_ms)
        except Exception as e:
            self._monitor.record_error(model_name)
            raise

        return result

    # ------------------------------------------------------------------
    # A/B Testing
    # ------------------------------------------------------------------

    def start_ab(self, control_model: str, candidate_model: str,
                 traffic_split: float = 0.5) -> ABExperiment:
        return self._ab.start(control_model, candidate_model, traffic_split)

    def complete_ab(self, experiment_id: str,
                    winner: str = "") -> ABExperiment:
        return self._ab.complete(experiment_id, winner)

    # ------------------------------------------------------------------
    # Canary
    # ------------------------------------------------------------------

    def start_canary(self, model_name: str,
                     start_pct: float | None = None) -> None:
        pct = start_pct or self.config.canary_start_pct
        self._router.set_canary(model_name, pct)

    def increase_canary(self, model_name: str,
                        increment: float | None = None) -> float:
        inc = increment or self.config.canary_increment
        current = self._router._canary_pct.get(model_name, 0.0)
        new_pct = min(current + inc, 1.0)
        self._router.set_canary(model_name, new_pct)
        if new_pct >= 1.0:
            self._router.set_canary(model_name, 0.0)  # Canary complete
        return new_pct

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    @property
    def monitor(self) -> dict: return self._monitor.snapshot()

    @property
    def cache_stats(self) -> dict:
        return {"hit_rate": self._cache.hit_rate, "size": self._cache.size()}
