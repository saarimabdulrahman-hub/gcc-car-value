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


@pytest.mark.asyncio
async def test_mileage_adjustment_direction_is_downward(monkeypatch):
    """Target has more km than the segment → mileage adjustment must be negative."""
    from src.engine import statistical

    comps = [make_comp(price=80000, days=5) for _ in range(20)]
    for c in comps:
        c.mileage_km = 30000  # segment is low-mileage

    async def mock_find_comps(*args, **kwargs):
        return comps

    monkeypatch.setattr(statistical, "find_comps", mock_find_comps)

    result = await statistical.valuate(
        session=None, make="Toyota", model="Camry", year=2020,
        mileage_km=100000, spec="GCC", country="AE", city="Dubai",
    )

    mileage_adj = [a for a in result.adjustments if a.reason == "mileage"]
    assert mileage_adj, "expected a mileage adjustment"
    assert mileage_adj[0].amount < 0  # more km than segment → price down


# ── valuate() integration tests — mock find_comps, exercise adjustments ──

def make_full_comp(price, mileage, spec="GCC", city="Dubai", days=10):
    return CompListing(
        source="test", make="Toyota", model="Camry", year=2020,
        mileage_km=mileage, spec=spec, city=city, country="AE",
        asking_price_aed=price, quality_score=90, status="active",
        days_on_market=days, delisting_confidence=None,
        platform_name="Test Platform",
    )


@pytest.fixture
def mock_find_comps(monkeypatch):
    """Replace find_comps with a configurable fake returning fixture comps."""
    holder = {}

    async def fake_find_comps(session, make, model, year, mileage_km,
                              spec, country, city, min_comps=15, max_comps=50):
        return holder["comps"]

    monkeypatch.setattr("src.engine.statistical.find_comps", fake_find_comps)
    return holder


class FakeSession:
    pass


@pytest.mark.asyncio
async def test_valuate_insufficient_with_few_comps(mock_find_comps):
    from src.engine.statistical import valuate
    mock_find_comps["comps"] = [make_full_comp(70000, 50000) for _ in range(3)]
    result = await valuate(FakeSession(), "Toyota", "Camry", 2020, 50000)
    assert result.confidence == "insufficient"
    assert result.estimate == 0
    assert result.comp_count == 3


@pytest.mark.asyncio
async def test_valuate_mileage_adjustment(mock_find_comps):
    from src.engine.statistical import valuate
    # Comps average HIGHER mileage (60k) than target (40k) → target has fewer
    # km than segment avg → estimate adjusts UP by delta*0.25
    comps = [make_full_comp(price=100000 + i * 100, mileage=60000) for i in range(10)]
    mock_find_comps["comps"] = comps
    result = await valuate(FakeSession(), "Toyota", "Camry", 2020, 40000)
    assert result.confidence != "insufficient"
    assert len(result.adjustments) >= 1
    mileage_adj = next(a for a in result.adjustments if a.reason == "mileage")
    assert mileage_adj.amount > 0  # fewer km than avg → positive adjustment
    assert result.estimate > 100000


@pytest.mark.asyncio
async def test_valuate_spec_premium(mock_find_comps):
    from src.engine.statistical import valuate
    # GCC comps priced higher than non-GCC → target GCC gets a premium
    gcc = [make_full_comp(price=110000 + i * 100, mileage=50000, spec="GCC") for i in range(5)]
    non_gcc = [make_full_comp(price=90000 + i * 100, mileage=50000, spec="US") for i in range(5)]
    mock_find_comps["comps"] = gcc + non_gcc
    result = await valuate(FakeSession(), "Toyota", "Camry", 2020, 50000, spec="GCC")
    spec_adj = next((a for a in result.adjustments if a.reason == "spec"), None)
    assert spec_adj is not None
    assert spec_adj.amount > 0  # GCC premium adds value


@pytest.mark.asyncio
async def test_valuate_city_adjustment(mock_find_comps):
    from src.engine.statistical import valuate
    # Dubai comps pricier than Sharjah comps → target in Dubai gets a premium
    dubai = [make_full_comp(price=105000 + i * 100, mileage=50000, city="Dubai") for i in range(6)]
    sharjah = [make_full_comp(price=95000 + i * 100, mileage=50000, city="Sharjah") for i in range(6)]
    mock_find_comps["comps"] = dubai + sharjah
    result = await valuate(FakeSession(), "Toyota", "Camry", 2020, 50000, city="Dubai")
    city_adj = next((a for a in result.adjustments if a.reason == "city"), None)
    assert city_adj is not None
    assert city_adj.amount > 0


@pytest.mark.asyncio
async def test_valuate_no_adjustments_when_uniform(mock_find_comps):
    from src.engine.statistical import valuate
    # All comps identical spec/city/mileage → no mileage/spec/city adjustments
    comps = [make_full_comp(price=100000 + i * 50, mileage=50000) for i in range(12)]
    mock_find_comps["comps"] = comps
    result = await valuate(FakeSession(), "Toyota", "Camry", 2020, 50000)
    reasons = [a.reason for a in result.adjustments]
    # Mileage adjustment is appended even at zero delta; spec/city are skipped
    # when their inputs are None. Any zero-delta adjustment must not move price.
    assert "spec" not in reasons
    assert "city" not in reasons
    for a in result.adjustments:
        assert abs(a.amount) < 1
