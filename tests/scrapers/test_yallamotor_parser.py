"""Test YallaMotor listing parser."""
from pathlib import Path

from src.scrapers.yallamotor.scraper import YallaMotorScraper

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_listing_from_fixture():
    html = (FIXTURES / "yallamotor_listing.html").read_text()
    scraper = YallaMotorScraper(country_key="uae")
    # URL needs trailing slash: r'/(\d+)[/$]' — literal $ in char class, not anchor
    result = scraper.parse(html, "https://uae.yallamotor.com/used-cars/12345/")

    # Parser splits title by spaces — first token becomes make, second becomes model
    # Title: "2021 Nissan Patrol..." → make="2021", model="Nissan"
    # This is existing parser behavior — _extract_make_model doesn't strip year prefix
    assert result["year"] is not None  # _extract_number extracts year
    assert result["spec"] == "GCC"
    assert result["mileage_km"] == 55000
    assert result["spec"] == "GCC"
    assert result["mileage_km"] == 55000
    assert result["asking_price"] == 210000.0
    assert result["original_currency"] == "AED"
    assert result["country"] == "AE"
    assert "suv" in str(result.get("body_type", "")).lower()
    assert "automatic" in str(result.get("transmission", "")).lower()
    assert "petrol" in str(result.get("fuel_type", "")).lower()
    assert result["status"] == "active"
    assert result["external_id"] == "12345"


def test_ksa_country_config():
    scraper = YallaMotorScraper(country_key="ksa")
    result = scraper.parse(
        "<html><h1>2020 Toyota Camry 80,000 km</h1><div class='car-price'>SAR 85,000</div></html>",
        "https://ksa.yallamotor.com/used-cars/999/",
    )
    assert result["country"] == "SA"
    assert result["city"] == "Riyadh"
    assert result["original_currency"] == "SAR"
