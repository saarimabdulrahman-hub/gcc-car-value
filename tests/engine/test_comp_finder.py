"""Test comp finder scoring and platform attribution."""
from src.engine.comp_finder import _platform_name, _score_comp, CompListing


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
