"""Test feature store — registry, catalog, store, dataset builder, validation."""
import pytest
from ml.features.registry import FeatureRegistry
from ml.features.feature_store import FeatureStore
from ml.features.models import FeatureDefinition, FeatureVector
from ml.features.validators import FeatureValidator
from ml.features.versioning import DatasetVersionManager
from ml.features.catalog import CATALOG
from ml.features.errors import DuplicateFeatureError, FeatureNotFoundError


class TestFeatureRegistry:
    def test_catalog_loaded(self):
        reg = FeatureRegistry()
        assert reg.count() >= 25
        assert "make" in reg.list_names()
        assert "price" in reg.list_names()
        assert "mileage_km" in reg.list_names()

    def test_get_feature(self):
        reg = FeatureRegistry()
        f = reg.get("year")
        assert f.dtype == "int64"
        assert f.valid_range == (1990, 2027)

    def test_duplicate_registration(self):
        reg = FeatureRegistry()
        with pytest.raises(DuplicateFeatureError):
            reg.register(FeatureDefinition("make", "duplicate make"))

    def test_get_nonexistent_raises(self):
        reg = FeatureRegistry()
        with pytest.raises(FeatureNotFoundError):
            reg.get("nonexistent_feature")

    def test_schema_version(self):
        reg = FeatureRegistry()
        v1 = reg.schema_version
        assert v1 > 0


class TestFeatureStore:
    def test_save_and_load(self):
        reg = FeatureRegistry()
        store = FeatureStore(reg)
        fv = FeatureVector(listing_id="l-1", fingerprint="fp-1",
                          values={"make": "Toyota", "price": 75000.0})
        store.save(fv)
        loaded = store.load("fp-1")
        assert loaded.values["make"] == "Toyota"

    def test_build_vector(self):
        reg = FeatureRegistry()
        store = FeatureStore(reg)
        fv = store.build_vector("fp-x", "l-x", make="Toyota", price=50000.0, year=2020)
        assert fv.values["make"] == "Toyota"
        assert fv.values["price"] == 50000.0

    def test_to_rows(self):
        reg = FeatureRegistry()
        store = FeatureStore(reg)
        store.save(FeatureVector(listing_id="l-1", fingerprint="fp-1",
                                values={"make": "Toyota", "price": 75000}))
        rows = store.to_rows()
        assert len(rows) == 1
        assert rows[0]["make"] == "Toyota"


class TestCatalog:
    def test_all_features_have_required_fields(self):
        for f in CATALOG:
            assert f.name, f"Feature has no name"
            assert f.dtype, f"Feature '{f.name}' has no dtype"
            assert f.source, f"Feature '{f.name}' has no source"

    def test_required_features(self):
        required = [f.name for f in CATALOG if f.required]
        assert "make" in required
        assert "model" in required
        assert "year" in required


class TestValidators:
    def test_valid_vector_passes(self):
        reg = FeatureRegistry()
        validator = FeatureValidator(reg)
        fv = FeatureVector(listing_id="l-1", fingerprint="fp-1",
                          values={"make": "Toyota", "model": "Camry", "year": 2020})
        errors = validator.validate_vector(fv)
        assert len(errors) == 0

    def test_range_violation(self):
        reg = FeatureRegistry()
        validator = FeatureValidator(reg)
        fv = FeatureVector(listing_id="l-1", fingerprint="fp-1",
                          values={"year": 3000})  # Above max 2027
        errors = validator.validate_vector(fv)
        assert any("year" in e and "range" in e.lower() for e in errors)


class TestVersioning:
    def test_version_manager(self):
        mgr = DatasetVersionManager()
        from ml.features.models import DatasetVersion
        v = DatasetVersion(dataset_id="test-1", row_count=100, feature_count=28)
        mgr.add_version(v)
        assert mgr.get_latest().row_count == 100
        assert len(mgr.get_all()) == 1
