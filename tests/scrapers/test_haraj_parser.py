"""Test Haraj KSA listing parser."""
from pathlib import Path

from src.scrapers.haraj_ksa.scraper import HarajKSAScraper

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_listing_from_fixture():
    html = (FIXTURES / "haraj_listing.html").read_text()
    scraper = HarajKSAScraper()
    # URL needs trailing slash for regex r'/(\d+)[/$]' to capture ID
    result = scraper.parse(html, "https://haraj.com.sa/car/12345/")

    # Parser splits title by spaces — first token is year
    assert result["year"] == 2018
    assert result["spec"] == "GCC"
    assert result["mileage_km"] == 120000
    assert result["asking_price"] == 145000.0
    assert result["original_currency"] == "SAR"
    assert result["country"] == "SA"
    assert result["status"] == "active"
    assert result["external_id"] == "12345"


def test_parse_empty_listing():
    scraper = HarajKSAScraper()
    result = scraper.parse("<html></html>", "https://haraj.com.sa/car/999")
    assert result["make"] == ""
    assert result["model"] == ""
    assert result["year"] is None
    assert result["asking_price"] == 0
