"""Direct tests for the scraped-listing validator (pipeline gate)."""
from src.pipeline.validator import validate_listing


def _valid(**overrides) -> dict:
    """A minimal listing that passes every validation rule. Override to break it."""
    base = {
        "make": "Toyota",
        "model": "Land Cruiser",
        "year": 2020,
        "asking_price": 250000,
        "mileage_km": 60000,
        "spec": "GCC",
        "city": "Dubai",
        "country": "AE",
        "source": "dubizzle_uae",
        "external_id": "abc-123",
    }
    base.update(overrides)
    return base


def test_valid_listing_passes():
    result = validate_listing(_valid())
    assert result.is_valid is True
    assert result.errors == []


def test_missing_make_fails():
    data = _valid()
    del data["make"]
    result = validate_listing(data)
    assert result.is_valid is False
    assert any("make" in e for e in result.errors)


def test_missing_asking_price_fails():
    data = _valid()
    del data["asking_price"]
    result = validate_listing(data)
    assert result.is_valid is False
    assert any("asking_price" in e for e in result.errors)


def test_empty_external_id_fails():
    result = validate_listing(_valid(external_id=""))
    assert result.is_valid is False
    assert any("external_id" in e for e in result.errors)


def test_whitespace_external_id_fails():
    result = validate_listing(_valid(external_id="   "))
    assert result.is_valid is False
    assert any("external_id" in e for e in result.errors)


def test_none_year_fails():
    result = validate_listing(_valid(year=None))
    assert result.is_valid is False
    assert any("year" in e for e in result.errors)


def test_invalid_country_fails_schema():
    # 'US' is not an allowed country code (AE/SA/QA/KW/BH/OM)
    result = validate_listing(_valid(country="US"))
    assert result.is_valid is False


def test_high_mileage_is_valid_but_warns():
    result = validate_listing(_valid(mileage_km=600000))
    assert result.is_valid is True
    assert "high_mileage" in result.warnings
