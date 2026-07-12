"""Test PredictionService — feature building and prediction."""
import pytest
import numpy as np
from src.ml.prediction_service import PredictionService, PredictionResult


class MockModel:
    """Predicts a fixed value based on input mean for testing."""
    def predict(self, X):
        return np.array([X.mean(axis=1)[0] * 100])


@pytest.fixture
def service():
    model = MockModel()
    metadata = {
        "model_name": "test_model_v1",
        "model_type": "lightgbm",
        "mae": 5000.0,
        "mape": 4.5,
        "r2_score": 0.85,
        "feature_version": "1.0.0",
        "features_used": None,  # uses TRAINING_FEATURE_NAMES default
        "training_rows": 5000,
        "trained_at": "2026-07-01T00:00:00+00:00",
    }
    return PredictionService(model, metadata)


def test_prediction_returns_result(service):
    result = service.predict(
        make="Toyota", model="Land Cruiser", year=2018,
        mileage_km=120000, spec="GCC", country="AE", city="Dubai",
    )
    assert isinstance(result, PredictionResult)
    assert result.predicted_value > 0
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.model_version == "test_model_v1"
    assert result.feature_count > 0
    assert result.prediction_latency_ms >= 0


def test_prediction_with_market_context(service):
    result = service.predict(
        make="Nissan", model="Patrol", year=2020,
        mileage_km=80000, spec="GCC", country="AE", city="Abu Dhabi",
        market_context={
            "segment_median_price": 180000,
            "segment_liquidity_days": 14,
            "price_volatility": 0.08,
            "market_trend_4w": 0.03,
            "listing_volume": 50,
            "brand_reliability": 3.5,
            "depreciation_rate": 0.10,
            "common_issue_count": 2,
        },
    )
    assert result.predicted_value > 0
    assert result.feature_count >= 15


def test_prediction_with_minimal_input(service):
    """Minimum required input — all optional fields omitted."""
    result = service.predict(make="Toyota", model="Camry", year=2020)
    assert isinstance(result, PredictionResult)
    assert result.predicted_value > 0


def test_confidence_from_mae():
    """Confidence score derived from MAE ratio."""
    import numpy as np

    class SimpleModel:
        def predict(self, X):
            return np.array([100000.0])

    # Low MAE → high confidence
    high_conf_svc = PredictionService(SimpleModel(), {"mae": 5000, "model_name": "v1", "features_used": None})
    result = high_conf_svc.predict(make="Toyota", model="Camry", year=2020)
    assert result.confidence_score >= 0.75

    # High MAE → low confidence
    low_conf_svc = PredictionService(SimpleModel(), {"mae": 40000, "model_name": "v1", "features_used": None})
    result = low_conf_svc.predict(make="Toyota", model="Camry", year=2020)
    assert result.confidence_score <= 0.60
