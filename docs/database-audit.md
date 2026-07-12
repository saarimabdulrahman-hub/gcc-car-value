# GCC Car Value Platform — Database Audit

**Date:** 2026-07-12  
**Migration:** `c42f2f2afaa8_initial_schema.py` (2026-07-04)  
**Engine:** PostgreSQL 16 + pgvector extension, SQLAlchemy 2.0 async  
**Tables:** 18 total (17 standard + 1 partitioned)

---

## 1. Schema Overview

### Entity-Relationship Summary

```
user_accounts ──< saved_valuations
user_accounts ──< price_alerts

canonical_vehicles ──< listings ──< listing_snapshots  [PARTITIONED BY RANGE (captured_at)]

pipeline_runs ──< listings           (via pipeline_run_id, no FK)
pipeline_runs ──< listing_snapshots   (via pipeline_run_id, FK exists)
pipeline_runs ──< dead_letter         (via pipeline_run_id, no FK)
pipeline_runs ──< scraper_health      (via pipeline_run_id, no FK)

valuation_queries     standalone
model_registry        standalone
drift_events          standalone
feature_flags         standalone
car_specs             standalone
car_issues            standalone
maintenance_costs     standalone
depreciation_curves   standalone
model_ratings         standalone
```

**Enforced FK constraints (5):**
- `listings.canonical_vehicle_id` → `canonical_vehicles.id`
- `listing_snapshots.listing_id` → `listings.id`
- `listing_snapshots.pipeline_run_id` → (implicit via LineageMixin — FK in DDL)
- `saved_valuations.user_id` → `user_accounts.id`
- `price_alerts.user_id` → `user_accounts.id`

**Logical FK (no constraint):**
- `dead_letter.pipeline_run_id` — references `pipeline_runs.run_id` but no FK constraint
- `scraper_health.pipeline_run_id` — references `pipeline_runs.run_id` but no FK constraint

---

## 2. Complete Table Definitions

### 2.1 `canonical_vehicles` — Cross-Source Deduplication Anchor

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | Primary key |
| 2 | `make` | TEXT | NOT NULL | — | Normalized make name |
| 3 | `model` | TEXT | NOT NULL | — | Normalized model name |
| 4 | `year` | INTEGER | NOT NULL | — | Manufacturing year |
| 5 | `generation` | TEXT | NULL | — | e.g. "J200 (2008-2021)" |
| 6 | `body_type` | TEXT | NULL | — | SUV, sedan, pickup |
| 7 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

**Implicit unique:** `(make, model, year, generation)` — specified in blueprint DDL but **not enforced** in model or migration.

**Referenced by:** `listings.canonical_vehicle_id`

---

### 2.2 `listings` — Core Production Table

Inherits `LineageMixin`: `schema_version`, `parser_version`, `normalizer_version`, `pipeline_run_id`, `ingested_at`

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `canonical_vehicle_id` | UUID (FK) | NULL | — | → `canonical_vehicles.id` |
| 3 | `source` | TEXT | NOT NULL | — | e.g. "dubizzle_uae" |
| 4 | `external_id` | TEXT | NOT NULL | — | Source's listing ID |
| 5 | `url` | TEXT | NULL | — | Original listing URL |
| 6 | `first_seen_at` | TIMESTAMPTZ | NOT NULL | — | |
| 7 | `last_seen_at` | TIMESTAMPTZ | NOT NULL | — | |
| 8 | `status` | TEXT | NOT NULL | — | active, inactive_pending, probably_sold, sold_confirmed, expired, delisted |
| 9 | `delisted_at` | TIMESTAMPTZ | NULL | — | |
| 10 | `delisting_confidence` | FLOAT | NULL | — | 0.0–1.0 |
| 11 | `make` | TEXT | NOT NULL | — | |
| 12 | `model` | TEXT | NOT NULL | — | |
| 13 | `year` | INTEGER | NOT NULL | — | |
| 14 | `trim` | TEXT | NULL | — | |
| 15 | `spec` | TEXT | NULL | — | GCC, US, Japan, European, Other |
| 16 | `body_type` | TEXT | NULL | — | |
| 17 | `transmission` | TEXT | NULL | — | |
| 18 | `fuel_type` | TEXT | NULL | — | |
| 19 | `engine_size` | FLOAT | NULL | — | Liters |
| 20 | `color` | TEXT | NULL | — | |
| 21 | `doors` | INTEGER | NULL | — | |
| 22 | `cylinders` | INTEGER | NULL | — | |
| 23 | `original_price` | FLOAT | NOT NULL | — | Price as scraped |
| 24 | `original_currency` | TEXT | NOT NULL | — | AED, SAR, KWD, QAR, BHD, OMR |
| 25 | `exchange_rate` | FLOAT | NOT NULL | — | Rate used for conversion |
| 26 | `exchange_timestamp` | TIMESTAMPTZ | NOT NULL | — | When rate was fetched |
| 27 | `normalized_price_aed` | FLOAT | NOT NULL | — | original_price × exchange_rate |
| 28 | `price_history` | JSONB | NULL | `[]` | [{date, price, currency}, ...] |
| 29 | `mileage_km` | INTEGER | NULL | — | |
| 30 | `warranty` | BOOLEAN | NULL | — | |
| 31 | `service_history` | BOOLEAN | NULL | — | |
| 32 | `seller_type` | TEXT | NULL | — | dealer, private, auction |
| 33 | `city` | TEXT | NOT NULL | — | |
| 34 | `country` | TEXT | NOT NULL | — | AE, SA, QA, KW, BH, OM |
| 35 | `quality_score` | INTEGER | NOT NULL | `0` | 0–100 |
| 36 | `quality_flags` | JSONB | NULL | `[]` | [{flag_reasons}] |
| 37 | `raw_data_s3_key` | TEXT | NULL | — | S3 key for raw HTML |
| — | `schema_version` | INTEGER | NOT NULL | — | † LineageMixin |
| — | `parser_version` | TEXT | NOT NULL | — | † |
| — | `normalizer_version` | TEXT | NOT NULL | — | † |
| — | `pipeline_run_id` | UUID | NOT NULL | — | † |
| — | `ingested_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | † |

**Implied unique:** `(source, external_id)` — specified in blueprint; **not an explicit UNIQUE constraint** in the ORM model, but enforced via upsert logic in `promoter.py`.

---

### 2.3 `listing_snapshots` — Price History (Partitioned)

Inherits `LineageMixin`. Partitioned by `RANGE (captured_at)`.

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | | |
| 2 | `listing_id` | UUID (FK) | NOT NULL | — | → `listings.id` |
| 3 | `captured_at` | TIMESTAMPTZ | NOT NULL | — | **Partition key** |
| 4 | `asking_price` | FLOAT | NOT NULL | — | |
| 5 | `original_currency` | TEXT | NOT NULL | — | |
| 6 | `status` | TEXT | NOT NULL | — | |
| 7 | `days_on_market` | INTEGER | NULL | — | Computed: captured_at − first_seen_at |
| 8 | `price_change_pct` | FLOAT | NULL | — | Delta from previous snapshot |
| — | `schema_version` | INTEGER | NOT NULL | — | † LineageMixin |
| — | `parser_version` | TEXT | NOT NULL | — | † |
| — | `normalizer_version` | TEXT | NOT NULL | — | † |
| — | `pipeline_run_id` | UUID | NOT NULL | — | † FK in DDL |
| — | `ingested_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | † |

**Relationship:** `ListingSnapshot.listing` ↔ `Listing.snapshots`

**Partitions (2 created, no auto-creation):**
- `listing_snapshots_2026_07`: 2026-07-01 → 2026-08-01
- `listing_snapshots_2026_08`: 2026-08-01 → 2026-09-01

**⚠️ Risk:** No partition auto-creation. INSERTs after August 2026 will fail.

---

### 2.4 `pipeline_runs` — Batch Execution Metadata

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `run_id` | UUID (UNIQUE) | NOT NULL | `uuid4()` | |
| 3 | `source` | TEXT | NULL | — | NULL for cross-source runs |
| 4 | `started_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |
| 5 | `completed_at` | TIMESTAMPTZ | NULL | — | |
| 6 | `duration_seconds` | INTEGER | NULL | — | |
| 7 | `pages_crawled` | INTEGER | NULL | `0` | |
| 8 | `records_ingested` | INTEGER | NULL | `0` | |
| 9 | `records_new` | INTEGER | NULL | `0` | |
| 10 | `records_updated` | INTEGER | NULL | `0` | |
| 11 | `records_promoted` | INTEGER | NULL | `0` | |
| 12 | `records_rejected` | INTEGER | NULL | `0` | |
| 13 | `duplicates_found` | INTEGER | NULL | `0` | |
| 14 | `quality_score_p50` | FLOAT | NULL | — | |
| 15 | `quality_score_p90` | FLOAT | NULL | — | |
| 16 | `quality_score_mean` | FLOAT | NULL | — | |
| 17 | `error_count` | INTEGER | NULL | `0` | |
| 18 | `errors` | JSONB | NULL | `[]` | |
| 19 | `success` | BOOLEAN | NULL | `False` | |
| 20 | `parser_version` | TEXT | NULL | — | |
| 21 | `normalizer_version` | TEXT | NULL | — | |
| 22 | `git_commit` | TEXT | NULL | — | |

**⚠️ Note:** Several columns use nullable `Integer` with `default=0` in the ORM. This means Python-level defaults work, but the DB column allows NULL. Rows inserted via raw SQL could have NULL instead of 0.

---

### 2.5 `dead_letter` — Rejected Records

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `source` | TEXT | NOT NULL | — | |
| 3 | `external_id` | TEXT | NULL | — | |
| 4 | `rejection_reason` | TEXT | NOT NULL | — | e.g. "quality_score_45_below_60" |
| 5 | `raw_data` | JSONB | NOT NULL | — | Full scraped record |
| 6 | `quality_score` | INTEGER | NULL | — | |
| 7 | `pipeline_run_id` | UUID | NOT NULL | — | Logical → pipeline_runs.run_id (no FK) |
| 8 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.6 `scraper_health` — Field-Level Extraction Statistics

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `pipeline_run_id` | UUID | NOT NULL | — | Logical FK (no constraint) |
| 3 | `source` | TEXT | NOT NULL | — | |
| 4 | `captured_at` | TIMESTAMPTZ | NOT NULL | — | |
| 5 | `pages_crawled` | INTEGER | NULL | — | |
| 6 | `listings_found` | INTEGER | NULL | — | |
| 7 | `listings_new` | INTEGER | NULL | — | |
| 8 | `listings_updated` | INTEGER | NULL | — | |
| 9 | `price_extracted_pct` | FLOAT | NULL | — | 0.0–100.0 |
| 10 | `year_extracted_pct` | FLOAT | NULL | — | |
| 11 | `mileage_extracted_pct` | FLOAT | NULL | — | |
| 12 | `spec_extracted_pct` | FLOAT | NULL | — | |
| 13 | `trim_extracted_pct` | FLOAT | NULL | — | |
| 14 | `city_extracted_pct` | FLOAT | NULL | — | |
| 15 | `body_type_extracted_pct` | FLOAT | NULL | — | |
| 16 | `transmission_extracted_pct` | FLOAT | NULL | — | |
| 17 | `parse_success_rate` | FLOAT | NULL | — | % pages that parsed without error |
| 18 | `avg_parse_time_ms` | FLOAT | NULL | — | |
| 19 | `html_structure_hash` | TEXT | NULL | — | Detect DOM changes |
| 20 | `selector_failures` | JSONB | NULL | — | [{selector, fail_count}] |
| 21 | `unexpected_layouts` | INTEGER | NULL | — | |
| 22 | `scraper_confidence` | FLOAT | NULL | — | Composite 0–100 |
| 23 | `errors` | JSONB | NULL | — | [{url, error_type, message}] |

---

### 2.7 `valuation_queries` — Idempotent Valuation Cache

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `cache_key` | TEXT (UNIQUE) | NOT NULL | — | SHA-256 of inputs + date |
| 3 | `queried_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |
| 4 | `make` | TEXT | NOT NULL | — | |
| 5 | `model` | TEXT | NOT NULL | — | |
| 6 | `year` | INTEGER | NOT NULL | — | |
| 7 | `mileage_km` | INTEGER | NULL | — | |
| 8 | `spec` | TEXT | NULL | — | |
| 9 | `trim` | TEXT | NULL | — | |
| 10 | `city` | TEXT | NULL | — | |
| 11 | `country` | TEXT | NULL | — | |
| 12 | `estimated_price` | FLOAT | NULL | — | |
| 13 | `price_low` | FLOAT | NULL | — | 10th percentile |
| 14 | `price_high` | FLOAT | NULL | — | 90th percentile |
| 15 | `comp_count` | INTEGER | NULL | — | |
| 16 | `confidence` | TEXT | NULL | — | high, medium, low |
| 17 | `model_version` | TEXT | NULL | — | e.g. "statistical_v1" |
| 18 | `model_type` | TEXT | NULL | — | statistical, lightgbm |
| 19 | `shap_values` | JSONB | NULL | — | **Never populated** |
| 20 | `feature_importance` | JSONB | NULL | — | **Never populated** |
| 21 | `adjustments` | JSONB | NULL | — | [{reason, amount, detail}] |
| 22 | `response_ms` | INTEGER | NULL | — | |
| 23 | `api_version` | TEXT | NULL | — | |
| 24 | `user_id` | TEXT | NULL | — | If authenticated |
| 25 | `ip_hash` | TEXT | NULL | — | SHA-256 of IP |

---

### 2.8 `model_registry` — ML Model Lifecycle

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `trained_at` | TIMESTAMPTZ | NOT NULL | — | |
| 3 | `model_type` | TEXT | NOT NULL | — | statistical, lightgbm |
| 4 | `model_path` | TEXT | NULL | — | Path to serialized model |
| 5 | `model_name` | TEXT | NOT NULL | — | e.g. "lightgbm_v20260712_1400" |
| 6 | `mae` | FLOAT | NULL | — | |
| 7 | `mape` | FLOAT | NULL | — | Mean absolute % error |
| 8 | `r2_score` | FLOAT | NULL | — | |
| 9 | `training_rows` | INTEGER | NULL | — | |
| 10 | `holdout_rows` | INTEGER | NULL | — | |
| 11 | `training_dataset_hash` | TEXT | NULL | — | SHA-256 of dataset |
| 12 | `feature_version` | TEXT | NULL | — | |
| 13 | `git_commit` | TEXT | NULL | — | |
| 14 | `hyperparameters` | JSONB | NULL | — | {n_estimators, max_depth, ...} |
| 15 | `training_config` | JSONB | NULL | — | |
| 16 | `features_used` | JSONB | NULL | — | List of feature names |
| 17 | `status` | TEXT | NOT NULL | `"training"` | training, evaluating, shadow, approved, active, rolled_back, archived |
| 18 | `shadow_started_at` | TIMESTAMPTZ | NULL | — | |
| 19 | `approved_at` | TIMESTAMPTZ | NULL | — | |
| 20 | `approved_by` | TEXT | NULL | — | |
| 21 | `activated_at` | TIMESTAMPTZ | NULL | — | |
| 22 | `rolled_back_at` | TIMESTAMPTZ | NULL | — | |
| 23 | `rollback_reason` | TEXT | NULL | — | |
| 24 | `shadow_query_count` | INTEGER | NULL | — | |
| 25 | `shadow_mae` | FLOAT | NULL | — | |
| 26 | `shadow_vs_active_pct` | FLOAT | NULL | — | Improvement vs active |

---

### 2.9 `drift_events` — Data/Model Drift Monitoring

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `detected_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |
| 3 | `drift_type` | TEXT | NOT NULL | — | feature, target, prediction, market |
| 4 | `feature_name` | TEXT | NULL | — | |
| 5 | `psi_value` | FLOAT | NULL | — | Population Stability Index |
| 6 | `baseline_period` | DATERANGE | NULL | — | |
| 7 | `current_period` | DATERANGE | NULL | — | |
| 8 | `threshold_exceeded` | BOOLEAN | NULL | — | |
| 9 | `details` | JSONB | NULL | — | |
| 10 | `acknowledged` | BOOLEAN | NULL | `False` | |

---

### 2.10 `feature_flags` — Feature Rollout Control

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `flag_name` | TEXT (UNIQUE) | NOT NULL | — | |
| 3 | `description` | TEXT | NULL | — | |
| 4 | `enabled` | BOOLEAN | NULL | `False` | |
| 5 | `rollout_pct` | INTEGER | NULL | `100` | 0–100 (% of traffic) |
| 6 | `target_users` | JSONB | NULL | — | Array of user IDs, NULL = all |
| 7 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |
| 8 | `updated_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.11 `car_specs` — Knowledge Base: Vehicle Specifications

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `make` | TEXT | NOT NULL | — | |
| 3 | `model` | TEXT | NOT NULL | — | |
| 4 | `generation` | TEXT | NULL | — | e.g. "J200 (2008-2021)" |
| 5 | `year_start` | INTEGER | NULL | — | |
| 6 | `year_end` | INTEGER | NULL | — | NULL = current |
| 7 | `trim` | TEXT | NULL | — | |
| 8 | `engine_options` | JSONB | NULL | — | [{size_L, cylinders, fuel, hp, torque}] |
| 9 | `transmission_options` | JSONB | NULL | — | [{type, gears}] |
| 10 | `drivetrain` | TEXT | NULL | — | 4WD, AWD, RWD, FWD |
| 11 | `fuel_economy_combined` | FLOAT | NULL | — | L/100km |
| 12 | `fuel_tank_capacity` | FLOAT | NULL | — | Liters |
| 13 | `seating_capacity` | INTEGER | NULL | — | |
| 14 | `cargo_volume_L` | FLOAT | NULL | — | |
| 15 | `safety_rating` | TEXT | NULL | — | e.g. "NCAP 5-star" |
| 16 | `warranty_years` | INTEGER | NULL | — | |
| 17 | `warranty_km` | INTEGER | NULL | — | |
| 18 | `source` | TEXT | NULL | — | JATO, manufacturer, manual, curated |
| 19 | `source_url` | TEXT | NULL | — | |
| 20 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.12 `car_issues` — Knowledge Base: Common Problems

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `make` | TEXT | NOT NULL | — | |
| 3 | `model` | TEXT | NOT NULL | — | |
| 4 | `generation` | TEXT | NULL | — | |
| 5 | `year_start` | INTEGER | NULL | — | |
| 6 | `year_end` | INTEGER | NULL | — | |
| 7 | `issue_title` | TEXT | NOT NULL | — | |
| 8 | `issue_description` | TEXT | NULL | — | |
| 9 | `severity` | TEXT | NULL | — | minor, moderate, major, critical |
| 10 | `typical_mileage_km` | INTEGER | NULL | — | When issue typically appears |
| 11 | `repair_cost_estimate` | FLOAT | NULL | — | AED |
| 12 | `source` | TEXT | NULL | — | drivearabia, reddit, forum, manual, curated |
| 13 | `source_url` | TEXT | NULL | — | |
| 14 | `confirmed` | BOOLEAN | NULL | `False` | |
| 15 | `confirmed_by_count` | INTEGER | NULL | `0` | |
| 16 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.13 `maintenance_costs` — Knowledge Base: Ownership Costs

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `make` | TEXT | NOT NULL | — | |
| 3 | `model` | TEXT | NOT NULL | — | |
| 4 | `generation` | TEXT | NULL | — | |
| 5 | `service_interval_km` | INTEGER | NULL | — | e.g. 10000 |
| 6 | `minor_service_cost` | FLOAT | NULL | — | AED |
| 7 | `major_service_cost` | FLOAT | NULL | — | AED |
| 8 | `common_repair_costs` | JSONB | NULL | — | [{repair, cost_range, mileage}] |
| 9 | `annual_insurance_estimate` | FLOAT | NULL | — | AED |
| 10 | `source` | TEXT | NULL | — | partsouq, dealer_menu, community, curated |
| 11 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.14 `depreciation_curves` — Knowledge Base: Value Retention

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `make` | TEXT | NOT NULL | — | |
| 3 | `model` | TEXT | NOT NULL | — | |
| 4 | `generation` | TEXT | NULL | — | |
| 5 | `msrp_aed` | FLOAT | NULL | — | Original manufacturer price |
| 6 | `residual_pct_year` | JSONB | NOT NULL | — | {1: 0.88, 2: 0.80, 3: 0.72, ...} |
| 7 | `computed_from_rows` | INTEGER | NULL | — | How many listings informed this |
| 8 | `last_updated` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.15 `model_ratings` — Knowledge Base: Consumer Ratings

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `make` | TEXT | NOT NULL | — | |
| 3 | `model` | TEXT | NOT NULL | — | |
| 4 | `generation` | TEXT | NULL | — | |
| 5 | `reliability` | FLOAT | NULL | — | 1–5 |
| 6 | `comfort` | FLOAT | NULL | — | 1–5 |
| 7 | `performance` | FLOAT | NULL | — | 1–5 |
| 8 | `fuel_economy` | FLOAT | NULL | — | 1–5 |
| 9 | `offroad_capability` | FLOAT | NULL | — | 1–5 |
| 10 | `resale_value` | FLOAT | NULL | — | 1–5 |
| 11 | `overall` | FLOAT | NULL | — | 1–5 |
| 12 | `rating_count` | INTEGER | NULL | `0` | |
| 13 | `source` | TEXT | NULL | — | computed, community, expert, curated |
| 14 | `last_updated` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

**⚠️ Note:** Blueprint DDL specifies `CHECK (rating BETWEEN 1 AND 5)` constraints on rating columns. These are **not enforced** in the model or migration.

---

### 2.16 `user_accounts` — User Authentication

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `email` | TEXT (UNIQUE) | NOT NULL | — | |
| 3 | `password_hash` | TEXT | NOT NULL | — | PBKDF2-SHA256, 100K iterations |
| 4 | `password_salt` | TEXT | NOT NULL | — | 16-byte hex |
| 5 | `tier` | TEXT | NOT NULL | `"registered"` | registered, enterprise |
| 6 | `api_key_hash` | TEXT | NULL | — | SHA-256 of API key |
| 7 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

**Referenced by:** `saved_valuations.user_id`, `price_alerts.user_id`

---

### 2.17 `saved_valuations` — User Bookmarks

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `user_id` | UUID (FK) | NOT NULL | — | → `user_accounts.id` |
| 3 | `make` | TEXT | NOT NULL | — | |
| 4 | `model` | TEXT | NOT NULL | — | |
| 5 | `year` | INTEGER | NOT NULL | — | |
| 6 | `mileage_km` | INTEGER | NULL | — | |
| 7 | `spec` | TEXT | NULL | — | |
| 8 | `city` | TEXT | NULL | — | |
| 9 | `country` | TEXT | NULL | — | |
| 10 | `estimated_price` | FLOAT | NULL | — | |
| 11 | `confidence` | TEXT | NULL | — | |
| 12 | `notes` | TEXT | NULL | — | |
| 13 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

### 2.18 `price_alerts` — Price Alert Subscriptions

| # | Column | Type | Nullable | Default | Notes |
|---|--------|------|----------|---------|-------|
| 1 | `id` | UUID (PK) | NOT NULL | `uuid4()` | |
| 2 | `user_id` | UUID (FK) | NOT NULL | — | → `user_accounts.id` |
| 3 | `make` | TEXT | NOT NULL | — | |
| 4 | `model` | TEXT | NOT NULL | — | |
| 5 | `year_min` | INTEGER | NULL | — | |
| 6 | `year_max` | INTEGER | NULL | — | |
| 7 | `country` | TEXT | NULL | — | |
| 8 | `target_price` | FLOAT | NULL | — | Alert when median drops below |
| 9 | `active` | BOOLEAN | NULL | `True` | |
| 10 | `last_triggered_at` | TIMESTAMPTZ | NULL | — | |
| 11 | `created_at` | TIMESTAMPTZ | NOT NULL | `NOW()` | |

---

## 3. Indexes

### 3.1 Existing Indexes (13 total)

| # | Index Name | Table | Columns | Type | Purpose |
|---|-----------|-------|---------|------|---------|
| 1 | `idx_listings_source_external` | `listings` | `source`, `external_id` | Composite B-tree | Upsert lookups, dedup |
| 2 | `idx_listings_make_model_year` | `listings` | `make`, `model`, `year` | Composite B-tree | Comp finder queries |
| 3 | `idx_listings_status` | `listings` | `status` | Single-column B-tree | Status filtering |
| 4 | `idx_listings_country_city` | `listings` | `country`, `city` | Composite B-tree | Geo filtering |
| 5 | `idx_listings_quality` | `listings` | `quality_score` | Single-column B-tree | Quality threshold filtering |
| 6 | `idx_listings_canonical` | `listings` | `canonical_vehicle_id` | Single-column B-tree | FK join performance |
| 7 | `idx_listings_pipeline_run` | `listings` | `pipeline_run_id` | Single-column B-tree | Pipeline run lookups |
| 8 | `idx_snapshots_listing_date` | `listing_snapshots` | `listing_id`, `captured_at` | Composite B-tree | Price history queries |
| 9 | `idx_snapshots_run` | `listing_snapshots` | `pipeline_run_id` | Single-column B-tree | Pipeline run lookups |
| 10 | `idx_valuation_cache` | `valuation_queries` | `cache_key` | Single-column B-tree | Cache hit lookups |
| 11 | `idx_valuation_queried_at` | `valuation_queries` | `queried_at` | Single-column B-tree | TTL-based cleanup |
| 12 | `idx_pipeline_runs_started` | `pipeline_runs` | `started_at` | Single-column B-tree | Recent run queries |
| 13 | `idx_drift_detected` | `drift_events` | `detected_at`, `drift_type` | Composite B-tree | Drift monitoring queries |

### 3.2 Missing Indexes (Recommended)

| # | Table | Columns | Rationale |
|---|-------|---------|-----------|
| 1 | `listings` | `normalized_price_aed` | Sort/filter by price in comp finder (currently scans all matching rows) |
| 2 | `listings` | `last_seen_at` | `ORDER BY last_seen_at DESC` in comp finder is a sort on every query |
| 3 | `listings` | `mileage_km` | Range filter in comp finder tiered queries |
| 4 | `canonical_vehicles` | `make`, `model`, `year` | Canonical resolution lookups |
| 5 | `valuation_queries` | `user_id` | User valuation history queries |
| 6 | `saved_valuations` | `user_id` | User bookmark listing queries |
| 7 | `price_alerts` | `user_id`, `active` | Active alert polling queries |
| 8 | `car_specs` | `make`, `model` | Knowledge base lookups during valuation |
| 9 | `car_issues` | `make`, `model` | Knowledge base lookups during valuation |
| 10 | `pipeline_runs` | `source` | Filter pipeline runs by scraper source |
| 11 | `dead_letter` | `pipeline_run_id` | Debugging rejected records per run |
| 12 | `scraper_health` | `source`, `captured_at` | Scraper health trend queries (used by `/v1/admin/scrapers`) |

---

## 4. Constraints Analysis

### 4.1 Unique Constraints

| Table | Column(s) | Enforced? | Method |
|-------|-----------|-----------|--------|
| `pipeline_runs` | `run_id` | ✅ Yes | ORM `unique=True` |
| `valuation_queries` | `cache_key` | ✅ Yes | ORM `unique=True` |
| `feature_flags` | `flag_name` | ✅ Yes | ORM `unique=True` |
| `user_accounts` | `email` | ✅ Yes | ORM `unique=True` |
| `listings` | `source`, `external_id` | ⚠️ No | Only via application-level upsert in promoter.py |
| `canonical_vehicles` | `make`, `model`, `year`, `generation` | ❌ No | Specified in blueprint, never created |

### 4.2 Foreign Key Constraints

| Child Table | Column | Parent Table | Enforced? |
|-------------|--------|-------------|-----------|
| `listings` | `canonical_vehicle_id` | `canonical_vehicles` | ✅ Yes (ORM `ForeignKey`) |
| `listing_snapshots` | `listing_id` | `listings` | ✅ Yes (ORM `ForeignKey` + DDL) |
| `listing_snapshots` | `pipeline_run_id` | (logical) | ✅ Yes (DDL only, not in ORM model) |
| `saved_valuations` | `user_id` | `user_accounts` | ✅ Yes (ORM `ForeignKey`) |
| `price_alerts` | `user_id` | `user_accounts` | ✅ Yes (ORM `ForeignKey`) |
| `dead_letter` | `pipeline_run_id` | (logical) | ❌ No FK |
| `scraper_health` | `pipeline_run_id` | (logical) | ❌ No FK |

### 4.3 Check Constraints

**None.** The blueprint specifies:
- `model_ratings` columns: `CHECK (rating BETWEEN 1 AND 5)` — not created
- `listings.quality_score`: `CHECK (quality_score BETWEEN 0 AND 100)` — not created
- `valuation_queries.confidence`: `CHECK (confidence IN ('high','medium','low','insufficient'))` — not created

### 4.4 NOT NULL Constraints

All NOT NULL columns are properly declared in ORM models. **One risk:** `pipeline_runs` has 8 columns with `default=0` but `nullable=True` in the ORM — the DB allows NULL for these columns despite the Python-level default.

---

## 5. Type System

### 5.1 Cross-Dialect Type Decorators (`src/db/base.py`)

| Decorator | PostgreSQL | SQLite | Used By |
|-----------|-----------|--------|---------|
| `UniversalUUID` | `UUID` | `CHAR(36)` | All PKs, all FK columns |
| `UniversalJSONB` | `JSONB` | `JSON` | `listings.price_history`, `listings.quality_flags`, `pipeline_runs.errors`, `dead_letter.raw_data`, `valuation_queries.shap_values/feature_importance/adjustments`, `model_registry.hyperparameters/training_config/features_used`, `drift_events.details`, `feature_flags.target_users`, `car_specs.engine_options/transmission_options`, `maintenance_costs.common_repair_costs`, `depreciation_curves.residual_pct_year`, `scraper_health.selector_failures/errors` |
| `UniversalDATERANGE` | `DATERANGE` | `String(64)` | `drift_events.baseline_period`, `drift_events.current_period` |

### 5.2 Migration vs ORM Type Inconsistency

The `listing_snapshots` table has a type mismatch:
- **ORM model** (`listing_snapshot.py`): Columns declared with `UniversalUUID`
- **Migration DDL** (`c42f2f2afaa8`): Columns use `postgresql.UUID` directly (hardcoded, not `UniversalUUID`)

This means the migration bypasses the cross-dialect decorators. The table cannot be auto-created via `Base.metadata.create_all()` — it's explicitly excluded in the migration and created via raw DDL.

### 5.3 Implicit Type Conversions

The `ListingSchema` Pandera validator in `validator.py` coerces types:
- `year`: string → int
- `asking_price`: string → float
- `mileage_km`: string → int

These happen at the validation layer, not the DB layer.

---

## 6. Partitioning

### 6.1 `listing_snapshots` — Range Partitioning

- **Partition key:** `captured_at` (TIMESTAMPTZ)
- **Strategy:** Monthly RANGE partitions
- **Partitions created:** 2 (July 2026, August 2026)
- **Auto-creation:** None

### 6.2 Partition Gap Analysis

| Risk | Detail |
|------|--------|
| **No auto-creation** | No `pg_partman` extension, no cron job, no application-level partition manager |
| **INSERT failure after Aug 2026** | Any INSERT with `captured_at >= 2026-09-01` will fail with "no partition of relation" |
| **No partition detach/archive** | Blueprint specifies detaching old partitions and archiving to S3 as Parquet after 2 years |
| **No default partition** | No `DEFAULT` partition to catch un-partitioned dates |

### 6.3 Recommended Fix

```sql
-- Add as part of pipeline startup or cron:
CREATE TABLE IF NOT EXISTS listing_snapshots_{YYYY}_{MM}
PARTITION OF listing_snapshots
FOR VALUES FROM ('{YYYY}-{MM}-01') TO ('{next_month}-01');
```

---

## 7. Missing Database Objects (Blueprint vs Reality)

| Object | Blueprint Reference | Status |
|--------|-------------------|--------|
| `listings_staging` table | §4.3 | ❌ Not created — pipeline writes directly to `listings` |
| `segment_stats` materialized view | §3.1 (post-scrape jobs) | ❌ Not created |
| `market_trends` materialized view | §3.1 | ❌ Not created |
| `listing_snapshots` monthly partitions | §4.2 | ⚠️ Only 2 created (Jul+Aug 2026) |
| `listing_snapshots` partition management | §4.2 | ❌ No auto-creation |
| `listing_snapshots` retention via partition detach | §4.2 | ❌ Not implemented |
| pgvector extension | §5.1 | ✅ Installed (not used) |
| `uuid-ossp` extension | Migration | ✅ Installed |
| Audit log table (partitioned by month) | §10.6 | ❌ Not created — blueprint specifies audit logging middleware with 90-day retention |

---

## 8. Data Lineage System

The `LineageMixin` adds 5 columns to `listings` and `listing_snapshots`:

| Column | Purpose |
|--------|---------|
| `schema_version` | Version of the table's schema |
| `parser_version` | Version of the parser that produced this row |
| `normalizer_version` | Version of the normalizer applied |
| `pipeline_run_id` | UUID linking to `pipeline_runs` |
| `ingested_at` | Timestamp of ingestion |

**Note:** `pipeline_run_id` in `LineageMixin` uses `UniversalUUID` with `nullable=False` but **no `ForeignKey` constraint** is declared in the ORM. The migration adds a FK for `listing_snapshots.pipeline_run_id` but not for `listings.pipeline_run_id`. This is inconsistent.

---

## 9. Performance Risks

### 9.1 Query Performance

| Risk | Detail | Severity |
|------|--------|----------|
| **Comp finder full scan** | `find_comps()` in `comp_finder.py` filters on `make`, `model`, `year` range, `mileage_km` range, `spec`, `country`, `quality_score`, and `status` — the `idx_listings_make_model_year` covers the first 3 columns but the remaining filters (mileage range, quality_score) require filtering in memory | Medium |
| **No price index** | `ORDER BY last_seen_at DESC` in comp finder performs a full sort on matching rows; no covering index for price-sorted comp queries | Medium |
| **No covering index for admin stats** | `/v1/admin/stats` runs `COUNT(*)` on `listings` and `valuation_queries` — these are sequential scans | Low |
| **JSONB queries** | `quality_flags`, `price_history`, `shap_values`, `feature_importance`, `adjustments` are JSONB — no GIN indexes for JSONB queries | Low (currently not queried by JSON content) |

### 9.2 Write Performance

| Risk | Detail | Severity |
|------|--------|----------|
| **Select-then-upsert race** | `promoter.py` does SELECT then INSERT/UPDATE — no `ON CONFLICT` clause; two concurrent scrapers can create duplicate `listings` rows | High |
| **No bulk insert** | Each listing inserted individually via ORM `session.add()` — no `bulk_insert_mappings` | Low |

### 9.3 Partition Performance

| Risk | Detail | Severity |
|------|--------|----------|
| **INSERT failure after Aug 2026** | See §6.2 | **Critical** |
| **Partition pruning** | Queries filtering on `captured_at` benefit from partition pruning — but only if partition key is in WHERE clause | Info |

---

## 10. Schema Deviations from Blueprint

| # | Blueprint Spec | Actual Implementation | Impact |
|---|---------------|----------------------|--------|
| 1 | `listings` has `UNIQUE(source, external_id)` | No constraint; handled via application-level upsert | Possible duplicates under race conditions |
| 2 | `canonical_vehicles` has `UNIQUE(make, model, year, COALESCE(generation, ''))` | No constraint | Duplicate canonical entries possible |
| 3 | `model_ratings` has CHECK constraints on all rating columns (BETWEEN 1 AND 5) | No CHECK constraints | Invalid ratings can be inserted |
| 4 | `valuation_queries.confidence` has CHECK for valid values | No CHECK constraint | Invalid confidence values possible |
| 5 | `listings_staging` table | Not created; pipeline writes directly to `listings` | No preprocessing isolation |
| 6 | Audit log table (partitioned, 90-day retention) | Not created | No request audit trail |
| 7 | `listing_snapshots` uses `UniversalUUID` in ORM but `postgresql.UUID` in DDL | Type inconsistency between model and migration | Works on PG, fails on SQLite |
| 8 | Blueprint specifies `seller_type`, `warranty`, `service_history` columns on `listings` | Present but never extracted by any scraper parser | Dead columns |
| 9 | Blueprint specifies `price_history` as `JSONB DEFAULT '[]'` | Present but never appended to | Dead column |
| 10 | Blueprint specifies `doors`, `cylinders`, `engine_size` columns | Present but never extracted by scrapers | Dead columns |

---

## 11. Data Volume Estimates

Based on the blueprint's volume projections:

| Table | Est. Weekly Growth | Est. Year 1 Size | Partition Strategy |
|-------|-------------------|------------------|--------------------|
| `listings` | 15K–25K new/updated | ~200K active + growth | None needed (bounded) |
| `listing_snapshots` | ~100K rows | ~5M rows | Monthly RANGE (broken — see §6) |
| `valuation_queries` | Unknown | Unknown | None (cache key dedup) |
| `pipeline_runs` | ~10–20 per week | ~1K rows | None needed |
| `dead_letter` | Variable | Unknown | None needed |
| `scraper_health` | ~10–20 per week | ~1K rows | None needed |
| `drift_events` | ~10 per week | ~500 rows | None needed |
| Knowledge base tables | Static (seed) | ~500–1000 rows | None needed |
| `user_accounts` | Unknown | Unknown | None needed |

---

## 12. Recommendations

### Critical
1. **Add partition auto-creation** for `listing_snapshots` — INSERTs will fail after August 2026
2. **Add `UNIQUE(source, external_id)` on `listings`** — prevent duplicate listings from concurrent scrapers
3. **Use `ON CONFLICT ... DO UPDATE` in promoter** — replace SELECT-then-UPSERT pattern

### High
4. **Add `idx_listings_last_seen_at` index** — comp finder sorts by this column
5. **Add `idx_listings_mileage_km` index** — comp finder filters by mileage range
6. **Add `UNIQUE(make, model, year, COALESCE(generation, ''))` on `canonical_vehicles`** — per blueprint
7. **Add CHECK constraints on `model_ratings`** — per blueprint
8. **Add FK constraints on `dead_letter.pipeline_run_id` and `scraper_health.pipeline_run_id`** — referential integrity
9. **Fix `listing_snapshots` migration type** — use `UniversalUUID` consistently

### Medium
10. **Add indexes on knowledge base tables** — `car_specs(make, model)`, `car_issues(make, model)`
11. **Add indexes on user tables** — `saved_valuations(user_id)`, `price_alerts(user_id, active)`
12. **Add `idx_scraper_health_source_date` index** — for admin scraper health queries
13. **Create `listings_staging` table** — per blueprint §4.3 preprocessing isolation
14. **Add GIN index on `listings.quality_flags`** — if flag-based filtering is needed

### Low
15. **Create materialized views** — `segment_stats`, `market_trends` per blueprint
16. **Create audit log table** — partitioned by month, 90-day retention
17. **Add `pg_partman` extension** — automated partition management
18. **Remove or populate dead columns** — `doors`, `cylinders`, `price_history` are never used

---

*Database audit completed 2026-07-12. No production code modified.*
