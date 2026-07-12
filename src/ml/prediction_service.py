"""PredictionService — build features and call the ML model.

Provides a clean interface between the valuation API and the LightGBM model.
Feature vector construction is isolated here so it can be tested independently.

Usage:
    from src.ml.prediction_service import PredictionService
    svc = PredictionService(model, metadata)
    result = svc.predict(make="Toyota", model="Land Cruiser", year=2018, ...)
"""

from dataclasses import dataclass
from datetime import datetime
import numpy as np
import structlog

logger = structlog.get_logger()

# Feature names must match what the model was trained on.
# These correspond to the 15 features registered in engine/features/.
TRAINING_FEATURE_NAMES = [
    "mileage_km", "vehicle_age_years", "is_gcc_spec", "is_us_spec",
    "is_dealer", "has_warranty", "has_service_history",
    "segment_median_price", "segment_liquidity_days", "price_volatility",
    "market_trend_4w", "listing_volume",
    "brand_reliability", "depreciation_rate", "common_issue_count",
]


@dataclass
class PredictionResult:
    """Typed prediction output."""
    predicted_value: float
    confidence_score: float       # 0.0 – 1.0
    model_version: str
    feature_count: int
    prediction_latency_ms: float


class PredictionService:
    """Call the ML model for a single vehicle valuation.

    Features are built from the query parameters and optional market context.
    Market context enriches the feature vector with segment-level data.
    If market context is not provided, sensible defaults are used.
    """

    def __init__(self, model: object, metadata: dict):
        self._model = model
        self._metadata = metadata
        self._feature_names: list[str] = (
            metadata.get("features_used", []) or TRAINING_FEATURE_NAMES
        )

    def predict(
        self,
        make: str,
        model: str,
        year: int,
        mileage_km: int | None = None,
        spec: str | None = None,
        country: str | None = None,
        city: str | None = None,
        seller_type: str | None = None,
        warranty: bool = False,
        service_history: bool = False,
        market_context: dict | None = None,
    ) -> PredictionResult:
        """Compute an ML-based valuation estimate.

        Args:
            make, model, year: Vehicle identity.
            mileage_km: Odometer.
            spec: GCC, US, Japan, European.
            country: AE, SA, QA, KW, BH, OM.
            city: City name.
            seller_type: dealer, private, auction.
            warranty: Has warranty.
            service_history: Has service history.
            market_context: Optional dict with segment-level market data
                (segment_median_price, segment_liquidity_days,
                 price_volatility, market_trend_4w, listing_volume,
                 brand_reliability, depreciation_rate, common_issue_count).

        Returns:
            PredictionResult with predicted_value and metadata.
        """
        import time
        start = time.perf_counter()

        ctx = market_context or {}
        current_year = datetime.now().year

        # Build feature vector in the exact order the model expects.
        # Missing features get a 0.0 (which matches training fillna(0)).
        feature_values: dict[str, float] = {
            "mileage_km": float(mileage_km or 0),
            "vehicle_age_years": float(current_year - year),
            "is_gcc_spec": 1.0 if str(spec or "").upper() == "GCC" else 0.0,
            "is_us_spec": 1.0 if str(spec or "").upper() == "US" else 0.0,
            "is_dealer": 1.0 if seller_type == "dealer" else 0.0,
            "has_warranty": 1.0 if warranty else 0.0,
            "has_service_history": 1.0 if service_history else 0.0,
            "segment_median_price": float(ctx.get("segment_median_price", 0)),
            "segment_liquidity_days": float(ctx.get("segment_liquidity_days", 30)),
            "price_volatility": float(ctx.get("price_volatility", 0.05)),
            "market_trend_4w": float(ctx.get("market_trend_4w", 0.0)),
            "listing_volume": float(ctx.get("listing_volume", 0)),
            "brand_reliability": float(ctx.get("brand_reliability", 3.0)),
            "depreciation_rate": float(ctx.get("depreciation_rate", 0.12)),
            "common_issue_count": float(ctx.get("common_issue_count", 0)),
        }

        # Build ordered feature array
        X = np.array([
            feature_values.get(name, 0.0)
            for name in self._feature_names
        ]).reshape(1, -1)

        # Predict
        predicted = float(self._model.predict(X)[0])

        # Confidence: derive from model's training MAE and the comp-based
        # statistical confidence. Higher MAE → lower confidence.
        mae = self._metadata.get("mae")
        if mae and predicted > 0:
            cv_approx = mae / predicted
            if cv_approx < 0.10:
                confidence = 0.90
            elif cv_approx < 0.20:
                confidence = 0.75
            elif cv_approx < 0.30:
                confidence = 0.60
            else:
                confidence = 0.40
        else:
            confidence = 0.70  # default if no MAE metadata

        latency_ms = (time.perf_counter() - start) * 1000

        logger.debug("ml_prediction_computed",
                     make=make, model=model, year=year,
                     predicted=round(predicted),
                     confidence=round(confidence, 2),
                     latency_ms=round(latency_ms, 1))

        return PredictionResult(
            predicted_value=predicted,
            confidence_score=round(confidence, 2),
            model_version=self._metadata.get("model_name", "unknown"),
            feature_count=len(self._feature_names),
            prediction_latency_ms=round(latency_ms, 1),
        )
