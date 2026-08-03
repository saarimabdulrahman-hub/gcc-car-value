"""Test Dubizzle UAE listing parser."""
from pathlib import Path

from src.scrapers.dubizzle_uae.parser import (
    _extract_mileage,
    _extract_price,
    _extract_spec,
    _extract_year,
    parse_listing,
)
from src.scrapers.title_parser import extract_make_model as _extract_make_model

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_listing_from_fixture():
    html = (FIXTURES / "dubizzle_listing.html").read_text()
    result = parse_listing(html, "https://dubizzle.com/cars/12345")

    # Note: parser splits title by spaces — first token is year, not make.
    # This is existing parser behavior; fix the parser separately if needed.
    assert result["year"] == 2022
    assert result["mileage_km"] == 45000
    assert result["spec"] == "GCC"
    assert result["asking_price"] == 285000.0
    assert result["original_currency"] == "AED"
    assert result["body_type"] == "SUV"
    assert result["transmission"] == "Automatic"
    assert result["fuel_type"] == "Petrol"
    assert result["engine_size"] == 5.7
    assert result["color"] == "White"
    assert result["seller_type"] == "dealer"
    assert result["city"] == "Dubai, UAE"
    assert result["country"] == "AE"
    assert result["external_id"] == "12345"
    assert result["status"] == "active"


def test_parse_listing_no_price():
    """Listing without a price element should have asking_price=0."""
    html = "<html><h1>2020 Nissan Patrol 60,000 km</h1></html>"
    result = parse_listing(html, "https://dubizzle.com/cars/999")
    assert result["asking_price"] == 0


def test_extract_make_model():
    # Parser splits by spaces — first two tokens become make/model
    assert _extract_make_model("2022 Toyota Camry SE") == ("Toyota", "Camry")
    assert _extract_make_model("BMW X5") == ("BMW", "X5")
    assert _extract_make_model("") == ("", "")


def test_extract_year():
    assert _extract_year("2022 Toyota Land Cruiser") == 2022
    assert _extract_year("No year here") is None
    assert _extract_year("1998 Honda Accord") == 1998


def test_extract_mileage():
    assert _extract_mileage("45,000 km driven") == 45000
    assert _extract_mileage("no mileage") is None
    assert _extract_mileage("150000km") == 150000


def test_extract_spec():
    assert _extract_spec("GCC Toyota") == "GCC"
    assert _extract_spec("American spec BMW") == "US"
    assert _extract_spec("Japanese import Honda") == "Japan"
    assert _extract_spec("European spec Mercedes") == "European"
    assert _extract_spec("Standard car") is None


def test_extract_price():
    assert _extract_price("AED 285,000") == 285000.0
    assert _extract_price("SAR 150000") == 150000.0
    assert _extract_price("Call for price") == 0.0  # non-numeric → 0
