"""Test comp finder scoring and platform attribution."""
from src.engine.comp_finder import CompListing, _platform_name, _score_comp


def test_platform_names():
    assert _platform_name("dubizzle_uae") == "Dubizzle UAE"
    assert _platform_name("yallamotor") == "YallaMotor"
    assert _platform_name("haraj") == "Haraj KSA"
    assert _platform_name("unknown_source") == "unknown_source"


def test_found_on_text():
    comp = CompListing(
        source="dubizzle_uae", make="Toyota", model="Camry",
        year=2020, mileage_km=50000, spec="GCC", city="Dubai",
        country="AE", asking_price_aed=75000, quality_score=90,
        status="active", days_on_market=5, delisting_confidence=None,
        platform_name="Dubizzle UAE",
    )
    assert "Dubizzle UAE" in comp.found_on_text
    assert "Dubai" in comp.found_on_text


def test_score_recent_listing_scores_higher():
    recent = CompListing(
        source="test", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai", country="AE",
        asking_price_aed=75000, quality_score=90, status="active",
        days_on_market=3, delisting_confidence=None, platform_name="Test",
    )
    old = CompListing(
        source="test2", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai", country="AE",
        asking_price_aed=75000, quality_score=90, status="active",
        days_on_market=120, delisting_confidence=None, platform_name="Test",
    )
    recent_score = _score_comp(recent, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    old_score = _score_comp(old, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert recent_score > old_score


def test_sold_comp_gets_bonus():
    sold = CompListing(
        source="test", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai", country="AE",
        asking_price_aed=75000, quality_score=90, status="sold_confirmed",
        days_on_market=14, delisting_confidence=0.99, platform_name="Test",
    )
    active = CompListing(
        source="test2", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai", country="AE",
        asking_price_aed=75000, quality_score=90, status="active",
        days_on_market=14, delisting_confidence=None, platform_name="Test",
    )
    sold_score = _score_comp(sold, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    active_score = _score_comp(active, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert sold_score > active_score


def _mk(**over):
    base = dict(
        source="test", make="Toyota", model="Camry", year=2020,
        mileage_km=50000, spec="GCC", city="Dubai", country="AE",
        asking_price_aed=75000, quality_score=90, status="active",
        days_on_market=5, delisting_confidence=None, platform_name="Test",
    )
    base.update(over)
    return CompListing(**base)


def test_spec_match_scores_higher_than_mismatch():
    same_spec = _mk(spec="GCC")
    diff_spec = _mk(spec="US")
    # Requested spec is GCC: matching GCC comp scores better than US spec
    same_score = _score_comp(same_spec, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    diff_score = _score_comp(diff_spec, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert same_score > diff_score


def test_gcc_spec_penalty_smaller_than_other_spec():
    # Requested US spec: a GCC comp gets only -5, a Japan comp -15
    gcc_comp = _mk(spec="GCC")
    japan_comp = _mk(spec="Japan")
    gcc_score = _score_comp(gcc_comp, "Toyota", "Camry", 2020, 50000, "US", "AE")
    japan_score = _score_comp(japan_comp, "Toyota", "Camry", 2020, 50000, "US", "AE")
    assert gcc_score > japan_score


def test_lower_mileage_penalty_for_closer_mileage():
    close = _mk(mileage_km=50000)
    far = _mk(mileage_km=150000)
    close_score = _score_comp(close, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    far_score = _score_comp(far, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert close_score > far_score


def test_matching_year_scores_better():
    exact = _mk(year=2020)
    older = _mk(year=2015)
    exact_score = _score_comp(exact, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    older_score = _score_comp(older, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert exact_score > older_score


def test_country_mismatch_penalized():
    same = _mk(country="AE")
    other = _mk(country="SA")
    same_score = _score_comp(same, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    other_score = _score_comp(other, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert same_score > other_score


def test_higher_quality_scores_better():
    high = _mk(quality_score=95)
    low = _mk(quality_score=50)
    high_score = _score_comp(high, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    low_score = _score_comp(low, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    assert high_score > low_score


def test_score_without_mileage_or_spec_no_crash():
    comp = _mk(mileage_km=None, spec=None)
    score = _score_comp(comp, "Toyota", "Camry", 2020, None, None, None)
    assert score > 0


def test_perfect_match_scores_near_max():
    comp = _mk()  # exact match on year/mileage/spec/country, 90 quality
    score = _score_comp(comp, "Toyota", "Camry", 2020, 50000, "GCC", "AE")
    # Quality bonus (+9) and recency push a perfect match above 100
    assert 100 <= score <= 115
