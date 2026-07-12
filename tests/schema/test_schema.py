"""Test canonical listing schema — models, validation, enums, serialization."""
import pytest
from schema.listing import CanonicalListing
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from schema.location import Location
from schema.seller import Seller
from schema.images import Images
from schema.history import VehicleHistory
from schema.validation import SchemaValidator
from schema.enums import Marketplace, FuelType, Currency, Country, Specification


@pytest.fixture
def valid_listing():
    return CanonicalListing(
        marketplace=Marketplace.DUBIZZLE_UAE,
        marketplace_listing_id="dub-12345",
        listing_url="https://dubizzle.com/listing/12345",
        vehicle=Vehicle(
            make="Toyota", model="Land Cruiser", year=2018,
            mileage_km=120000, body_type="suv",
            fuel_type=FuelType.PETROL, transmission="automatic",
            specification=Specification.GCC,
        ),
        pricing=Pricing(amount=125000.0, currency=Currency.AED),
        location=Location(country=Country.AE, city="Dubai"),
        seller=Seller(seller_type="dealer", seller_name="Al-Futtaim"),
        images=Images(cover_image="https://img.example.com/car.jpg", image_count=8),
    )


class TestCanonicalListing:
    def test_create_valid_listing(self, valid_listing):
        assert valid_listing.marketplace == Marketplace.DUBIZZLE_UAE
        assert valid_listing.vehicle.make == "Toyota"
        assert valid_listing.pricing.amount == 125000.0

    def test_listing_id_is_generated(self):
        listing = CanonicalListing(
            marketplace="test", marketplace_listing_id="1",
            listing_url="https://example.com",
        )
        assert len(listing.listing_id) > 0

    def test_to_dict(self, valid_listing):
        d = valid_listing.to_dict()
        assert d["make"] == "Toyota"
        assert d["model"] == "Land Cruiser"
        assert d["year"] == 2018
        assert d["price_amount"] == 125000.0
        assert d["price_currency"] == "AED"
        assert d["country"] == "AE"
        assert d["city"] == "Dubai"
        assert d["mileage_km"] == 120000
        assert d["seller_type"] == "dealer"

    def test_empty_listing_has_defaults(self):
        listing = CanonicalListing()
        assert listing.vehicle.make == ""
        assert listing.pricing.amount == 0.0


class TestSubModels:
    def test_vehicle_defaults(self):
        v = Vehicle()
        assert v.make == ""
        assert v.mileage_km == 0

    def test_pricing_defaults(self):
        p = Pricing()
        assert p.currency == "AED"

    def test_location_defaults(self):
        loc = Location()
        assert loc.country == "AE"

    def test_seller_defaults(self):
        s = Seller()
        assert s.seller_type == "private"

    def test_images_defaults(self):
        img = Images()
        assert img.gallery == []

    def test_history_defaults(self):
        h = VehicleHistory()
        assert h.owners == 0


class TestValidation:
    def test_valid_listing_passes(self, valid_listing):
        validator = SchemaValidator()
        errors = validator.validate(valid_listing)
        assert len(errors) == 0
        assert validator.is_valid(valid_listing)

    def test_missing_make(self):
        validator = SchemaValidator()
        listing = CanonicalListing(
            marketplace="test",
            marketplace_listing_id="1",
            listing_url="https://example.com",
            vehicle=Vehicle(make=""),  # Missing
        )
        errors = validator.validate(listing)
        assert any("make" in e for e in errors)

    def test_negative_price(self):
        validator = SchemaValidator()
        listing = CanonicalListing(
            marketplace="test", marketplace_listing_id="1",
            listing_url="https://example.com",
            vehicle=Vehicle(make="Toyota", model="Camry", year=2020),
            pricing=Pricing(amount=-100),
        )
        errors = validator.validate(listing)
        assert any("positive" in e for e in errors)

    def test_future_year(self):
        validator = SchemaValidator()
        from datetime import datetime
        future = datetime.utcnow().year + 5
        listing = CanonicalListing(
            marketplace="test", marketplace_listing_id="1",
            listing_url="https://example.com",
            vehicle=Vehicle(make="Toyota", model="Camry", year=future),
            pricing=Pricing(amount=50000),
        )
        errors = validator.validate(listing)
        assert any("future" in e for e in errors)

    def test_invalid_currency(self):
        validator = SchemaValidator()
        listing = CanonicalListing(
            marketplace="test", marketplace_listing_id="1",
            listing_url="https://example.com",
            vehicle=Vehicle(make="Toyota", model="Camry", year=2020),
            pricing=Pricing(amount=50000, currency="XYZ"),
        )
        errors = validator.validate(listing)
        assert any("currency" in e for e in errors)

    def test_negative_mileage(self):
        validator = SchemaValidator()
        listing = CanonicalListing(
            marketplace="test", marketplace_listing_id="1",
            listing_url="https://example.com",
            vehicle=Vehicle(make="Toyota", model="Camry", year=2020, mileage_km=-1),
            pricing=Pricing(amount=50000),
        )
        errors = validator.validate(listing)
        assert any("mileage" in e for e in errors)


class TestEnums:
    def test_marketplace_values(self):
        assert Marketplace.DUBIZZLE_UAE == "dubizzle_uae"
        assert Marketplace.HARAJ == "haraj"

    def test_currency_values(self):
        assert Currency.AED == "AED"
        assert Currency.KWD == "KWD"

    def test_country_values(self):
        assert Country.AE == "AE"
        assert len(list(Country)) == 6  # All 6 GCC

    def test_fuel_types(self):
        assert FuelType.ELECTRIC == "electric"
