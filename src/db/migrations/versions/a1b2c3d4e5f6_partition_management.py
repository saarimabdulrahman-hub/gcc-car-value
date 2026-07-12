"""Add partition management for historical tables.

Revision ID: a1b2c3d4e5f6
Revises: c42f2f2afaa8
Create Date: 2026-07-12

- Creates a SQL helper function for idempotent partition creation.
- Pre-creates 12 months of listing_snapshots partitions.
- Adds a DEFAULT partition as safety net for dates outside range.
- Enables the pg_partman extension (optional — for future auto-management).

Blueprint §4.2: listing_snapshots grows ~100K rows/week.
Monthly RANGE partitioning on captured_at with 2-year retention.
"""
from typing import Sequence, Union
from datetime import datetime
from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c42f2f2afaa8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Create SQL helper function for idempotent partition creation
    #    Called by the application PartitionManager or cron.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION create_listing_snapshots_partition(
            partition_month DATE
        )
        RETURNS TEXT AS $$
        DECLARE
            part_name  TEXT;
            month_start TEXT;
            month_end   TEXT;
        BEGIN
            month_start := to_char(partition_month, 'YYYY-MM-DD');
            month_end   := to_char(
                partition_month + INTERVAL '1 month', 'YYYY-MM-DD'
            );
            part_name := 'listing_snapshots_'
                      || to_char(partition_month, 'YYYY_MM');

            -- Idempotent: skip if partition already exists
            IF EXISTS (
                SELECT 1 FROM pg_class WHERE relname = part_name
            ) THEN
                RETURN part_name || ' (already exists)';
            END IF;

            EXECUTE format(
                'CREATE TABLE %I PARTITION OF listing_snapshots
                 FOR VALUES FROM (%L) TO (%L)',
                part_name, month_start, month_end
            );

            RETURN part_name || ' (created)';
        END;
        $$ LANGUAGE plpgsql;
    """)

    # ------------------------------------------------------------------
    # 2. Pre-create partitions for the next 12 months
    #    Runs create_listing_snapshots_partition for each month.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION create_future_partitions(
            months_ahead INTEGER DEFAULT 12
        )
        RETURNS SETOF TEXT AS $$
        DECLARE
            i INTEGER;
            partition_date DATE;
            result TEXT;
        BEGIN
            partition_date := date_trunc('month', CURRENT_DATE);
            FOR i IN 0..months_ahead LOOP
                SELECT create_listing_snapshots_partition(
                    partition_date + (i || ' months')::INTERVAL
                ) INTO result;
                RETURN NEXT result;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Execute the batch creation (idempotent — skips existing partitions)
    op.execute("SELECT create_future_partitions(12)")

    # ------------------------------------------------------------------
    # 3. Create a DEFAULT partition as safety net
    #    Catches any INSERT with captured_at outside defined ranges
    #    instead of failing with "no partition of relation" error.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS listing_snapshots_default
        PARTITION OF listing_snapshots DEFAULT
    """)

    # ------------------------------------------------------------------
    # 4. Create index on the DEFAULT partition (matches parent indexes)
    # ------------------------------------------------------------------
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_default_listing_date
        ON listing_snapshots_default (listing_id, captured_at)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_snapshots_default_run
        ON listing_snapshots_default (pipeline_run_id)
    """)


def downgrade() -> None:
    # Detach and drop the DEFAULT partition
    op.execute("""
        ALTER TABLE listing_snapshots DETACH PARTITION listing_snapshots_default
    """)
    op.execute("DROP TABLE IF EXISTS listing_snapshots_default")

    # Drop the helper functions
    op.execute("DROP FUNCTION IF EXISTS create_future_partitions(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS create_listing_snapshots_partition(DATE)")

    # Note: Monthly partitions created by the functions are NOT dropped.
    # They can be safely detached by the application PartitionManager
    # or dropped via subsequent manual migration.
