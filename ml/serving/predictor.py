"""Predictor — serves predictions from loaded models with caching and fallback."""

import time
from ml.serving.model_loader import ModelLoader
from ml.serving.cache import PredictionCache
from ml.serving.models import PredictionResult


class Predictor:
    """Core prediction engine — model.predict() with caching and fallback."""

    def __init__(self, loader: ModelLoader,
                 cache: PredictionCache | None = None):
        self._loader = loader
        self._cache = cache or PredictionCache()
        self._fallback_fn = None          # Optional: callable when model fails

    def set_fallback(self, fn) -> None:
        self._fallback_fn = fn

    def predict(self, model_name: str, features: dict,
                cache_key: str = "") -> PredictionResult:
        """Run prediction through the active model.

        Args:
            model_name: Registered model name.
            features: Feature dict for prediction.
            cache_key: Optional cache key for result reuse.
        """
        start = time.perf_counter()

        # Check cache
        if cache_key:
            cached = self._cache.get(cache_key)
            if cached: return cached

        result = None
        fallback_used = False

        try:
            model = self._loader.get_active_model(model_name)
            meta = self._loader.get_metadata(model_name)

            # Convert features to X array
            feat_cols = meta.feature_names if meta else list(features.keys())
            X = [[features.get(c, 0.0) for c in feat_cols]]

            prediction = float(model.predict(X)[0]) if hasattr(model, 'predict') else 0.0

            result = PredictionResult(
                prediction=prediction,
                model_version=f"{model_name}:v{meta.version if meta else '?'}",
                model_name=model_name,
                experiment_id=meta.experiment_id if meta else "",
                latency_ms=(time.perf_counter() - start) * 1000,
                feature_schema_version=meta.version if meta else 0,
            )
        except Exception as e:
            # Fallback
            if self._fallback_fn:
                fallback_pred = self._fallback_fn(features)
                result = PredictionResult(
                    prediction=fallback_pred,
                    model_version="fallback", model_name=model_name,
                    fallback_used=True,
                    latency_ms=(time.perf_counter() - start) * 1000,
                )
            else:
                raise

        if cache_key and result:
            self._cache.set(cache_key, result)

        return result
