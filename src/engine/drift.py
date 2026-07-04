"""Drift detection — feature, target, prediction, and market drift monitoring.

Spec Section 7.3: Computes PSI (Population Stability Index) and distribution changes.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.drift_event import DriftEvent
import structlog

logger = structlog.get_logger()


@dataclass
class DriftResult:
    drift_type: str
    feature_name: str | None
    psi_value: float
    threshold_exceeded: bool
    details: dict


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index between two distributions."""
    # Combine to compute bin edges
    combined = np.concatenate([expected, actual])
    bin_edges = np.percentile(combined, np.linspace(0, 100, bins + 1))
    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return 0.0

    e_hist, _ = np.histogram(expected, bins=bin_edges)
    a_hist, _ = np.histogram(actual, bins=bin_edges)

    # Add small epsilon to avoid division by zero
    e_pct = (e_hist + 0.0001) / (e_hist.sum() + 0.0001)
    a_pct = (a_hist + 0.0001) / (a_hist.sum() + 0.0001)

    psi_values = (a_pct - e_pct) * np.log(a_pct / e_pct)
    return float(np.sum(psi_values))


def check_feature_drift(current: np.ndarray, baseline: np.ndarray,
                        feature_name: str) -> DriftResult:
    """Check if a single feature has drifted from baseline."""
    psi = compute_psi(baseline, current)
    exceeded = psi > 0.2
    return DriftResult(
        drift_type="feature",
        feature_name=feature_name,
        psi_value=psi,
        threshold_exceeded=exceeded,
        details={
            "baseline_mean": float(np.mean(baseline)),
            "current_mean": float(np.mean(current)),
            "baseline_std": float(np.std(baseline)),
            "current_std": float(np.std(current)),
        },
    )


def check_target_drift(current_prices: np.ndarray,
                       baseline_prices: np.ndarray) -> DriftResult:
    """Check if target (price) distribution has shifted."""
    pct_change = abs(np.median(current_prices) - np.median(baseline_prices)) / \
                 max(np.median(baseline_prices), 1) * 100
    psi = compute_psi(baseline_prices, current_prices)
    exceeded = pct_change > 15 or psi > 0.3
    return DriftResult(
        drift_type="target",
        feature_name="price",
        psi_value=psi,
        threshold_exceeded=exceeded,
        details={
            "median_change_pct": round(pct_change, 2),
            "baseline_median": float(np.median(baseline_prices)),
            "current_median": float(np.median(current_prices)),
        },
    )


def check_prediction_drift(current_mae: float, baseline_mae: float) -> DriftResult:
    """Check if model performance is degrading."""
    degradation = (current_mae - baseline_mae) / max(baseline_mae, 1) * 100
    exceeded = degradation > 30
    return DriftResult(
        drift_type="prediction",
        feature_name="mae",
        psi_value=degradation / 100,
        threshold_exceeded=exceeded,
        details={
            "mae_degradation_pct": round(degradation, 2),
            "baseline_mae": round(baseline_mae, 2),
            "current_mae": round(current_mae, 2),
        },
    )


def check_market_drift(current_volume: int, baseline_volume: int,
                       current_volatility: float,
                       baseline_volatility: float) -> DriftResult:
    """Check for market structure changes."""
    volume_drop = (baseline_volume - current_volume) / max(baseline_volume, 1) * 100
    vol_spike = current_volatility / max(baseline_volatility, 0.001)
    exceeded = volume_drop > 40 or vol_spike > 2.0
    return DriftResult(
        drift_type="market",
        feature_name="volume_volatility",
        psi_value=max(volume_drop / 100, vol_spike / 3),
        threshold_exceeded=exceeded,
        details={
            "volume_change_pct": round(volume_drop, 2),
            "volatility_ratio": round(vol_spike, 2),
        },
    )


async def log_drift_event(session: AsyncSession, result: DriftResult) -> DriftEvent:
    """Record a drift event in the database."""
    event = DriftEvent(
        detected_at=datetime.now(timezone.utc),
        drift_type=result.drift_type,
        feature_name=result.feature_name,
        psi_value=result.psi_value,
        threshold_exceeded=result.threshold_exceeded,
        details=result.details,
    )
    session.add(event)
    if result.threshold_exceeded:
        logger.warning("drift_detected",
                       type=result.drift_type,
                       feature=result.feature_name,
                       psi=round(result.psi_value, 4))
    return event
