"""Test Dubizzle pipeline — discovery, pagination, listing extraction, mapper, pipeline orchestration."""
import pytest
from marketplaces.dubizzle.config import DubizzleConfig
from marketplaces.dubizzle.discovery import DubizzleDiscovery
from marketplaces.dubizzle.pagination import DubizzlePagination
from marketplaces.dubizzle.listing import DubizzleListingExtractor
from marketplaces.dubizzle.details import DubizzleDetailExtractor
from marketplaces.dubizzle.mapper import DubizzleMapper
from marketplaces.dubizzle.pipeline import DubizzlePipeline
from marketplaces.dubizzle.constants import MARKETPLACE_NAME
from browser.dom.document import DOMDocument

# Mock HTML for search results page
SEARCH_HTML = """
<html><body>
<div class="listing-card">
    <h2>Toyota Land Cruiser 2018</h2>
    <div class="price">AED 125,000</div>
    <div class="year">2018</div>
    <div class="mileage">120,000 km</div>
    <div class="location">Dubai</div>
    <a href="/motors/used-cars/toyota/land-cruiser/123456">View</a>
</div>
<div class="listing-card">
    <h2>Nissan Patrol 2020</h2>
    <div class="price">AED 180,000</div>
    <div class="year">2020</div>
    <div class="mileage">80,000 km</div>
    <div class="location">Abu Dhabi</div>
    <a href="/motors/used-cars/nissan/patrol/789012">View</a>
</div>
</body></html>
"""

# Mock HTML for detail page
DETAIL_HTML = """
<html><body>
<h1>Toyota Land Cruiser 2018 VXR</h1>
<div class="price-value">AED 125,000</div>
<div class="mileage">120,000 km</div>
<div class="year">2018</div>
<div class="spec">GCC Spec</div>
<div class="transmission">Automatic</div>
<div class="fuel">Petrol</div>
<div class="body-type">SUV</div>
<div class="color">White</div>
<div class="location">Dubai</div>
<div class="description">Well maintained GCC spec Land Cruiser</div>
<div class="seller">Al-Futtaim Motors</div>
</body></html>
"""


class TestDiscovery:
    def test_search_url_default(self):
        discovery = DubizzleDiscovery()
        url = discovery.search_url()
        assert "dubizzle.com" in url
        assert "used-cars" in url

    def test_search_url_with_make(self):
        discovery = DubizzleDiscovery()
        url = discovery.search_url(make="Toyota", model="Land Cruiser")
        assert "toyota" in url
        assert "land-cruiser" in url

    def test_search_url_with_page(self):
        discovery = DubizzleDiscovery()
        url = discovery.search_url(page=3)
        assert "page=3" in url

    def test_seed_urls(self):
        discovery = DubizzleDiscovery()
        seeds = discovery.seed_urls()
        assert len(seeds) == 6
        assert all("dubizzle.com" in s for s in seeds)

    def test_listing_url(self):
        discovery = DubizzleDiscovery()
        url = discovery.listing_url("123456")
        assert "123456" in url


class TestPagination:
    def test_basic_pagination(self):
        p = DubizzlePagination()
        p.start()
        assert p.next_page() == 1
        assert p.next_page() == 2
        assert p.current_page == 2

    def test_max_pages(self):
        config = DubizzleConfig(max_pages=3)
        p = DubizzlePagination(config)
        p.start()
        for _ in range(3):
            p.next_page()
        assert p.is_exhausted

    def test_checkpoint_roundtrip(self):
        p = DubizzlePagination()
        p.start()
        p.next_page()
        p.record_listings(25)
        state = p.checkpoint_state()
        p2 = DubizzlePagination()
        p2.restore_state(state)
        assert p2.current_page == 1


class TestListingExtractor:
    def test_extract_cards(self):
        doc = DOMDocument.from_html(SEARCH_HTML)
        extractor = DubizzleListingExtractor()
        cards = extractor.extract_cards(doc)
        assert len(cards) >= 2


class TestDetailExtractor:
    def test_extract_details(self):
        doc = DOMDocument.from_html(DETAIL_HTML)
        extractor = DubizzleDetailExtractor()
        details = extractor.extract(doc)
        assert details["make"] == "Toyota"
        assert details["model"] == "Land Cruiser"
        assert details["spec"] == "GCC Spec"
        assert details["transmission"] == "Automatic"


class TestMapper:
    def test_map_to_canonical(self):
        mapper = DubizzleMapper()
        data = {
            "make": "Toyota", "model": "Land Cruiser", "year": 2018,
            "price": 125000.0, "currency": "AED",
            "mileage_km": 120000, "spec": "GCC Spec",
            "transmission": "Automatic", "fuel_type": "Petrol",
            "body_type": "SUV", "color": "White",
            "location": "Dubai", "seller_name": "Al-Futtaim",
            "listing_id": "123456", "url": "https://dubizzle.com/listing/123456",
        }
        listing = mapper.map_to_canonical(data)
        assert listing.marketplace == MARKETPLACE_NAME
        assert listing.vehicle.make == "Toyota"
        assert listing.vehicle.model == "Land Cruiser"
        assert listing.pricing.amount == 125000.0


class TestPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_with_mock_fetcher(self):
        """Full pipeline with mocked page fetcher."""
        async def mock_fetch(url):
            if "123456" in url:
                return DETAIL_HTML
            if "789012" in url:
                return DETAIL_HTML.replace("Toyota", "Nissan").replace("Land Cruiser", "Patrol")
            # Search page (first page or any page) — return search results
            if "used-cars" in url:
                return SEARCH_HTML
            return "<html><body>No listings</body></html>"

        pipeline = DubizzlePipeline(DubizzleConfig(max_pages=1))
        listings = await pipeline.run(mock_fetch)
        assert len(listings) >= 1
        listing = listings[0]
        assert listing.marketplace == MARKETPLACE_NAME
