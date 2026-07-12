"""Test Haraj pipeline — discovery, pagination, extraction, mapper, Arabic support."""
import pytest
from marketplaces.haraj.config import HarajConfig
from marketplaces.haraj.discovery import HarajDiscovery
from marketplaces.haraj.pagination import HarajPagination
from marketplaces.haraj.mapper import HarajMapper
from marketplaces.haraj.capabilities import HarajCapabilities
from marketplaces.haraj.constants import MARKETPLACE_NAME

# Arabic mock listing with RTL content
SEARCH_HTML = """
<html dir="rtl"><body>
<div class="post">
    <h3>تويوتا لاندكروزر 2018</h3>
    <div class="price">ريال 125,000</div>
    <div class="year">2018</div>
    <div class="mileage">120,000 كم</div>
    <div class="location">الرياض</div>
    <a href="/haraj/123456">عرض</a>
</div>
</body></html>
"""

DETAIL_HTML = """
<html dir="rtl"><body>
<h1>تويوتا لاندكروزر 2018 VXR</h1>
<div class="price">ريال 125,000</div>
<div class="mileage">120,000 كم</div>
<div class="year">2018</div>
<div class="spec">مواصفات خليجية</div>
<div class="transmission">أوتوماتيك</div>
<div class="fuel">بنزين</div>
<div class="body-type">SUV</div>
<div class="color">أبيض</div>
<div class="location">الرياض</div>
<div class="description">لاندكروزر بحالة ممتازة</div>
<div class="seller">معرض السيارات</div>
</body></html>
"""


class TestHarajDiscovery:
    def test_search_url(self):
        d = HarajDiscovery()
        url = d.search_url()
        assert "haraj.com.sa" in url

    def test_search_with_make(self):
        d = HarajDiscovery(); url = d.search_url(make="toyota")
        assert "toyota" in url

    def test_search_with_city(self):
        d = HarajDiscovery(); url = d.search_url(city="Riyadh")
        assert "Riyadh" in url


class TestHarajPagination:
    def test_pagination(self):
        p = HarajPagination(); p.start()
        assert p.next_page() == 1; p.next_page()
        assert p.current_page == 2

    def test_checkpoint(self):
        p = HarajPagination(); p.start(); p.next_page()
        state = p.checkpoint_state()
        p2 = HarajPagination(); p2.restore_state(state)
        assert p2.current_page == 1


class TestHarajMapper:
    def test_map_to_canonical(self):
        m = HarajMapper()
        data = {"make": "Toyota", "model": "Land Cruiser", "year": 2018,
                "price": 125000.0, "location": "Riyadh", "listing_id": "123"}
        listing = m.map_to_canonical(data, url="https://haraj.com.sa/haraj/123")
        assert listing.marketplace == MARKETPLACE_NAME
        assert listing.vehicle.make == "Toyota"
        assert listing.pricing.currency == "SAR"
        assert listing.location.country == "SA"


class TestCapabilities:
    def test_capability_manifest(self):
        caps = HarajCapabilities()
        assert caps.is_arabic_first
        assert caps.default_currency == "SAR"
        assert caps.default_country == "SA"
        assert caps.supports_chat


class TestArabicSupport:
    def test_arabic_content_preserved(self):
        """Arabic text flows through extraction unchanged — no translation."""
        from browser.dom.document import DOMDocument
        doc = DOMDocument.from_html(DETAIL_HTML)
        assert "تويوتا" in doc.text
        assert "لاندكروزر" in doc.text
        assert "مواصفات خليجية" in doc.text
