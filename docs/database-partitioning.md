# GCC Car Value — Database Partitioning Strategy

**Date:** 2026-07-12  
**PostgreSQL Version:** 16  
**Blueprint Reference:** §4.2 Table Partitioning Strategy

---

## 1. Overview

High-volume historical tables use PostgreSQL native RANGE partitioning by month. Partitioning improves:

- **Query performance** — partition pruning excludes irrelevant partitions from sequential scans
- **Maintenance** — `VACUUM`, `ANALYZE`, and `REINDEX` can target individual partitions
- **Archival** — old partitions can be detached and backed up without locking active data
- **Data lifecycle** — expired partitions are dropped or archived independently

## 2. Partitioned Tables

| Table | Partition Key | Interval | Weekly Volume | Retention | Strategy |
|-------|--------------|----------|---------------|-----------|----------|
| `listing_snapshots` | `captured_at` | Monthly RANGE | ~100K rows | 24 months | Detach → archive → drop |

### Tables NOT Partitioned (and why)

| Table | Reason |
|-------|--------|
| `listings` | Bounded (~200K active, upserted). Index on `(make, model, year)` sufficient. |
| `valuation_queries` | Cache-key dedup limits growth. Index on `queried_at` for TTL cleanup. Consider partitioning when >10M rows. |
| `pipeline_runs` | ~50 rows/week. Will not reach meaningful size for years. |
| `scraper_health` | ~20 rows/week. Negligible volume. |
| `drift_events` | ~10 rows/week. Negligible volume. |
| `dead_letter` | Variable. Monitor; partition when >1M rows. |
| Knowledge base tables | Static seed data. Never grow significantly. |
| `user_accounts` | Unknown growth. Partition when >1M users. |

## 3. Partition Naming Convention

```
{parent_table}_{YYYY}_{MM}

Examples:
  listing_snapshots_2026_07
  listing_snapshots_2026_08
  listing_snapshots_2026_09
```

A **DEFAULT partition** (`listing_snapshots_default`) catches any INSERT with `captured_at` outside defined ranges. This prevents "no partition of relation" errors and alerts operators to missing partitions.

## 4. Partition Management

### 4.1 Automatic Partition Creation

**Method A — Python (preferred for scheduler integration):**

```bash
# Create partitions for the next 3 months
python -m src.db.partition_manager ensure-future --months 3

# Check status
python -m src.db.partition_manager status

# Archive expired (dry run first)
python -m src.db.partition_manager archive --dry-run
python -m src.db.partition_manager archive --retention 24
```

**Method B — SQL (for ad-hoc use):**

```sql
-- Create a specific month
SELECT create_listing_snapshots_partition('2026-09-01');

-- Batch create next 6 months
SELECT create_future_partitions(6);
```

### 4.2 Maintenance Schedule

| Frequency | Action | Command |
|-----------|--------|---------|
| **Monthly** | Create next month's partition | `python -m src.db.partition_manager ensure-future --months 1` |
| **Quarterly** | Archive partitions older than 24 months | `python -m src.db.partition_manager archive` |
| **Weekly** | Verify next partition exists | `python -m src.db.partition_manager status` |

**Recommended:** Run `ensure-future --months 3` via APScheduler or cron on the 1st of each month. Run `status` after each scraper pipeline to verify partition health.

### 4.3 Scheduler Integration (APScheduler)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.db.partition_manager import PartitionManager
from src.db.session import async_session_factory

async def ensure_partitions():
    async with async_session_factory() as session:
        mgr = PartitionManager(session)
        created = await mgr.ensure_future_partitions(months_ahead=3)
        if created:
            logger.info("monthly_partitions_created", count=len(created))

scheduler = AsyncIOScheduler()
scheduler.add_job(ensure_partitions, "cron", day=1, hour=3)
```

## 5. Retention Policy

```
listing_snapshots retention: 24 months

Month 0  (current):  Active — receives INSERTs
Month 1–23:          Active — queried for price history
Month 24+:           Detached — archived to S3 as Parquet, then dropped
```

### Archive Procedure

1. `PartitionManager.archive_expired_partitions(dry_run=True)` — preview
2. `PartitionManager.archive_expired_partitions()` — detaches old partitions
3. Detached partitions become standalone tables (e.g., `listing_snapshots_2024_07`)
4. Export to S3 as Parquet: `COPY listing_snapshots_2024_07 TO 's3://...' FORMAT PARQUET`
5. Drop standalone table: `DROP TABLE listing_snapshots_2024_07`

The DEFAULT partition should be monitored. If rows accumulate there, it indicates missing partition creation — investigate and backfill.

## 6. Migration Management

### Current Migrations

| Revision | Description |
|----------|-------------|
| `c42f2f2afaa8` | Initial schema — creates `listing_snapshots` with RANGE partitioning + 2 initial partitions (Jul+Aug 2026) |
| `a1b2c3d4e5f6` | Partition management — creates SQL helper functions + 12 months future partitions + DEFAULT partition |

### Adding Partitioning to a New Table

1. Create a new Alembic migration
2. Use `postgresql_partition_by="RANGE (column)"` in `op.create_table()`
3. Create initial partitions
4. Create a DEFAULT partition
5. Add the table to `PARTITION_CONFIG` in `partition_manager.py`
6. Update this document

Example migration fragment for a new partitioned table:

```python
op.create_table(
    "new_table",
    sa.Column("id", postgresql.UUID, primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    # ... other columns
    postgresql_partition_by="RANGE (created_at)",
)

# Initial 3 months of partitions
for month_offset in range(3):
    op.execute(f"""
        CREATE TABLE IF NOT EXISTS new_table_{formatted_month}
        PARTITION OF new_table
        FOR VALUES FROM ('{start}') TO ('{end}')
    """)

# DEFAULT partition
op.execute("CREATE TABLE IF NOT EXISTS new_table_default PARTITION OF new_table DEFAULT")
```

## 7. Performance

### Partition Pruning

PostgreSQL automatically prunes irrelevant partitions when `captured_at` appears in the WHERE clause:

```sql
EXPLAIN ANALYZE
SELECT * FROM listing_snapshots
WHERE listing_id = 'abc123'
  AND captured_at >= '2026-07-01'
  AND captured_at < '2026-08-01';
-- Only scans listing_snapshots_2026_07

EXPLAIN ANALYZE
SELECT * FROM listing_snapshots
WHERE captured_at >= CURRENT_DATE - INTERVAL '30 days';
-- Scans only partitions covering the last 30 days
```

### Index Strategy

Indexes on the parent table are inherited by all child partitions. Each partition maintains its own index storage, which keeps individual index sizes manageable.

### Monitoring Queries

```sql
-- Partition sizes
SELECT
    child.relname AS partition,
    pg_size_pretty(pg_total_relation_size(child.oid)) AS size,
    pg_stat_user_tables.n_live_tup AS estimated_rows
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child  ON pg_inherits.inhrelid = child.oid
LEFT JOIN pg_stat_user_tables ON pg_stat_user_tables.relid = child.oid
WHERE parent.relname = 'listing_snapshots'
ORDER BY child.relname;

-- Rows in DEFAULT partition (should be 0)
SELECT count(*) FROM listing_snapshots_default;

-- Check next month partition exists
SELECT 1 FROM pg_class
WHERE relname = 'listing_snapshots_' || to_char(CURRENT_DATE + INTERVAL '1 month', 'YYYY_MM');
```

## 8. Backward Compatibility

- **SQLAlchemy ORM:** Unchanged. Partitioned tables are transparent to the ORM — `SELECT`, `INSERT`, `UPDATE`, and `DELETE` work identically on partitioned and non-partitioned tables.
- **Existing queries:** No changes required. PostgreSQL routes queries to the correct partition automatically.
- **Migrations:** Fully reversible. The `a1b2c3d4e5f6` migration can be downgraded safely (drops functions + DEFAULT partition; does not drop monthly partitions).
- **No ORM model changes:** The `ListingSnapshot` model is unchanged. Partitioning is a DDL-only concern.

## 9. Future Considerations

### When to Partition Additional Tables

| Table | Threshold | Suggested Partition Key |
|-------|-----------|------------------------|
| `valuation_queries` | >10M rows or >1GB | `queried_at` (monthly, 12-month retention) |
| `dead_letter` | >1M rows | `created_at` (monthly, 6-month retention) |
| `pipeline_runs` | >500K rows | `started_at` (yearly) |

### pg_partman Extension

Consider installing `pg_partman` for fully automated partition management when the table count or partition volume grows beyond what the Python `PartitionManager` handles comfortably. The extension is already available in the `pgvector/pgvector:pg16` Docker image.

```sql
-- Future: automated partition management with pg_partman
CREATE EXTENSION IF NOT EXISTS pg_partman;

SELECT partman.create_parent(
    p_parent_table := 'public.valuation_queries',
    p_control := 'queried_at',
    p_type := 'native',
    p_interval := '1 month',
    p_premake := 3,
    p_start_partition := '2026-07-01'
);
```

---

*Partitioning strategy documented 2026-07-12.*
