# GCC Car Value — Database Integrity Constraints

**Date:** 2026-07-12  
**Migration:** `b7c8d9e0f1a2_integrity_constraints.py`  
**Blueprint Reference:** §4.1 (Core Schema)  

---

## 1. Constraints Added

### 1.1 UNIQUE Constraints

| Table | Constraint | Columns | Rationale |
|-------|-----------|---------|-----------|
| `listings` | `uq_listings_source_external_id` | `source`, `external_id` | Prevent duplicate listings from concurrent scraper runs. The promoter previously used SELECT-then-UPSERT with no atomic guarantee. |
| `canonical_vehicles` | `uq_canonical_vehicles_make_model_year_gen` | `make`, `model`, `year`, `generation` | Cross-source dedup anchor. Same vehicle on Dubizzle + YallaMotor must map to one canonical row. Uses `UNIQUE NULLS NOT DISTINCT` so multiple NULL generations for the same make/model/year are treated as duplicates. |

### 1.2 CHECK Constraints

| Table | Constraint | Condition | Rationale |
|-------|-----------|-----------|-----------|
| `model_ratings` | `ck_model_ratings_{col}_range` × 7 | `col IS NULL OR (col >= 1 AND col <= 5)` | Rating columns must be in valid range. NULL allowed (unrated dimension). Existing values outside 1-5 are NULL'd before constraint is added. |
| `listings` | `ck_listings_quality_score_range` | `quality_score >= 0 AND quality_score <= 100` | Quality scores must be in valid range. Prevents negative or >100 scores from buggy scrapers. |
| `listings` | `ck_listings_year_range` | `year >= 1990 AND year <= {current+1}` | Year must be plausible. Allows next-year models but rejects 1899 or 3000. |
| `listings` | `ck_listings_normalized_price_positive` | `normalized_price_aed > 0` | Price must be positive. Rejects 0-AED listings (test posts, errors). |
| `listings` | `ck_listings_original_price_positive` | `original_price > 0` | Original price must be positive. |
| `listings` | `ck_listings_mileage_non_negative` | `mileage_km IS NULL OR mileage_km >= 0` | Mileage must not be negative. NULL allowed (unknown mileage). |
| `listing_snapshots` | `ck_snapshots_asking_price_positive` | `asking_price > 0` | Snapshot prices must be positive. |
| `valuation_queries` | `ck_valuation_queries_confidence_valid` | `confidence IN ('high','medium','low','insufficient')` | Confidence must be a valid enum value. |
| `valuation_queries` | `ck_valuation_queries_estimate_positive` | `estimated_price IS NULL OR estimated_price > 0` | Cached estimates must be positive. |

**Total: 16 CHECK constraints across 4 tables.**

### 1.3 Foreign Key Constraints

| Child Table | Column | Parent Table | ON DELETE | Rationale |
|-------------|--------|-------------|-----------|-----------|
| `dead_letter` | `pipeline_run_id` | `pipeline_runs.run_id` | `SET NULL` | Orphaned dead letters lose their run reference but are preserved for debugging. |
| `scraper_health` | `pipeline_run_id` | `pipeline_runs.run_id` | `SET NULL` | Orphaned health records lose their run reference but are preserved for trend analysis. |

**Before migration:** Orphaned rows (where `pipeline_run_id` doesn't match any `pipeline_runs.run_id`) are set to NULL. This prevents the FK constraint from failing on existing data.

## 2. Duplicate Detection Strategy

The migration uses a `_add_unique_constraint_with_dedup_check()` helper that:

1. **Counts duplicates** before adding the constraint
2. **Raises an error** if duplicates exist (with a sample query to find them)
3. **Does NOT delete data** — the operator must manually review and merge duplicates

### Duplicate Resolution Queries

```sql
-- Find duplicate listings (same source + same external ID)
SELECT source, external_id, count(*)
FROM listings
GROUP BY source, external_id
HAVING count(*) > 1;

-- Remove duplicate listings (keep the one with highest quality_score)
DELETE FROM listings
WHERE id IN (
    SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY source, external_id
                   ORDER BY quality_score DESC, last_seen_at DESC
               ) AS rn
        FROM listings
    ) ranked
    WHERE rn > 1
);

-- Find duplicate canonical vehicles
SELECT make, model, year, COALESCE(generation, '') AS gen, count(*)
FROM canonical_vehicles
GROUP BY make, model, year, COALESCE(generation, '')
HAVING count(*) > 1;
```

## 3. Before/After Comparison

| Aspect | Before | After |
|--------|--------|-------|
| Duplicate listing prevention | Application-level SELECT-then-UPSERT (race condition) | PostgreSQL UNIQUE constraint (atomic) |
| Rating value enforcement | None (any float accepted) | CHECK (1-5 range) |
| Year validation | Pandera schema at ingestion layer only | CHECK at database layer (defense in depth) |
| Price validation | Pandera schema at ingestion layer only | CHECK at database layer |
| FK integrity for dead_letter | None (orphans possible) | FK with SET NULL on delete |
| FK integrity for scraper_health | None (orphans possible) | FK with SET NULL on delete |
| Confidence values | Free-text, any value accepted | Enforced enum via CHECK |

## 4. Model Updates

SQLAlchemy models were updated to reflect the new constraints:

- `Listing.__table_args__` — `UniqueConstraint("source", "external_id")`
- `CanonicalVehicle.__table_args__` — `UniqueConstraint("make", "model", "year", "generation")`
- `DeadLetter.pipeline_run_id` — added `ForeignKey("pipeline_runs.run_id", ondelete="SET NULL")`, changed to `nullable=True`
- `ScraperHealth.pipeline_run_id` — added `ForeignKey("pipeline_runs.run_id", ondelete="SET NULL")`, changed to `nullable=True`

## 5. Migration

```
Revision: b7c8d9e0f1a2
Depends on: a1b2c3d4e5f6 (partition management)
Chain: c42f2f2afaa8 -> a1b2c3d4e5f6 -> b7c8d9e0f1a2
```

**Upgrade:** Adds 2 UNIQUE + 16 CHECK + 2 FK constraints. Orphan cleanup before FKs. Rating outliers NULL'd before CHECKs.

**Downgrade:** Drops all constraints in reverse order. Data is preserved — downgrade only removes the constraint enforcement, not the data.

## 6. Backward Compatibility

- **Existing valid data:** Unaffected — constraints only reject new invalid data
- **Existing invalid data:** Rating outliers (>5 or <1) are set to NULL before CHECK is added. Orphaned FK references are set to NULL.
- **Application code:** No changes required — the promoter's upsert logic still works, but the DB now provides a safety net
- **API:** No changes — endpoints are unaware of constraint enforcement

---

*Database integrity documented 2026-07-12.*
