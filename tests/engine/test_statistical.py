"""Test statistical valuation engine."""
import pytest
from src.engine.statistical import _compute_confidence, _bootstrap_ci
from src.engine.comp_finder import CompListing
import numpy as np


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
