from src.pipeline.validator import validate_listing

def make_valid(**overrides):
    base = {"make": "Toyota", "model": "Land Cruiser", "year": 2018,
            "asking_price": 125000.0, "mileage_km": 80000, "spec": "GCC",
            "city": "Dubai", "country": "AE", "source": "dubizzle",
            "external_id": "abc123", "url": "https://example.com/car"}
    base.update(overrides)
    return base

def test_valid_listing_passes():
    result = validate_listing(make_valid())
    assert result.is_valid
    assert len(result.errors) == 0

def test_missing_make_rejected():
    result = validate_listing(make_valid(make=None))
    assert not result.is_valid

def test_future_year_rejected():
    result = validate_listing(make_valid(year=2030))
    assert not result.is_valid

def test_test_post_price_rejected():
    result = validate_listing(make_valid(asking_price=12345))
    assert not result.is_valid

def test_invalid_country_rejected():
    result = validate_listing(make_valid(country="US"))
    assert not result.is_valid

def test_high_mileage_warns():
    result = validate_listing(make_valid(mileage_km=600000))
    assert result.is_valid
    assert any("high_mileage" in w for w in result.warnings)

def test_old_vehicle_warns():
    result = validate_listing(make_valid(year=1995))
    assert result.is_valid
    assert any("old_vehicle" in w for w in result.warnings)
