"""Test canonicalization engine — make, model, transmission, fuel, body, color, spec, location normalization."""
import pytest
from schema.listing import CanonicalListing
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from schema.location import Location
from normalization.engine import NormalizationEngine
from normalization.models import NormalizationReport, FieldNormalization


@pytest.fixture
def engine():
    return NormalizationEngine()


def make_listing(**overrides) -> CanonicalListing:
    """Factory for a listing with defaults."""
    v = Vehicle(make="Toyota", model="Land Cruiser", year=2018, mileage_km=120000)
    p = Pricing(amount=125000.0, currency="AED")
    loc = Location(country="AE", city="Dubai")
    for k, v_ in overrides.items():
        if hasattr(v, k): setattr(v, k, v_)
        elif hasattr(p, k): setattr(p, k, v_)
        elif hasattr(loc, k): setattr(loc, k, v_)
    return CanonicalListing(
        marketplace="test", marketplace_listing_id="1",
        listing_url="https://example.com",
        vehicle=v, pricing=p, location=loc,
    )


class TestMakeNormalization:
    def test_lowercase(self, engine):
        listing = make_listing(make="toyota")
        report = engine.normalize(listing)
        assert listing.vehicle.make == "Toyota"

    def test_alias(self, engine):
        listing = make_listing(make="toyota motors")
        report = engine.normalize(listing)
        assert listing.vehicle.make == "Toyota"

    def test_vw_alias(self, engine):
        listing = make_listing(make="vw")
        report = engine.normalize(listing)
        assert listing.vehicle.make == "Volkswagen"

    def test_unknown_title_cased(self, engine):
        listing = make_listing(make="some unknown brand")
        report = engine.normalize(listing)
        assert listing.vehicle.make == "Some Unknown Brand"


class TestModelNormalization:
    def test_land_cruiser_alias(self, engine):
        listing = make_listing(make="Toyota", model="landcruiser")
        report = engine.normalize(listing)
        assert listing.vehicle.model == "Land Cruiser"

    def test_lc_shortcut(self, engine):
        listing = make_listing(make="Toyota", model="lc")
        report = engine.normalize(listing)
        assert listing.vehicle.model == "Land Cruiser"

    def test_nissan_patrol(self, engine):
        listing = make_listing(make="Nissan", model="patrol safari")
        report = engine.normalize(listing)
        assert listing.vehicle.model == "Patrol"

    @pytest.mark.parametrize("raw,expected", [
        ("cx5", "CX-5"), ("cx 5", "CX-5"), ("cx-5", "CX-5"),
    ])
    def test_mazda_cx5_variants(self, engine, raw, expected):
        listing = make_listing(make="Mazda", model=raw)
        engine.normalize(listing)
        assert listing.vehicle.model == expected


class TestTransmissionNormalization:
    @pytest.mark.parametrize("raw,expected", [
        ("auto", "automatic"), ("at", "automatic"), ("a/t", "automatic"),
        ("manual", "manual"), ("mt", "manual"),
        ("cvt", "cvt"), ("dsg", "dct"), ("tiptronic", "automatic"),
    ])
    def test_transmission_variants(self, engine, raw, expected):
        listing = make_listing(transmission=raw)
        engine.normalize(listing)
        assert listing.vehicle.transmission == expected


class TestFuelNormalization:
    @pytest.mark.parametrize("raw,expected", [
        ("gasoline", "petrol"), ("gas", "petrol"), ("petrol", "petrol"),
        ("diesel", "diesel"), ("hybrid", "hybrid"), ("ev", "electric"),
    ])
    def test_fuel_variants(self, engine, raw, expected):
        listing = make_listing(fuel_type=raw)
        engine.normalize(listing)
        assert listing.vehicle.fuel_type == expected


class TestSpecNormalization:
    @pytest.mark.parametrize("raw,expected", [
        ("gcc spec", "GCC"), ("gulf spec", "GCC"), ("خليجي", "GCC"),
        ("american spec", "US"), ("us spec", "US"),
        ("japanese", "Japan"), ("ياباني", "Japan"),
        ("european", "European"), ("euro", "European"),
    ])
    def test_spec_variants(self, engine, raw, expected):
        listing = make_listing(specification=raw)
        engine.normalize(listing)
        assert listing.vehicle.specification == expected


class TestColorNormalization:
    @pytest.mark.parametrize("raw,expected", [
        ("pearl white", "White"), ("super white", "White"),
        ("midnight black", "Black"), ("jet black", "Black"),
        ("graphite", "Grey"), ("champagne", "Gold"),
    ])
    def test_color_variants(self, engine, raw, expected):
        listing = make_listing(color=raw)
        engine.normalize(listing)
        assert listing.vehicle.color == expected


class TestLocationNormalization:
    @pytest.mark.parametrize("raw,expected", [
        ("dubai", "Dubai"), ("دبي", "Dubai"),
        ("abu dhabi", "Abu Dhabi"), ("rak", "Ras Al Khaimah"),
        ("riyadh", "Riyadh"), ("makkah", "Mecca"),
    ])
    def test_city_variants(self, engine, raw, expected):
        listing = make_listing(city=raw)
        engine.normalize(listing)
        assert listing.location.city == expected


class TestMileageUnitConversion:
    def test_miles_to_km(self, engine):
        listing = make_listing(mileage_km=50000, mileage_unit="miles")
        engine.normalize(listing)
        assert listing.vehicle.mileage_km == int(50000 * 1.60934)
        assert listing.vehicle.mileage_unit == "km"


class TestNormalizationReport:
    def test_report_tracks_changes(self, engine):
        listing = make_listing(make="toyota", model="lc", color="pearl white",
                             specification="gulf spec", transmission="auto",
                             fuel_type="gasoline", body_type="4x4",
                             city="rak")
        report = engine.normalize(listing)
        assert isinstance(report, NormalizationReport)
        assert report.total_fields > 0
        assert report.changed_fields > 0

    def test_originals_preserved_in_metadata(self, engine):
        listing = make_listing(make="toyota motors")
        engine.normalize(listing)
        assert "original_values" in listing.metadata
        assert listing.metadata["original_values"]["make"] == "toyota motors"

    def test_unchanged_fields_not_changed(self, engine):
        listing = make_listing(make="Toyota", model="Camry")
        report = engine.normalize(listing)
        make_field = [f for f in report.fields if f.field == "make"][0]
        assert make_field.original == make_field.normalized
