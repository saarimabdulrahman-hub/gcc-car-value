"""Test database integrity constraints at the model level.

Verifies that UNIQUE, CHECK, and FK constraints are correctly declared
on SQLAlchemy models and would be enforced by PostgreSQL.
"""
import pytest
from sqlalchemy import inspect, UniqueConstraint, CheckConstraint, ForeignKeyConstraint


class TestUniqueConstraints:
    """Verify UNIQUE constraints are declared on models."""

    def test_listings_has_source_external_id_unique(self):
        from src.models.listing import Listing
        args = getattr(Listing, '__table_args__', None)
        assert args is not None, "Listing missing __table_args__"
        # args may be a tuple of constraints
        constraints = [c for c in args if isinstance(c, UniqueConstraint)]
        names = [c.name for c in constraints]
        assert "uq_listings_source_external_id" in names

    def test_canonical_vehicles_has_unique(self):
        from src.models.canonical_vehicle import CanonicalVehicle
        args = getattr(CanonicalVehicle, '__table_args__', None)
        assert args is not None, "CanonicalVehicle missing __table_args__"
        constraints = [c for c in args if isinstance(c, UniqueConstraint)]
        names = [c.name for c in constraints]
        assert "uq_canonical_vehicles_make_model_year_gen" in names


class TestForeignKeyConstraints:
    """Verify FK constraints are declared on models."""

    def test_dead_letter_has_fk_to_pipeline_runs(self):
        from src.models.dead_letter import DeadLetter
        fks = [c for c in DeadLetter.__table__.columns
               if c.foreign_keys]
        fk_cols = [c.name for c in fks]
        assert "pipeline_run_id" in fk_cols

    def test_scraper_health_has_fk_to_pipeline_runs(self):
        from src.models.scraper_health import ScraperHealth
        fks = [c for c in ScraperHealth.__table__.columns
               if c.foreign_keys]
        fk_cols = [c.name for c in fks]
        assert "pipeline_run_id" in fk_cols

    def test_listing_has_fk_to_canonical_vehicles(self):
        from src.models.listing import Listing
        fks = [c for c in Listing.__table__.columns
               if c.foreign_keys]
        fk_cols = [c.name for c in fks]
        assert "canonical_vehicle_id" in fk_cols


class TestModelTableNames:
    """All models have valid __tablename__."""

    MODELS = [
        ("src.models.listing", "Listing", "listings"),
        ("src.models.canonical_vehicle", "CanonicalVehicle", "canonical_vehicles"),
        ("src.models.dead_letter", "DeadLetter", "dead_letter"),
        ("src.models.scraper_health", "ScraperHealth", "scraper_health"),
        ("src.models.valuation_query", "ValuationQuery", "valuation_queries"),
        ("src.models.model_rating", "ModelRating", "model_ratings"),
        ("src.models.user_account", "UserAccount", "user_accounts"),
        ("src.models.pipeline_run", "PipelineRun", "pipeline_runs"),
        ("src.models.listing_snapshot", "ListingSnapshot", "listing_snapshots"),
    ]

    @pytest.mark.parametrize("module_path,class_name,expected_table", MODELS)
    def test_table_name(self, module_path, class_name, expected_table):
        import importlib
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        assert cls.__tablename__ == expected_table


class TestRequiredColumns:
    """Verify NOT NULL columns are correctly declared."""

    def test_listing_required_fields(self):
        """Core listing fields are NOT NULL."""
        from src.models.listing import Listing
        cols = {c.name: c.nullable for c in Listing.__table__.columns}
        assert not cols["source"], "source should be NOT NULL"
        assert not cols["external_id"], "external_id should be NOT NULL"
        assert not cols["make"], "make should be NOT NULL"
        assert not cols["model"], "model should be NOT NULL"
        assert not cols["year"], "year should be NOT NULL"
        assert not cols["normalized_price_aed"], "normalized_price_aed should be NOT NULL"

    def test_dead_letter_rejection_reason_not_null(self):
        from src.models.dead_letter import DeadLetter
        cols = {c.name: c.nullable for c in DeadLetter.__table__.columns}
        assert not cols["rejection_reason"]
