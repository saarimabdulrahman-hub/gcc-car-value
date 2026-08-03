"""add_performance_indexes

Revision ID: 1cbe748cf623
Revises: b7c8d9e0f1a2
Create Date: 2026-08-02 16:22:07.205818

Adds critical indexes on hot query paths and a missing FK constraint.
"""
from typing import Sequence, Union
from alembic import op

revision: str = "1cbe748cf623"
down_revision: Union[str, Sequence[str], None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # FK constraint on LineageMixin tables (Listing, ListingSnapshot)
    op.create_foreign_key(
        "fk_listings_pipeline_run",
        "listings", "pipeline_runs",
        ["pipeline_run_id"], ["run_id"],
    )

    # Hot-path indexes for valuation engine
    op.create_index("ix_listings_make_model_year", "listings", ["make", "model", "year"])
    op.create_index("ix_listings_country_make", "listings", ["country", "make", "model"])
    op.create_index("ix_listings_canonical_vehicle", "listings", ["canonical_vehicle_id"])

    # User-facing endpoints
    op.create_index("ix_saved_valuations_user_id", "saved_valuations", ["user_id"])
    op.create_index("ix_price_alerts_user_active", "price_alerts", ["user_id", "active"])

    # Monitoring queries
    op.create_index("ix_drift_events_acknowledged", "drift_events", ["acknowledged"])

    # Vehicle metadata lookups (valuation engine, knowledge base)
    op.create_index("ix_car_specs_make_model", "car_specs", ["make", "model"])
    op.create_index("ix_depreciation_curves_make_model", "depreciation_curves", ["make", "model"])
    op.create_index("ix_maintenance_costs_make_model", "maintenance_costs", ["make", "model"])

    # Cache lookup
    op.create_index("ix_valuation_queries_cache_key", "valuation_queries", ["cache_key"])


def downgrade() -> None:
    op.drop_constraint("fk_listings_pipeline_run", "listings", type_="foreignkey")
    op.drop_index("ix_listings_make_model_year", table_name="listings")
    op.drop_index("ix_listings_country_make", table_name="listings")
    op.drop_index("ix_listings_canonical_vehicle", table_name="listings")
    op.drop_index("ix_saved_valuations_user_id", table_name="saved_valuations")
    op.drop_index("ix_price_alerts_user_active", table_name="price_alerts")
    op.drop_index("ix_drift_events_acknowledged", table_name="drift_events")
    op.drop_index("ix_car_specs_make_model", table_name="car_specs")
    op.drop_index("ix_depreciation_curves_make_model", table_name="depreciation_curves")
    op.drop_index("ix_maintenance_costs_make_model", table_name="maintenance_costs")
    op.drop_index("ix_valuation_queries_cache_key", table_name="valuation_queries")
