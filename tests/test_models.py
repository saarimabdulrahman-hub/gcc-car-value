"""Verify all 15 database models are defined and discoverable."""


def test_all_expected_tables_in_metadata():
    """Every table from the spec DDL exists in Base.metadata."""
    import src.models  # noqa: F401 — triggers model registration
    from src.db.base import Base
    expected = {
        "canonical_vehicles", "listings", "listing_snapshots",
        "pipeline_runs", "dead_letter", "valuation_queries",
        "model_registry", "scraper_health", "drift_events",
        "feature_flags", "car_specs", "car_issues",
        "maintenance_costs", "depreciation_curves", "model_ratings",
    }
    actual = set(Base.metadata.tables.keys())
    missing = expected - actual
    assert not missing, f"Missing tables: {missing}"


def test_all_models_importable():
    """All 15 model classes exist and can be instantiated."""
    from src.models import (
        CanonicalVehicle, Listing, ListingSnapshot,
        PipelineRun, DeadLetter, ValuationQuery,
        ModelRegistry, ScraperHealth, DriftEvent,
        FeatureFlag, CarSpec, CarIssue,
        MaintenanceCost, DepreciationCurve, ModelRating,
    )
    classes = [
        CanonicalVehicle, Listing, ListingSnapshot,
        PipelineRun, DeadLetter, ValuationQuery,
        ModelRegistry, ScraperHealth, DriftEvent,
        FeatureFlag, CarSpec, CarIssue,
        MaintenanceCost, DepreciationCurve, ModelRating,
    ]
    for cls in classes:
        assert cls.__tablename__ is not None, f"{cls.__name__} has no __tablename__"


def test_listing_has_lineage_columns():
    """Listing model inherits LineageMixin — required by spec Section 3.3."""
    from src.models import Listing
    lineage_fields = {"schema_version", "parser_version", "normalizer_version",
                      "pipeline_run_id", "ingested_at"}
    columns = {c.name for c in Listing.__table__.columns}
    assert lineage_fields.issubset(columns), f"Missing lineage fields: {lineage_fields - columns}"


def test_listing_has_dual_currency():
    """Spec Section 3.4: original_price + original_currency + exchange_rate + normalized_price_aed."""
    from src.models import Listing
    currency_fields = {"original_price", "original_currency", "exchange_rate",
                       "exchange_timestamp", "normalized_price_aed"}
    columns = {c.name for c in Listing.__table__.columns}
    assert currency_fields.issubset(columns), f"Missing currency fields: {currency_fields - columns}"
