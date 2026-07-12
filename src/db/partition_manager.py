"""PostgreSQL partition management for high-volume historical tables.

Blueprint §4.2: listing_snapshots is partitioned by RANGE (captured_at) monthly.
This module provides idempotent partition creation, archival, and status.

Usage from scheduler or CLI:
    from src.db.partition_manager import PartitionManager
    async with async_session_factory() as session:
        mgr = PartitionManager(session)
        await mgr.ensure_future_partitions(months_ahead=3)
        await mgr.get_partition_status()
"""

from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = structlog.get_logger()


def _add_months(dt: datetime, months: int) -> datetime:
    """Add N months to a datetime, clamping day-of-month to valid range."""
    import calendar
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

# ---------------------------------------------------------------------------
# Partition configuration
# ---------------------------------------------------------------------------

PARTITION_CONFIG = {
    "listing_snapshots": {
        "partition_column": "captured_at",
        "interval": "monthly",          # RANGE monthly
        "retention_months": 24,          # Keep 2 years of partitions
        "future_months": 3,             # Pre-create 3 months ahead
        "archive_strategy": "detach",   # detach (keep table) or drop
        "description": "Per-listing weekly price snapshots — ~100K rows/week",
    },
    # Future tables to partition when they grow:
    # "valuation_queries": {
    #     "partition_column": "queried_at",
    #     "interval": "monthly",
    #     "retention_months": 12,
    #     "future_months": 1,
    #     "archive_strategy": "drop",
    #     "description": "Idempotent valuation cache — TTL 24h",
    # },
}


class PartitionManager:
    """Manage PostgreSQL native RANGE partitions for historical tables."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def ensure_future_partitions(
        self,
        table_name: str = "listing_snapshots",
        months_ahead: int | None = None,
    ) -> list[str]:
        """Create partitions for the next N months. Idempotent.

        Returns list of partition names created (empty if all exist).
        """
        config = PARTITION_CONFIG[table_name]
        months = months_ahead or config["future_months"]
        created = []

        for i in range(months + 1):  # +1 includes current month
            partition_date = _add_months(datetime.utcnow().replace(day=1), i)
            partition_name = await self._create_partition_if_not_exists(
                table_name, partition_date
            )
            if partition_name:
                created.append(partition_name)

        if created:
            logger.info("partitions_created", table=table_name, count=len(created),
                        partitions=created)
        return created

    async def archive_expired_partitions(
        self,
        table_name: str = "listing_snapshots",
        retention_months: int | None = None,
        dry_run: bool = False,
    ) -> list[str]:
        """Detach partitions older than retention period.

        Detached partitions remain as standalone tables (can be backed up
        and dropped later). Use dry_run=True to preview without executing.
        """
        config = PARTITION_CONFIG[table_name]
        retention = retention_months or config["retention_months"]
        cutoff = _add_months(datetime.utcnow().replace(day=1), -retention)

        expired = await self._get_expired_partitions(table_name, cutoff)
        if not expired:
            return []

        if dry_run:
            logger.info("archive_dry_run", table=table_name,
                        partitions=expired, cutoff=cutoff.isoformat())
            return []

        detached = []
        for part_name, part_from, _ in expired:
            await self._detach_partition(table_name, part_name)
            detached.append(part_name)

        if detached:
            logger.info("partitions_archived", table=table_name,
                        count=len(detached), partitions=detached)
        return detached

    async def get_partition_status(
        self,
        table_name: str = "listing_snapshots",
    ) -> dict:
        """Return partition metadata for monitoring."""
        rows = await self.session.execute(text("""
            SELECT
                pg_class.relname                          AS partition_name,
                pg_get_expr(pg_class.relpartbound, pg_class.oid) AS range_bounds,
                pg_stat_user_tables.n_live_tup            AS estimated_rows,
                pg_size_pretty(pg_total_relation_size(pg_class.oid)) AS total_size
            FROM pg_class
            JOIN pg_inherits
                ON pg_inherits.inhrelid = pg_class.oid
            JOIN pg_class AS parent
                ON pg_inherits.inhparent = parent.oid
            LEFT JOIN pg_stat_user_tables
                ON pg_stat_user_tables.relid = pg_class.oid
            WHERE parent.relname = :table_name
            ORDER BY partition_name
        """), {"table_name": table_name})

        partitions = []
        for row in rows:
            partitions.append({
                "name": row.partition_name,
                "bounds": row.range_bounds,
                "estimated_rows": row.estimated_rows or 0,
                "total_size": row.total_size or "0 bytes",
            })

        # Count total and find next missing partition
        total_partitions = len(partitions)
        now = datetime.utcnow()
        next_month = _add_months(now.replace(day=1), 1)
        expected_name = f"{table_name}_{next_month.strftime('%Y_%m')}"
        has_next = any(p["name"] == expected_name for p in partitions)

        # Find the furthest future partition
        furthest = partitions[-1]["name"] if partitions else None

        return {
            "table": table_name,
            "total_partitions": total_partitions,
            "next_month_ready": has_next,
            "next_expected": expected_name if not has_next else None,
            "furthest_partition": furthest,
            "partitions": partitions,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _create_partition_if_not_exists(
        self, table_name: str, partition_date: datetime
    ) -> str | None:
        """Create a single monthly partition if it doesn't exist.

        Returns partition name if created, None if already exists.
        """
        month_start = partition_date.strftime("%Y-%m-%d")
        month_end = _add_months(partition_date, 1).strftime("%Y-%m-%d")
        partition_name = f"{table_name}_{partition_date.strftime('%Y_%m')}"

        # Check if partition already exists
        result = await self.session.execute(text("""
            SELECT 1 FROM pg_class
            WHERE relname = :partition_name
        """), {"partition_name": partition_name})

        if result.scalar():
            return None

        # Create the partition
        await self.session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {partition_name}
            PARTITION OF {table_name}
            FOR VALUES FROM ('{month_start}') TO ('{month_end}')
        """))
        await self.session.commit()

        logger.debug("partition_created", table=table_name,
                     partition=partition_name,
                     range_from=month_start, range_to=month_end)
        return partition_name

    async def _get_expired_partitions(
        self, table_name: str, cutoff: datetime
    ) -> list[tuple[str, str, str]]:
        """List partitions whose range ends before the cutoff date."""
        rows = await self.session.execute(text("""
            SELECT
                child.relname AS partition_name,
                pg_get_expr(child.relpartbound, child.oid) AS bounds,
                child.relname
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child  ON pg_inherits.inhrelid = child.oid
            WHERE parent.relname = :table_name
              AND child.relname LIKE :pattern
            ORDER BY child.relname
        """), {"table_name": table_name, "pattern": f"{table_name}_20%_%"})

        expired = []
        for row in rows:
            # Extract the upper bound date from the partition bounds expression
            bounds_str = row.bounds or ""
            # Example: "FOR VALUES FROM ('2026-07-01') TO ('2026-08-01')"
            import re
            match = re.search(r"TO \('(\d{4}-\d{2}-\d{2})'\)", bounds_str)
            if match:
                upper_bound = datetime.strptime(match.group(1), "%Y-%m-%d")
                if upper_bound <= cutoff:
                    expired.append((row.partition_name, bounds_str,
                                   match.group(1)))

        return expired

    async def _detach_partition(self, table_name: str, partition_name: str):
        """Detach a partition from the parent table.

        The detached partition becomes a standalone table. It is NOT dropped —
        this allows backing up to S3 as Parquet before final cleanup.
        """
        await self.session.execute(text(
            f"ALTER TABLE {table_name} DETACH PARTITION {partition_name}"
        ))
        await self.session.commit()
        logger.info("partition_detached", table=table_name,
                    partition=partition_name)


# ==========================================================================
# CLI Entry Point — run via: python -m src.db.partition_manager
# ==========================================================================

async def _cli_main():
    """CLI for partition management. Intended for cron/scheduler use."""
    import argparse
    from src.db.session import async_session_factory

    parser = argparse.ArgumentParser(
        description="Manage PostgreSQL partitions for GCC Car Value"
    )
    sub = parser.add_subparsers(dest="command")

    # ensure-future
    p_ensure = sub.add_parser("ensure-future", help="Create future partitions")
    p_ensure.add_argument("--months", type=int, default=3,
                          help="Months ahead to create (default: 3)")
    p_ensure.add_argument("--table", default="listing_snapshots",
                          help="Table name (default: listing_snapshots)")

    # archive
    p_archive = sub.add_parser("archive", help="Archive expired partitions")
    p_archive.add_argument("--retention", type=int, default=24,
                           help="Retention in months (default: 24)")
    p_archive.add_argument("--dry-run", action="store_true",
                           help="Preview without detaching")
    p_archive.add_argument("--table", default="listing_snapshots",
                           help="Table name")

    # status
    p_status = sub.add_parser("status", help="Show partition status")
    p_status.add_argument("--table", default="listing_snapshots",
                          help="Table name (default: listing_snapshots)")

    args = parser.parse_args()

    async with async_session_factory() as session:
        mgr = PartitionManager(session)

        if args.command == "ensure-future":
            created = await mgr.ensure_future_partitions(args.table, args.months)
            if created:
                print(f"Created {len(created)} partition(s): {', '.join(created)}")
            else:
                print("All partitions already exist.")

        elif args.command == "archive":
            detached = await mgr.archive_expired_partitions(
                args.table, args.retention, dry_run=args.dry_run
            )
            if args.dry_run:
                print(f"[DRY RUN] Would archive: {', '.join(detached)}")
            elif detached:
                print(f"Archived {len(detached)} partition(s): {', '.join(detached)}")
            else:
                print("No expired partitions to archive.")

        elif args.command == "status":
            import json
            status = await mgr.get_partition_status(args.table)
            print(json.dumps(status, indent=2, default=str))

        else:
            parser.print_help()


if __name__ == "__main__":
    import asyncio
    asyncio.run(_cli_main())
