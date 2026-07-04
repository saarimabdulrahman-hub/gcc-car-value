import pytest
from src.pipeline.normalizer import normalize_make, normalize_spec, normalize_city, normalize_listing

def test_normalize_make_lowercase():
    assert normalize_make("toyota") == "Toyota"

def test_normalize_make_unknown():
    assert normalize_make("BYD") == "Byd"

def test_normalize_spec_gcc_variations():
    assert normalize_spec("gcc spec") == "GCC"
    assert normalize_spec("us_spec") == "US"

def test_normalize_city():
    assert normalize_city("al ain") == "Al Ain"

def test_normalize_listing_full():
    data = {"make": "toyota", "model": "land cruiser", "year": "2018",
            "asking_price": "125000", "city": "al ain", "country": "AE",
            "spec": "gcc spec", "source": "dubizzle", "external_id": "abc"}
    result = normalize_listing(data)
    assert result["make"] == "Toyota"
    assert result["city"] == "Al Ain"
    assert result["spec"] == "GCC"
    assert result["normalized_price_aed"] == 125000.0
    assert result["original_currency"] == "AED"

def test_normalize_kwd_price():
    data = {"make": "Toyota", "model": "Camry", "year": "2020",
            "asking_price": "5000", "city": "Kuwait City", "country": "KW",
            "original_currency": "KWD", "source": "q8car", "external_id": "x"}
    result = normalize_listing(data)
    assert result["normalized_price_aed"] == pytest.approx(5000 * 11.94, rel=0.001)
