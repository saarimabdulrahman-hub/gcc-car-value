"""ML instrumentation — creates spans for ML operations.

Creates child spans for model loading, prediction, and fallback decisions.

Usage:
    from src.core.tracing.instrumentation.ml import MLInstrumentation
    ml = MLInstrumentation()

    with ml.start_prediction_span("lightgbm_v1") as span:
        result = model.predict(features)
        span.set_attribute("ml.prediction_value", result)
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from src.core.tracing.tracer import get_tracer


class MLInstrumentation:
    """Creates spans for ML model operations."""

    def __init__(self):
        self._tracer = get_tracer("ml")

    @contextmanager
    def start_prediction_span(self, model_version: str,
                              model_type: str = "lightgbm",
                              attributes: dict[str, Any] | None = None):
        """Create a span for an ML prediction.

        Args:
            model_version: Model version string (e.g., 'lightgbm_v20260712_1400').
            model_type: Model type (lightgbm, statistical).
            attributes: Additional span attributes.
        """
        with self._tracer.start_span(
            f"ml.predict ({model_type})",
            kind="internal",
            attributes={
                "ml.model_type": model_type,
                "ml.model_version": model_version,
                **(attributes or {}),
            },
        ) as span:
            yield span

    @contextmanager
    def start_model_load_span(self, model_name: str,
                              attributes: dict[str, Any] | None = None):
        """Create a span for model loading."""
        with self._tracer.start_span(
            f"ml.load_model ({model_name})",
            kind="internal",
            attributes={
                "ml.model_name": model_name,
                **(attributes or {}),
            },
        ) as span:
            yield span

    @contextmanager
    def start_fallback_span(self, reason: str,
                            attributes: dict[str, Any] | None = None):
        """Create a span for ML fallback to statistical engine."""
        with self._tracer.start_span(
            "ml.fallback",
            kind="internal",
            attributes={
                "ml.fallback_reason": reason,
                **(attributes or {}),
            },
        ) as span:
            yield span
