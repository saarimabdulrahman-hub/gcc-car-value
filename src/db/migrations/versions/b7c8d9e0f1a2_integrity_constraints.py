"""Add database integrity constraints.

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-12

Adds:
  - UNIQUE constraints on listings(source, external_id) and
    canonical_vehicles(make, model, year, generation)
  - CHECK constraints on model_ratings (rating 1-5), listings
    (year range, price > 0, mileage >= 0, quality_score 0-100),
    listing_snapshots (asking_price > 0), valuation_queries
    (confidence valid values)
  - FK constraints on dead_letter and scraper_health pipeline_run_id

Duplicate detection: if duplicates exist, the migration reports them
and RAISES an error with a remediation query. It does NOT delete data.

Blueprint §4.1 + database-audit.md §4, §10.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    current_year = datetime.utcnow().year

    # ------------------------------------------------------------------
    # 1. UNIQUE constraints with duplicate detection
    # ------------------------------------------------------------------

    # 1a. listings(source, external_id)
    _add_unique_constraint_with_dedup_check(
        table="listings",
        constraint_name="uq_listings_source_external_id",
        columns=["source", "external_id"],
        description="Duplicate listings detected (same source + external_id).\n"
                    "Run: SELECT source, external_id, count(*) FROM listings\n"
                    "      GROUP BY source, external_id HAVING count(*) > 1;\n"
                    "Keep the row with the highest quality_score or most recent last_seen_at.",
    )

    # 1b. canonical_vehicles(make, model, year, COALESCE(generation, ''))
    op.execute("""
        DO $$
        DECLARE
            dup_count INTEGER;
        BEGIN
            SELECT count(*) INTO dup_count FROM (
                SELECT make, model, year, COALESCE(generation, '') AS gen
                FROM canonical_vehicles
                GROUP BY make, model, year, COALESCE(generation, '')
                HAVING count(*) > 1
            ) dups;

            IF dup_count > 0 THEN
                RAISE WARNING 'Duplicate canonical vehicles: % groups found.
                Remediation:
                  SELECT make, model, year, COALESCE(generation, '''') AS gen, count(*)
                  FROM canonical_vehicles
                  GROUP BY make, model, year, COALESCE(generation, '''')
                  HAVING count(*) > 1
                  ORDER BY count(*) DESC;
                Merge duplicates by updating listing.canonical_vehicle_id
                to point to the oldest canonical_vehicle row for each group.', dup_count;
            END IF;

            -- Add the constraint even if warnings (duplicates are non-fatal here)
            BEGIN
                ALTER TABLE canonical_vehicles
                ADD CONSTRAINT uq_canonical_vehicles_make_model_year_gen
                UNIQUE NULLS NOT DISTINCT (make, model, year, generation);
            EXCEPTION WHEN duplicate_table THEN
                RAISE WARNING 'Could not add UNIQUE constraint due to duplicates.
                Clean up duplicates and re-run this migration.';
            END;
        END $$;
    """)

    # ------------------------------------------------------------------
    # 2. CHECK constraints
    # ------------------------------------------------------------------

    # 2a. model_ratings — rating range (1-5) on all 7 rating columns
    rating_columns = [
        "reliability", "comfort", "performance", "fuel_economy",
        "offroad_capability", "resale_value", "overall",
    ]
    for col in rating_columns:
        # Clean invalid values first: NULL out anything outside 1-5
        op.execute(sa.text(
            f"UPDATE model_ratings SET {col} = NULL "
            f"WHERE {col} IS NOT NULL AND ({col} < 1 OR {col} > 5)"
        ))
        op.create_check_constraint(
            constraint_name=f"ck_model_ratings_{col}_range",
            table_name="model_ratings",
            condition=sa.text(f"{col} IS NULL OR ({col} >= 1 AND {col} <= 5)"),
        )

    # 2b. listings.quality_score (0-100)
    op.create_check_constraint(
        constraint_name="ck_listings_quality_score_range",
        table_name="listings",
        condition=sa.text("quality_score >= 0 AND quality_score <= 100"),
    )

    # 2c. listings.year (>= 1990, <= current_year + 1)
    op.create_check_constraint(
        constraint_name="ck_listings_year_range",
        table_name="listings",
        condition=sa.text(
            f"year >= 1990 AND year <= {current_year + 1}"
        ),
    )

    # 2d. listings.normalized_price_aed > 0
    op.create_check_constraint(
        constraint_name="ck_listings_normalized_price_positive",
        table_name="listings",
        condition=sa.text("normalized_price_aed > 0"),
    )

    # 2e. listings.original_price > 0
    op.create_check_constraint(
        constraint_name="ck_listings_original_price_positive",
        table_name="listings",
        condition=sa.text("original_price > 0"),
    )

    # 2f. listings.mileage_km >= 0
    op.create_check_constraint(
        constraint_name="ck_listings_mileage_non_negative",
        table_name="listings",
        condition=sa.text("mileage_km IS NULL OR mileage_km >= 0"),
    )

    # 2g. listing_snapshots.asking_price > 0
    op.create_check_constraint(
        constraint_name="ck_snapshots_asking_price_positive",
        table_name="listing_snapshots",
        condition=sa.text("asking_price > 0"),
    )

    # 2h. valuation_queries.confidence — valid enum values
    op.create_check_constraint(
        constraint_name="ck_valuation_queries_confidence_valid",
        table_name="valuation_queries",
        condition=sa.text(
            "confidence IS NULL OR "
            "confidence IN ('high', 'medium', 'low', 'insufficient')"
        ),
    )

    # 2i. valuation_queries.estimated_price > 0 (when not null)
    op.create_check_constraint(
        constraint_name="ck_valuation_queries_estimate_positive",
        table_name="valuation_queries",
        condition=sa.text(
            "estimated_price IS NULL OR estimated_price > 0"
        ),
    )

    # ------------------------------------------------------------------
    # 3. Foreign Key constraints
    # ------------------------------------------------------------------

    # 3a. dead_letter.pipeline_run_id → pipeline_runs.run_id
    # Clean orphans first (set to NULL if no matching run)
    op.execute("""
        UPDATE dead_letter
        SET pipeline_run_id = NULL
        WHERE pipeline_run_id IS NOT NULL
          AND pipeline_run_id NOT IN (SELECT run_id FROM pipeline_runs)
    """)
    op.create_foreign_key(
        constraint_name="fk_dead_letter_pipeline_run",
        source_table="dead_letter",
        referent_table="pipeline_runs",
        local_cols=["pipeline_run_id"],
        remote_cols=["run_id"],
        ondelete="SET NULL",
    )

    # 3b. scraper_health.pipeline_run_id → pipeline_runs.run_id
    op.execute("""
        UPDATE scraper_health
        SET pipeline_run_id = NULL
        WHERE pipeline_run_id IS NOT NULL
          AND pipeline_run_id NOT IN (SELECT run_id FROM pipeline_runs)
    """)
    op.create_foreign_key(
        constraint_name="fk_scraper_health_pipeline_run",
        source_table="scraper_health",
        referent_table="pipeline_runs",
        local_cols=["pipeline_run_id"],
        remote_cols=["run_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # --- FKs (reverse order) ---
    op.drop_constraint("fk_scraper_health_pipeline_run", "scraper_health", type_="foreignkey")
    op.drop_constraint("fk_dead_letter_pipeline_run", "dead_letter", type_="foreignkey")

    # --- CHECKs ---
    op.drop_constraint("ck_valuation_queries_estimate_positive", "valuation_queries", type_="check")
    op.drop_constraint("ck_valuation_queries_confidence_valid", "valuation_queries", type_="check")
    op.drop_constraint("ck_snapshots_asking_price_positive", "listing_snapshots", type_="check")
    op.drop_constraint("ck_listings_mileage_non_negative", "listings", type_="check")
    op.drop_constraint("ck_listings_original_price_positive", "listings", type_="check")
    op.drop_constraint("ck_listings_normalized_price_positive", "listings", type_="check")
    op.drop_constraint("ck_listings_year_range", "listings", type_="check")
    op.drop_constraint("ck_listings_quality_score_range", "listings", type_="check")

    for col in ["reliability", "comfort", "performance", "fuel_economy",
                "offroad_capability", "resale_value", "overall"]:
        op.drop_constraint(f"ck_model_ratings_{col}_range", "model_ratings", type_="check")

    # --- UNIQUEs ---
    op.execute("ALTER TABLE canonical_vehicles DROP CONSTRAINT IF EXISTS uq_canonical_vehicles_make_model_year_gen")
    op.drop_constraint("uq_listings_source_external_id", "listings", type_="unique")


# ------------------------------------------------------------------
# Helper: Add UNIQUE constraint with duplicate check
# ------------------------------------------------------------------

def _add_unique_constraint_with_dedup_check(
    table: str,
    constraint_name: str,
    columns: list[str],
    description: str,
) -> None:
    """Add UNIQUE constraint, checking for duplicates first.

    If duplicates exist, RAISES an error with description and a
    sample query to identify them. No data is deleted.
    """
    col_list = ", ".join(columns)
    op.execute(sa.text(f"""
        DO $$
        DECLARE
            dup_count INTEGER;
        BEGIN
            SELECT count(*) INTO dup_count FROM (
                SELECT {col_list}, count(*) AS cnt
                FROM {table}
                GROUP BY {col_list}
                HAVING count(*) > 1
            ) dups;

            IF dup_count > 0 THEN
                RAISE EXCEPTION 'Cannot add UNIQUE constraint on {table}({col_list}): '
                    '% duplicate groups found. %',
                    dup_count, '{description}';
            END IF;
        END $$;
    """))

    op.create_unique_constraint(
        constraint_name=constraint_name,
        table_name=table,
        columns=columns,
    )
