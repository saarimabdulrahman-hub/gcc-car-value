"""initial schema

Revision ID: c42f2f2afaa8
Revises:
Create Date: 2026-07-04

Creates all 15 tables from the GCC Car Value Platform spec,
plus pgvector and uuid-ossp extensions.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c42f2f2afaa8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Required extensions (spec Section 11, Dockerfile)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Use declarative metadata to create all tables
    # This is the recommended pattern for initial schema from SQLAlchemy models
    from src.db.base import Base
    import src.models  # noqa: F401

    # Create all tables from metadata
    # Note: listing_snapshots is partitioned — created via partition DDL below
    Base.metadata.create_all(
        bind=op.get_bind(),
        tables=[t for t in Base.metadata.sorted_tables if t.name != "listing_snapshots"]
    )

    # Create partitioned listing_snapshots table manually
    op.create_table(
        "listing_snapshots",
        sa.Column("id", postgresql.UUID, primary_key=True),
        sa.Column("listing_id", postgresql.UUID, sa.ForeignKey("listings.id"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("asking_price", sa.Float, nullable=False),
        sa.Column("original_currency", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("days_on_market", sa.Integer),
        sa.Column("price_change_pct", sa.Float),
        sa.Column("schema_version", sa.Integer, nullable=False),
        sa.Column("parser_version", sa.Text, nullable=False),
        sa.Column("normalizer_version", sa.Text, nullable=False),
        sa.Column("pipeline_run_id", postgresql.UUID, nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        postgresql_partition_by="RANGE (captured_at)",
    )

    # Create initial monthly partitions
    op.execute("""
        CREATE TABLE IF NOT EXISTS listing_snapshots_2026_07
        PARTITION OF listing_snapshots
        FOR VALUES FROM ('2026-07-01') TO ('2026-08-01')
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS listing_snapshots_2026_08
        PARTITION OF listing_snapshots
        FOR VALUES FROM ('2026-08-01') TO ('2026-09-01')
    """)

    # Create all indexes
    op.create_index("idx_listings_source_external", "listings", ["source", "external_id"])
    op.create_index("idx_listings_make_model_year", "listings", ["make", "model", "year"])
    op.create_index("idx_listings_status", "listings", ["status"])
    op.create_index("idx_listings_country_city", "listings", ["country", "city"])
    op.create_index("idx_listings_quality", "listings", ["quality_score"])
    op.create_index("idx_listings_canonical", "listings", ["canonical_vehicle_id"])
    op.create_index("idx_listings_pipeline_run", "listings", ["pipeline_run_id"])
    op.create_index("idx_snapshots_listing_date", "listing_snapshots", ["listing_id", "captured_at"])
    op.create_index("idx_snapshots_run", "listing_snapshots", ["pipeline_run_id"])
    op.create_index("idx_valuation_cache", "valuation_queries", ["cache_key"])
    op.create_index("idx_valuation_queried_at", "valuation_queries", ["queried_at"])
    op.create_index("idx_pipeline_runs_started", "pipeline_runs", ["started_at"])
    op.create_index("idx_drift_detected", "drift_events", ["detected_at", "drift_type"])


def downgrade() -> None:
    op.drop_table("listing_snapshots")
    # Remaining tables dropped via metadata
    from src.db.base import Base
    import src.models  # noqa: F401
    Base.metadata.drop_all(bind=op.get_bind())
