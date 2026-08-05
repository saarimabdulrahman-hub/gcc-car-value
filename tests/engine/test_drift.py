"""Tests for the drift detection engine (compute_psi, feature/target/prediction/market drift)."""

import numpy as np
import pytest

from src.engine.drift import (
    check_feature_drift,
    check_market_drift,
    check_prediction_drift,
    check_target_drift,
    compute_psi,
    log_drift_event,
)


class TestComputePsi:
    def test_identical_distributions_near_zero(self):
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        psi = compute_psi(data, data)
        assert psi < 0.05

    def test_different_distributions_high_psi(self):
        expected = np.random.default_rng(0).normal(10, 1, 1000)
        actual = np.random.default_rng(1).normal(20, 1, 1000)
        psi = compute_psi(expected, actual)
        assert psi > 0.5

    def test_constant_array_returns_zero(self):
        data = np.array([5.0, 5.0, 5.0, 5.0])
        assert compute_psi(data, data) == 0.0

    def test_empty_arrays_no_crash(self):
        assert compute_psi(np.array([]), np.array([])) == 0.0


class TestFeatureDrift:
    def test_no_drift_within_threshold(self):
        rng = np.random.default_rng(0)
        # 1000 samples — PSI is noisy at tiny sample sizes
        result = check_feature_drift(rng.normal(10, 1, 1000), rng.normal(10, 1, 1000), "mileage")
        assert result.drift_type == "feature"
        assert result.feature_name == "mileage"
        assert not result.threshold_exceeded
        assert "baseline_mean" in result.details

    def test_shifted_distribution_triggers_drift(self):
        rng = np.random.default_rng(0)
        result = check_feature_drift(
            rng.normal(30, 1, 100), rng.normal(10, 1, 100), "year"
        )
        assert result.threshold_exceeded


class TestTargetDrift:
    def test_price_shift_exceeds_threshold(self):
        baseline = np.array([100_000, 110_000, 120_000, 105_000, 115_000])
        current = np.array([140_000, 150_000, 145_000, 160_000, 155_000])  # >15% median shift
        result = check_target_drift(current, baseline)
        assert result.drift_type == "target"
        assert result.threshold_exceeded
        assert "median_change_pct" in result.details

    def test_no_drift_when_prices_stable(self):
        rng = np.random.default_rng(42)
        baseline = rng.normal(100_000, 5_000, 200)
        current = rng.normal(100_000, 5_000, 200)
        result = check_target_drift(current, baseline)
        assert not result.threshold_exceeded


class TestPredictionDrift:
    def test_degradation_over_30_percent(self):
        result = check_prediction_drift(current_mae=14_000, baseline_mae=10_000)
        assert result.drift_type == "prediction"
        assert result.threshold_exceeded  # 40% degradation

    def test_improvement_no_drift(self):
        result = check_prediction_drift(current_mae=9_000, baseline_mae=10_000)
        assert not result.threshold_exceeded


class TestMarketDrift:
    def test_volume_drop_triggers(self):
        result = check_market_drift(
            current_volume=50, baseline_volume=100,  # 50% drop
            current_volatility=1.0, baseline_volatility=1.0,
        )
        assert result.threshold_exceeded

    def test_volatility_spike_triggers(self):
        result = check_market_drift(
            current_volume=90, baseline_volume=100,
            current_volatility=3.0, baseline_volatility=1.0,  # 3x spike
        )
        assert result.threshold_exceeded

    def test_stable_market_no_drift(self):
        result = check_market_drift(
            current_volume=95, baseline_volume=100,
            current_volatility=1.1, baseline_volatility=1.0,
        )
        assert not result.threshold_exceeded


class TestLogDriftEvent:
    @pytest.mark.asyncio
    async def test_logs_event(self):
        session = _FakeSession()
        result = check_feature_drift(
            np.array([1.0, 2.0]), np.array([10.0, 11.0]), "test_feature"
        )
        event = await log_drift_event(session, result)
        assert event.drift_type == "feature"
        assert event.feature_name == "test_feature"
        assert event.threshold_exceeded is True
        assert session.added == [event]


class _FakeSession:
    """Minimal AsyncSession stand-in capturing added objects."""

    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)
