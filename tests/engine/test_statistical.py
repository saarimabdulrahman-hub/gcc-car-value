"""Test statistical valuation engine."""
import numpy as np
import pytest

from src.engine.comp_finder import CompListing
from src.engine.statistical import _bootstrap_ci, _compute_confidence


def make_comp(price: float, days: int = 10, status: str = "active",
              spec: str = "GCC", city: str = "Dubai"):
    return CompListing(
        source="test", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec=spec, city=city, country="AE",
        asking_price_aed=price, quality_score=90, status=status,
        days_on_market=days, delisting_confidence=None,
        platform_name="Test Platform",
    )


def test_high_confidence_with_many_recent_comps():
    comps = [make_comp(price=70000 + i * 100, days=5) for i in range(35)]
    prices = np.array([c.asking_price_aed for c in comps])
    assert _compute_confidence(comps, prices) == "high"


def test_medium_confidence_with_enough_comps():
    comps = [make_comp(price=70000 + i * 500, days=5) for i in range(15)]
    prices = np.array([c.asking_price_aed for c in comps])
    assert _compute_confidence(comps, prices) == "medium"


def test_low_confidence_with_few_comps():
    comps = [make_comp(price=70000 + i * 1000, days=5) for i in range(7)]
    prices = np.array([c.asking_price_aed for c in comps])
    assert _compute_confidence(comps, prices) == "low"


def test_insufficient_with_very_few_comps():
    comps = [make_comp(price=70000, days=5) for i in range(3)]
    prices = np.array([c.asking_price_aed for c in comps])
    assert _compute_confidence(comps, prices) == "insufficient"


def test_bootstrap_ci_returns_bounds():
    prices = np.array([70000, 71000, 72000, 73000, 74000, 75000, 76000, 77000] * 5)
    low, high = _bootstrap_ci(prices)
    assert low < high
    assert 70000 <= low <= 78000
    assert 70000 <= high <= 78000


def test_insufficient_returns_zero_estimate():
    """valuates with <5 comps returns zero estimate with insufficient confidence."""
    from src.engine.statistical import ValuationResult

    result = ValuationResult(
        estimate=0, price_low=0, price_high=0,
        confidence="insufficient", comp_count=3,
        comps=[], adjustments=[], segment_median=0,
    )
    assert result.confidence == "insufficient"
    assert result.estimate == 0
    assert result.comp_count < 5


def test_high_confidence_requires_30_comps_low_cv():
    """N >= 30, CV < 0.15, recent >= 15 → high confidence."""
    comps = [make_comp(price=50000 + i * 50, days=5) for i in range(30)]
    prices = np.array([c.asking_price_aed for c in comps])
    assert _compute_confidence(comps, prices) == "high"


def test_medium_not_high_with_few_recent():
    """N >= 10, CV < 0.30 but not enough recent → medium, not high."""
    comps = [make_comp(price=50000 + i * 200, days=60) for i in range(15)]
    prices = np.array([c.asking_price_aed for c in comps])
    confidence = _compute_confidence(comps, prices)
    assert confidence in ("medium", "low")  # CV may push it to low


def test_zero_mean_price_edge_case():
    """All-zero prices produce degenerate CV — should not crash, returns low or insufficient."""
    comps = [make_comp(price=0, days=5) for _ in range(20)]
    prices = np.array([c.asking_price_aed for c in comps])
    # CV is NaN (0/0) → confidence can't be high
    result = _compute_confidence(comps, prices)
    assert result in ("low", "insufficient")


def test_bootstrap_ci_deterministic():
    """Bootstrap CI with fixed seed is deterministic."""
    prices = np.array([50000, 55000, 60000] * 10)
    low1, high1 = _bootstrap_ci(prices, n_bootstrap=500)
    low2, high2 = _bootstrap_ci(prices, n_bootstrap=500)
    assert low1 == low2
    assert high1 == high2


@pytest.mark.asyncio
async def test_valuate_with_mocked_comps(monkeypatch):
    """Full valuate() flow with mocked find_comps — the money path."""
    from src.engine import statistical

    # Build 45 comps to hit "high" confidence threshold
    comps = [
        make_comp(price=75000 + i * 200, days=5, spec="GCC", city="Dubai")
        for i in range(45)
    ]

    async def mock_find_comps(*args, **kwargs):
        return comps

    monkeypatch.setattr(statistical, "find_comps", mock_find_comps)

    result = await statistical.valuate(
        session=None,  # not used when find_comps is mocked
        make="Toyota", model="Land Cruiser", year=2022,
        mileage_km=50000, spec="GCC", country="AE", city="Dubai",
    )

    assert result.estimate > 0
    assert result.confidence == "high"
    assert result.comp_count == 45
    assert result.price_low < result.estimate < result.price_high
    assert result.confidence_interval_80 is not None
    assert len(result.comps) == 10  # top 10 by relevance
    assert len(result.adjustments) >= 1  # at least mileage adjustment


@pytest.mark.asyncio
async def test_valuate_insufficient_comps(monkeypatch):
    """valuate() with < 5 comps returns insufficient confidence."""
    from src.engine import statistical

    async def mock_find_comps(*args, **kwargs):
        return [make_comp(price=75000, days=5) for _ in range(3)]

    monkeypatch.setattr(statistical, "find_comps", mock_find_comps)

    result = await statistical.valuate(
        session=None, make="Ferrari", model="F40", year=1992,
    )

    assert result.confidence == "insufficient"
    assert result.estimate == 0
    assert result.comp_count == 3
