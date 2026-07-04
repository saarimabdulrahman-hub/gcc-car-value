# GCC Car Value Platform — Production Engineering Blueprint

**Version:** 2.0 (Revised)
**Date:** 2026-07-02
**Status:** Draft — Pending Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Data Pipeline Architecture](#3-data-pipeline-architecture)
4. [Database Design](#4-database-design)
5. [Similarity Search & Comp Finder](#5-similarity-search--comp-finder)
6. [Valuation Engine](#6-valuation-engine)
7. [MLOps Architecture](#7-mlops-architecture)
8. [Feature Engineering](#8-feature-engineering)
9. [API Design](#9-api-design)
10. [Security Architecture](#10-security-architecture)
11. [Monitoring & Observability](#11-monitoring--observability)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Development Phases & Roadmap](#13-development-phases--roadmap)
14. [Cost Estimates](#14-cost-estimates)
15. [Risk Assessment](#15-risk-assessment)
16. [Major Changes from Original Blueprint](#16-major-changes-from-original-blueprint)
17. [Engineering Scores](#17-engineering-scores)

---

## 1. Executive Summary

**GCC Car Value** is a consumer-first car valuation platform for the Gulf market. It scrapes classifieds and auction listings weekly, computes fair market values using a statistical engine (later enhanced with ML), and serves valuations through a public API and web application.

This blueprint is the **revised, production-grade** version of the initial design. Every section has been reviewed for architectural weaknesses, and 27 specific concerns have been addressed. Changes are integrated directly — this is the canonical implementation document.

**Core philosophy:** Simple, maintainable, production-ready, scalable, cost-efficient. No component is added unless it solves a real production problem.

---

## 2. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         GCC Car Value Platform                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      INGESTION LAYER                               │   │
│  │                                                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│  │  │ Dubizzle  │  │  Haraj   │  │YallaMotor│  │ Emirates Auction │ │   │
│  │  │ Scraper   │  │ Scraper  │  │ Scraper  │  │    Scraper       │ │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │   │
│  │       │             │             │                  │           │   │
│  │       ▼             ▼             ▼                  ▼           │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │              RAW LANDING ZONE (S3 + local staging)         │  │   │
│  │  │   raw_html/  raw_json/  parser_output/  validation_errors/ │  │   │
│  │  └────────────────────────────┬───────────────────────────────┘  │   │
│  │                               │                                  │   │
│  │                               ▼                                  │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │                   DATA QUALITY PIPELINE                     │  │   │
│  │  │                                                             │  │   │
│  │  │  Validate ──▶ Normalize ──▶ Quality Score ──▶ Deduplicate   │  │   │
│  │  │     │              │              │               │         │  │   │
│  │  │     ▼              ▼              ▼               ▼         │  │   │
│  │  │  [Reject]    [Enrich]    [Score 0-100]    [Merge/Update]    │  │   │
│  │  └────────────────────────────┬───────────────────────────────┘  │   │
│  │                               │                                  │   │
│  │          ┌────────────────────┴────────────────────┐             │   │
│  │          ▼                                         ▼             │   │
│  │  ┌──────────────┐                        ┌──────────────────┐   │   │
│  │  │   STAGING    │                        │  DEAD LETTER     │   │   │
│  │  │   TABLES     │                        │  (rejected rows) │   │   │
│  │  └──────┬───────┘                        └──────────────────┘   │   │
│  │         │                                                        │   │
│  │         │  Quality score ≥ threshold                             │   │
│  │         ▼                                                        │   │
│  │  ┌──────────────────────────────────────────────────────────┐    │   │
│  │  │                 PRODUCTION TABLES                          │    │   │
│  │  │  listings │ snapshots │ specs │ knowledge │ models │ ...  │    │   │
│  │  └──────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                     │
│  │   VALUATION ENGINE   │  │    KNOWLEDGE ENGINE   │                     │
│  │                      │  │                      │                     │
│  │  Statistical Model   │  │  Specs & Trims       │                     │
│  │  LightGBM Model      │  │  Common Issues       │                     │
│  │  Comp Finder         │  │  Ownership Costs     │                     │
│  │  Explainability      │  │  Depreciation Curves │                     │
│  └──────────┬───────────┘  └──────────┬───────────┘                     │
│             │                         │                                  │
│             └─────────┬───────────────┘                                  │
│                       ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      API LAYER (FastAPI)                          │   │
│  │                                                                   │   │
│  │  /v1/valuate  │  /v1/models  │  /v1/trends  │  /v1/health       │   │
│  │                                                                   │   │
│  │  Rate limiting  │  Auth (JWT + API Key)  │  Audit logging        │   │
│  └──────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│                                 ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    CONSUMERS                                       │   │
│  │                                                                   │   │
│  │  Web App (React)  │  Mobile (future)  │  Enterprise API clients   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    OBSERVABILITY LAYER                             │   │
│  │                                                                   │   │
│  │  OpenTelemetry  │  Prometheus  │  Grafana  │  Sentry  │  MLflow  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Database** | PostgreSQL 16 (single instance) | Handles 50 GB comfortably. No distributed DB needed for Years 1-3. |
| **Queue** | Staging tables as logical queue | V1 volume (15K-25K listings/week) doesn't justify a message broker. Staging tables provide the same decoupling with zero new infrastructure. Add RabbitMQ/Redis in Year 2+ if needed. |
| **Similarity Search** | Hard filters + weighted similarity | Car comps are deterministic, not fuzzy. Exact make/model, ranged year/mileage. More transparent and accurate than vector search for this domain. |
| **Raw Data** | S3 + local staging, compressed (zstd) | Never discard source data. Enables backfilling, parser debugging, and re-processing. |
| **Validation** | Pandera (DataFrame-native) | Lighter than Great Expectations, integrates with Python data stack, sufficient for this scale. |
| **ML Platform** | MLflow (self-hosted) | Open source, Python-native, runs on same instance. No SaaS cost. |
| **LLM** | Claude API (hosted, on-demand) | Only for valuation explanation text. Local models are not cost-effective at this scale. |

---

## 3. Data Pipeline Architecture

### 3.1 Revised Pipeline Flow

```
                              WEEKLY CRON TRIGGER
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SCRAPER ORCHESTRATOR                          │
│                                                                     │
│  For each active source (parallel workers):                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. FETCH                                                      │  │
│  │    - Fetch search index (paginated)                           │  │
│  │    - Diff against known external_ids                          │  │
│  │    - Fetch only new/updated listing pages                     │  │
│  │    - Store raw HTML in S3                                     │  │
│  │                                                               │  │
│  │ 2. PARSE                                                      │  │
│  │    - Extract fields via source-specific parser                │  │
│  │    - Store parser output JSON in staging                      │  │
│  │    - Record field extraction stats (success/fail per field)   │  │
│  │                                                               │  │
│  │ 3. VALIDATE (Pandera schema)                                  │  │
│  │    - Type checks (year is int, price is numeric)              │  │
│  │    - Range checks (year 1990..2027, price > 0)                │  │
│  │    - Required field checks (make, model, year, price)         │  │
│  │    - Cross-field checks (year ≤ current_year + 1)             │  │
│  │    - Custom checks (price not 1 AED test posts)               │  │
│  │                                                               │  │
│  │ 4. NORMALIZE                                                  │  │
│  │    - Normalize make/model names (canonical forms)             │  │
│  │    - Normalize spec (GCC_spec → GCC, US_spec → US, etc.)     │  │
│  │    - Normalize city names (Al Ain, al-ain → Al Ain)           │  │
│  │    - Compute normalized_price = original_price × exchange_rate│  │
│  │    - Extract structured fields from description text (regex)  │  │
│  │                                                               │  │
│  │ 5. QUALITY SCORE (0-100)                                      │  │
│  │    - Base score: 100                                          │  │
│  │    - Missing optional field: -5 each                          │  │
│  │    - Missing required field: REJECT (don't score)             │  │
│  │    - Price outlier (3σ from segment mean): -20                │  │
│  │    - Mileage outlier: -10                                     │  │
│  │    - Year anomaly: -15                                        │  │
│  │    - Suspiciously short description: -5                       │  │
│  │    - Known dealer spam pattern: -30                           │  │
│  │    - Multiple listings same seller/same car: -15              │  │
│  │                                                               │  │
│  │ 6. DEDUPLICATE                                                │  │
│  │    - Same external_id + source → UPDATE existing row          │  │
│  │    - Cross-source match (same car on Dubizzle + YallaMotor)   │  │
│  │      → merge into single canonical listing, track source      │  │
│  │    - Same phone number + same car (probable duplicate)        │  │
│  │                                                               │  │
│  │ 7. PROMOTE (quality_score ≥ 60)                               │  │
│  │    - Promote to production listings table                     │  │
│  │    - Below threshold → dead_letter table (for debugging)      │  │
│  │    - Log promotion stats per batch                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     POST-SCRAPE JOBS                                 │
│                                                                     │
│  1. DELISTING DETECTION (probabilistic)                             │
│     - For each previously-active listing NOT seen this week:        │
│       - Retry fetch (up to 3 attempts, 1-hour gaps)                 │
│       - If all fail → status = 'inactive_pending'                   │
│       - After 2 consecutive weeks inactive → 'probably_sold'        │
│       - After 4 weeks → 'delisted' (confidence: 0.95)               │
│       - 404 with listing removed page → 'probably_sold' (0.85)      │
│       - Still accessible but marked sold → 'sold_confirmed' (0.99)  │
│     - Record delisting_confidence (0.0-1.0)                         │
│                                                                     │
│  2. CROSS-SOURCE DEDUPLICATION                                      │
│     - Match listings across Dubizzle, YallaMotor, Haraj             │
│     - Join key: make + model + year + mileage (±5%) + city          │
│     - Create canonical_vehicle_id for matched groups                │
│                                                                     │
│  3. MATERIALIZED VIEW REFRESH                                       │
│     - segment_stats (median price, count, avg days to sell)         │
│     - market_trends (week-over-week price change per segment)       │
│                                                                     │
│  4. DRIFT DETECTION                                                 │
│     - Compare this week's feature distributions vs 4-week baseline  │
│     - Flag if PSI > 0.2 for any feature                             │
│                                                                     │
│  5. GENERATE BATCH METADATA                                         │
│     - pipeline_runs: run_id, records_in, promoted, rejected,        │
│       duplicates, quality_score_distribution, duration, errors      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Raw Data Preservation

| Aspect | Policy |
|---|---|
| **What to store** | Raw HTML of listing page, raw JSON of parsed output, parser output (intermediate), normalized output (final) |
| **Storage location** | S3 (raw HTML, raw JSON) + PostgreSQL staging (parser output, normalized output) |
| **Compression** | zstd (level 3) for S3 objects. ~3:1 compression ratio on HTML. |
| **Retention** | Raw HTML: 90 days. Parser output: 1 year. Normalized: indefinite (production tables). |
| **Cleanup** | S3 lifecycle policy: auto-delete objects older than 90 days. |
| **Why this matters** | If a parser bug corrupts normalized data, you can re-process from raw. If a new feature is discovered (sunroof, leather seats), you can backfill. Without raw data, bad parses are permanent losses. |

### 3.3 Schema Versioning

Every table that receives ingested data includes:

```sql
-- On every ingestion table:
schema_version       INTEGER NOT NULL,      -- version of this table's schema
parser_version       TEXT NOT NULL,         -- e.g., 'dubizzle_v2.1.0'
normalizer_version   TEXT NOT NULL,         -- e.g., 'normalizer_v1.3.0'
pipeline_run_id      UUID NOT NULL,         -- batch identifier
ingested_at          TIMESTAMPTZ NOT NULL   -- when this record was created
```

**Migration strategy:** Additive only. New columns get NULL for old rows. Never drop columns — deprecate and ignore. A migration is a new schema_version number. Old rows with old schema_version are re-processed lazily (on next scrape of that listing) or via backfill job.

**Backward compatibility:** The API always reads the latest schema_version. The reader layer handles missing columns via COALESCE with sensible defaults, so old and new rows coexist transparently.

### 3.4 Currency Handling

```sql
-- Never overwrite. Always preserve origin and derivation.
original_price        NUMERIC NOT NULL,       -- price as scraped
original_currency     TEXT NOT NULL,          -- 'AED', 'SAR', 'KWD', 'QAR', 'BHD', 'OMR'
exchange_rate         NUMERIC NOT NULL,       -- rate used for conversion
exchange_timestamp    TIMESTAMPTZ NOT NULL,   -- when rate was fetched
normalized_price_aed  NUMERIC NOT NULL        -- original_price × exchange_rate
```

Exchange rates fetched from a free API (exchangerate-api.com or similar) at pipeline start. Stored with the record so corrections can be replayed. If a USD-pegged currency (AED, SAR, QAR, OMR, BHD) fluctuates by >0.5%, alert — this shouldn't happen.

### 3.5 Delisting Detection (Probabilistic)

```
Listing NOT seen this week
    │
    ▼
Retry fetch (3 attempts, 1-hour gaps)
    │
    ├── All fail (404 / timeout / connection error)
    │       │
    │       ▼
    │   status = 'inactive_pending'
    │   delisting_confidence = 0.3
    │       │
    │       ▼ (next week: still not found)
    │   status = 'probably_sold'
    │   delisting_confidence = 0.7
    │       │
    │       ▼ (week 4: still not found)
    │   status = 'delisted'
    │   delisting_confidence = 0.95
    │
    ├── Page loads but contains "sold" / "بيعت" / "تم البيع"
    │   status = 'sold_confirmed'
    │   delisting_confidence = 0.99
    │
    ├── Page loads but contains "expired" / "منتهية"
    │   status = 'expired'
    │   delisting_confidence = 0.6
    │   (listing expired — not necessarily sold)
    │
    └── Page loads normally (temporary glitch)
        status = 'active'
        delisting_confidence = NULL
```

**Why not binary 404→sold:** 404s can be transient (CDN issues, site maintenance, URL restructuring). A car marked "sold" by the seller is a much stronger signal than a missing page. The confidence score propagates into the valuation — comps with `sold_confirmed` status are weighted higher in the transaction price estimation.

### 3.6 Scraper Confidence Monitoring

Each scraper run records field-level extraction stats:

```sql
CREATE TABLE scraper_health (
    id                  UUID PRIMARY KEY,
    pipeline_run_id     UUID NOT NULL,
    source              TEXT NOT NULL,
    captured_at         TIMESTAMPTZ NOT NULL,

    -- Volume
    pages_crawled       INTEGER,
    listings_found      INTEGER,
    listings_new        INTEGER,
    listings_updated    INTEGER,

    -- Field extraction rates (%)
    price_extracted_pct     NUMERIC,
    year_extracted_pct      NUMERIC,
    mileage_extracted_pct   NUMERIC,
    spec_extracted_pct      NUMERIC,
    trim_extracted_pct      NUMERIC,
    city_extracted_pct      NUMERIC,
    body_type_extracted_pct NUMERIC,
    transmission_extracted_pct NUMERIC,

    -- Parse confidence
    parse_success_rate  NUMERIC,        -- % of pages that parsed without error
    avg_parse_time_ms   NUMERIC,
    html_structure_hash TEXT,           -- detect DOM changes
    selector_failures   JSONB,          -- [{selector, fail_count}]
    unexpected_layouts  INTEGER,        -- pages that didn't match expected structure

    -- Derived
    scraper_confidence  NUMERIC,        -- composite score 0-100
    errors              JSONB           -- [{url, error_type, message}]
);
```

**Alert rules:**
- Any field extraction rate drops by >20% week-over-week → alert
- `html_structure_hash` changes → warning (site may have redesigned)
- `scraper_confidence` < 50 → alert (parser is effectively broken)
- Error rate > 10% of pages → alert

### 3.7 Data Validation Framework: Pandera

**Choice: Pandera** over Great Expectations.

| Factor | Pandera | Great Expectations |
|---|---|---|
| Setup complexity | `pip install pandera`, define schema in Python | Docker, config YAML, CLI, docs site |
| Integration | Native DataFrame validation | External validation engine |
| Schema definition | Python dataclass-style | YAML/JSON config |
| Scale fit | Perfect for this data volume | Enterprise, multi-team data lakes |
| Learning curve | 1 hour | 1 day+ |
| Overhead | Near zero | Significant |

Pandera schemas are Python code, version-controlled alongside the parsers:

```python
import pandera as pa

class ListingSchema(pa.DataFrameModel):
    make: str = pa.Field(nullable=False)
    model: str = pa.Field(nullable=False)
    year: int = pa.Field(in_range={"min_value": 1990, "max_value": 2027})
    asking_price: float = pa.Field(gt=0, lt=10_000_000)  # < 10M AED
    mileage_km: int = pa.Field(ge=0, le=1_000_000, nullable=True)
    spec: str = pa.Field(isin=["GCC", "US", "Japan", "European", "Other", None],
                          nullable=True)
    city: str = pa.Field(nullable=False)
    country: str = pa.Field(isin=["AE", "SA", "QA", "KW", "BH", "OM"])

    @pa.dataframe_check
    def year_not_future(cls, df):
        return df["year"] <= pd.Timestamp.now().year + 1

    @pa.dataframe_check
    def reasonable_price(cls, df):
        """Price shouldn't be exactly 1, 123, 1234, 12345 (test posts)"""
        suspicious = df[df["asking_price"].isin([1, 123, 1234, 12345, 123456])]
        return len(suspicious) == 0
```

---

## 4. Database Design

### 4.1 Core Schema (Revised)

```sql
-- ============================================================
-- PRODUCTION TABLES
-- ============================================================

-- Canonical vehicle identity (cross-source deduplication anchor)
CREATE TABLE canonical_vehicles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    year                INTEGER NOT NULL,
    generation          TEXT,               -- 'J200' for 2008-2021 Land Cruiser
    body_type           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(make, model, year, COALESCE(generation, ''))
);

-- Main listings table (production, quality_score ≥ 60)
CREATE TABLE listings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_vehicle_id UUID REFERENCES canonical_vehicles(id),

    -- Source identity
    source              TEXT NOT NULL,      -- 'dubizzle', 'yallamotor', 'haraj', ...
    external_id         TEXT NOT NULL,
    url                 TEXT,

    -- Lifecycle
    first_seen_at       TIMESTAMPTZ NOT NULL,
    last_seen_at        TIMESTAMPTZ NOT NULL,
    status              TEXT NOT NULL,      -- active, inactive_pending, probably_sold,
                                           --   sold_confirmed, expired, delisted
    delisted_at         TIMESTAMPTZ,
    delisting_confidence NUMERIC,          -- 0.0 to 1.0

    -- Vehicle identity
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    year                INTEGER NOT NULL,
    trim                TEXT,
    spec                TEXT,               -- GCC, US, Japan, European, Other
    body_type           TEXT,
    transmission        TEXT,
    fuel_type           TEXT,
    engine_size         NUMERIC,
    color               TEXT,
    doors               INTEGER,
    cylinders           INTEGER,

    -- Pricing (dual storage — original + normalized)
    original_price      NUMERIC NOT NULL,
    original_currency   TEXT NOT NULL,      -- AED, SAR, KWD, QAR, BHD, OMR
    exchange_rate       NUMERIC NOT NULL,
    exchange_timestamp  TIMESTAMPTZ NOT NULL,
    normalized_price_aed NUMERIC NOT NULL,
    price_history       JSONB DEFAULT '[]', -- [{date, price, currency}, ...]

    -- Condition & metadata
    mileage_km          INTEGER,
    warranty            BOOLEAN,
    service_history     BOOLEAN,
    seller_type         TEXT,               -- dealer, private, auction

    -- Location
    city                TEXT NOT NULL,
    country             TEXT NOT NULL,      -- AE, SA, QA, KW, BH, OM

    -- Quality
    quality_score       INTEGER NOT NULL DEFAULT 0,  -- 0-100
    quality_flags       JSONB DEFAULT '[]',           -- [flag_reasons]

    -- Lineage (every record)
    schema_version      INTEGER NOT NULL,
    parser_version      TEXT NOT NULL,
    normalizer_version  TEXT NOT NULL,
    pipeline_run_id     UUID NOT NULL,
    ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Full raw reference
    raw_data_s3_key     TEXT,               -- S3 key for raw HTML + JSON

    UNIQUE(source, external_id)
);

-- Weekly snapshots (partitioned)
CREATE TABLE listing_snapshots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id          UUID NOT NULL REFERENCES listings(id),
    captured_at         TIMESTAMPTZ NOT NULL,
    asking_price        NUMERIC NOT NULL,
    original_currency   TEXT NOT NULL,
    status              TEXT NOT NULL,
    days_on_market      INTEGER,            -- computed: captured_at - first_seen_at
    price_change_pct    NUMERIC,            -- from previous snapshot

    -- Lineage
    schema_version      INTEGER NOT NULL,
    pipeline_run_id     UUID NOT NULL,
    ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (captured_at);

-- Create monthly partitions
-- Partition naming: listing_snapshots_2026_07, listing_snapshots_2026_08, ...

-- Pipeline execution metadata
CREATE TABLE pipeline_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID NOT NULL UNIQUE,
    source              TEXT,               -- NULL for cross-source runs
    started_at          TIMESTAMPTZ NOT NULL,
    completed_at        TIMESTAMPTZ,
    duration_seconds    INTEGER,

    -- Volume stats
    pages_crawled       INTEGER DEFAULT 0,
    records_ingested    INTEGER DEFAULT 0,
    records_new         INTEGER DEFAULT 0,
    records_updated     INTEGER DEFAULT 0,
    records_promoted    INTEGER DEFAULT 0,    -- quality ≥ threshold
    records_rejected    INTEGER DEFAULT 0,    -- quality < threshold
    duplicates_found    INTEGER DEFAULT 0,

    -- Quality distribution
    quality_score_p50   NUMERIC,
    quality_score_p90   NUMERIC,
    quality_score_mean  NUMERIC,

    -- Errors
    error_count         INTEGER DEFAULT 0,
    errors              JSONB DEFAULT '[]',
    success             BOOLEAN DEFAULT FALSE,

    -- Versioning
    parser_version      TEXT,
    normalizer_version  TEXT,
    git_commit          TEXT
);

-- Dead letter queue (rejected records, for debugging)
CREATE TABLE dead_letter (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source              TEXT NOT NULL,
    external_id         TEXT,
    rejection_reason    TEXT NOT NULL,       -- 'missing_make', 'invalid_year', etc.
    raw_data            JSONB NOT NULL,
    quality_score       INTEGER,
    pipeline_run_id     UUID NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Valuation queries (idempotency + audit)
CREATE TABLE valuation_queries (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key           TEXT NOT NULL UNIQUE,  -- deterministic hash
    queried_at          TIMESTAMPTZ DEFAULT NOW(),

    -- Input
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    year                INTEGER NOT NULL,
    mileage_km          INTEGER,
    spec                TEXT,
    trim                TEXT,
    city                TEXT,
    country             TEXT,

    -- Output
    estimated_price     NUMERIC,
    price_low           NUMERIC,
    price_high          NUMERIC,
    comp_count          INTEGER,
    confidence          TEXT,               -- high, medium, low
    model_version       TEXT,
    model_type          TEXT,               -- statistical, lightgbm

    -- Explainability
    shap_values         JSONB,              -- top 5 features + contributions
    feature_importance  JSONB,
    adjustments         JSONB,              -- [{reason, amount, explanation}]

    -- Metadata
    response_ms         INTEGER,
    api_version         TEXT,
    user_id             TEXT,               -- if authenticated
    ip_hash             TEXT,               -- hashed for privacy
    UNIQUE(cache_key)
);

-- Enhanced model registry
CREATE TABLE model_registry (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trained_at          TIMESTAMPTZ NOT NULL,
    model_type          TEXT NOT NULL,      -- 'statistical', 'lightgbm'
    model_path          TEXT,               -- path to serialized model
    model_name          TEXT NOT NULL,      -- human-readable version label

    -- Performance
    mae                 NUMERIC,
    mape                NUMERIC,            -- mean absolute percentage error
    r2_score            NUMERIC,
    training_rows       INTEGER,
    holdout_rows        INTEGER,

    -- Training details
    training_dataset_hash TEXT,
    feature_version     TEXT,
    git_commit          TEXT,
    hyperparameters     JSONB,
    training_config     JSONB,
    features_used       JSONB,              -- list of feature names

    -- Lifecycle
    status              TEXT NOT NULL DEFAULT 'training',  -- training, evaluating,
                                                           -- shadow, approved, active,
                                                           -- rolled_back, archived
    shadow_started_at   TIMESTAMPTZ,        -- when shadow deployment began
    approved_at         TIMESTAMPTZ,        -- when human approved
    approved_by         TEXT,               -- who approved
    activated_at        TIMESTAMPTZ,        -- when became production
    rolled_back_at      TIMESTAMPTZ,
    rollback_reason     TEXT,

    -- Shadow performance (for comparison)
    shadow_query_count  INTEGER,
    shadow_mae          NUMERIC,
    shadow_vs_active_pct NUMERIC            -- improvement vs active model
);

-- Scraper health (as defined in 3.6)
-- Feature drift log
CREATE TABLE drift_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detected_at         TIMESTAMPTZ DEFAULT NOW(),
    drift_type          TEXT NOT NULL,      -- feature, target, prediction, market
    feature_name        TEXT,
    psi_value           NUMERIC,            -- population stability index
    baseline_period     DATERANGE,
    current_period      DATERANGE,
    threshold_exceeded  BOOLEAN,
    details             JSONB,
    acknowledged        BOOLEAN DEFAULT FALSE
);

-- Feature flags
CREATE TABLE feature_flags (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_name           TEXT NOT NULL UNIQUE,
    description         TEXT,
    enabled             BOOLEAN DEFAULT FALSE,
    rollout_pct         INTEGER DEFAULT 100,  -- % of traffic
    target_users        TEXT[],                -- user IDs, null = all
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- KNOWLEDGE BASE TABLES
-- ============================================================

CREATE TABLE car_specs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    generation          TEXT,               -- 'J200 (2008-2021)'
    year_start          INTEGER,
    year_end            INTEGER,
    trim                TEXT,
    engine_options      JSONB,              -- [{size_L, cylinders, fuel, hp, torque}]
    transmission_options JSONB,             -- [{type, gears}]
    drivetrain          TEXT,               -- '4WD', 'AWD', 'RWD', 'FWD'
    fuel_economy_combined NUMERIC,         -- L/100km
    fuel_tank_capacity  NUMERIC,
    seating_capacity    INTEGER,
    cargo_volume_L      NUMERIC,
    safety_rating       TEXT,               -- 'NCAP 5-star'
    warranty_years      INTEGER,
    warranty_km         INTEGER,
    source              TEXT,               -- 'JATO', 'manufacturer', 'manual'
    source_url          TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(make, model, COALESCE(generation, ''), COALESCE(trim, ''))
);

CREATE TABLE car_issues (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    generation          TEXT,
    year_start          INTEGER,
    year_end            INTEGER,
    issue_title         TEXT NOT NULL,
    issue_description   TEXT,
    severity            TEXT,               -- 'minor', 'moderate', 'major', 'critical'
    typical_mileage_km  INTEGER,            -- when issue typically appears
    repair_cost_estimate NUMERIC,           -- in AED
    source              TEXT,               -- 'drivearabia', 'reddit', 'forum', 'manual'
    source_url          TEXT,
    confirmed           BOOLEAN DEFAULT FALSE,
    confirmed_by_count  INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE maintenance_costs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    generation          TEXT,
    service_interval_km INTEGER,            -- e.g., 10000
    minor_service_cost  NUMERIC,            -- AED
    major_service_cost  NUMERIC,            -- AED
    common_repair_costs JSONB,              -- [{repair, cost_range, mileage}]
    annual_insurance_estimate NUMERIC,
    source              TEXT,               -- 'partsouq', 'dealer_menu', 'community'
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(make, model, COALESCE(generation, ''))
);

CREATE TABLE depreciation_curves (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    generation          TEXT,
    msrp_aed            NUMERIC,            -- original manufacturer price
    residual_pct_year   JSONB NOT NULL,     -- {1: 0.88, 2: 0.80, 3: 0.72, ...}
    computed_from_rows  INTEGER,            -- how many listings informed this
    last_updated        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(make, model, COALESCE(generation, ''))
);

CREATE TABLE model_ratings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make                TEXT NOT NULL,
    model               TEXT NOT NULL,
    generation          TEXT,
    reliability         NUMERIC CHECK (reliability BETWEEN 1 AND 5),
    comfort             NUMERIC CHECK (comfort BETWEEN 1 AND 5),
    performance         NUMERIC CHECK (performance BETWEEN 1 AND 5),
    fuel_economy        NUMERIC CHECK (fuel_economy BETWEEN 1 AND 5),
    offroad_capability  NUMERIC CHECK (offroad_capability BETWEEN 1 AND 5),
    resale_value        NUMERIC CHECK (resale_value BETWEEN 1 AND 5),
    overall             NUMERIC CHECK (overall BETWEEN 1 AND 5),
    rating_count        INTEGER DEFAULT 0,
    source              TEXT,               -- 'computed', 'community', 'expert'
    last_updated        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(make, model, COALESCE(generation, ''))
);

-- Indexes
CREATE INDEX idx_listings_source_external ON listings(source, external_id);
CREATE INDEX idx_listings_make_model_year ON listings(make, model, year);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_country_city ON listings(country, city);
CREATE INDEX idx_listings_quality ON listings(quality_score);
CREATE INDEX idx_listings_canonical ON listings(canonical_vehicle_id);
CREATE INDEX idx_listings_pipeline_run ON listings(pipeline_run_id);
CREATE INDEX idx_snapshots_listing_date ON listing_snapshots(listing_id, captured_at);
CREATE INDEX idx_snapshots_run ON listing_snapshots(pipeline_run_id);
CREATE INDEX idx_valuation_cache ON valuation_queries(cache_key);
CREATE INDEX idx_valuation_queried_at ON valuation_queries(queried_at);
CREATE INDEX idx_pipeline_runs_started ON pipeline_runs(started_at);
CREATE INDEX idx_drift_detected ON drift_events(detected_at, drift_type);
```

### 4.2 Table Partitioning Strategy

**`listing_snapshots` — partitioned monthly on `captured_at`.**

| Rationale | Detail |
|---|---|
| **Why monthly** | Weekly partitions create 52 partitions/year — too many. Yearly partitions grow too large. Monthly balances partition count with partition size. |
| **Why snapshots only** | `listings` is bounded (~200K active + growth). It doesn't need partitioning at this scale. `snapshots` grows unbounded (~100K/week). |
| **Why not by country or source** | Partition by time simplifies partition management (auto-create next month, auto-drop after 2 years). Query performance is adequate with the `(listing_id, captured_at)` index. |
| **Retention via partition** | After 2 years, entire monthly partition is detached and archived to S3 as Parquet. DuckDB can query it directly. |

### 4.3 Staging Tables (Pre-Production)

```sql
-- Staging mirrors production schema but adds:
-- - No unique constraints (duplicates resolved in promote step)
-- - Stores all records regardless of quality
-- - Truncated after each successful pipeline run

CREATE TABLE listings_staging (
    LIKE listings INCLUDING DEFAULTS,
    -- Override: no unique constraint
    staging_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    validation_errors   JSONB DEFAULT '[]',
    promoted            BOOLEAN DEFAULT FALSE
);
```

---

## 5. Similarity Search & Comp Finder

### 5.1 Decision: Hard Filters + Weighted Similarity (Not pgvector)

**Challenge result:** pgvector on a 7-dimensional feature vector is the wrong tool for this domain. Replaced with hard filters + weighted similarity.

**Why:**

| Approach | Car Valuation Fit |
|---|---|
| **pgvector embedding** | Embeddings capture fuzzy semantic similarity. But car comps are deterministic: a 2018 Camry is NOT similar to a 2019 Camry in embedding space if the embedding weights year strongly — it's either the same car or it isn't. Vector search adds opacity to what should be transparent rules. |
| **Hard filters + weighted scoring** | "Find all GCC-spec 2016-2020 Land Cruisers within 50K km of my mileage, in UAE, then rank by recency × mileage closeness × spec match." Every step is inspectable and debuggable. |

### 5.2 Comp Finder Algorithm

```python
def find_comps(
    make: str, model: str, year: int, mileage_km: int,
    spec: str, country: str, city: str | None = None,
    min_comps: int = 15, max_comps: int = 50
) -> list[CompListing]:
    """
    Tiered filters. Each tier relaxes constraints if not enough comps found.
    """

    tiers = [
        # Tier 1: Strict — same spec, tight year/mileage, same country
        {"year_range": 2, "mileage_range_pct": 0.30, "same_spec": True,
         "same_country": True, "same_city": False},

        # Tier 2: Relax spec — allow any spec, same country
        {"year_range": 3, "mileage_range_pct": 0.50, "same_spec": False,
         "same_country": True, "same_city": False},

        # Tier 3: Relax country — GCC-wide
        {"year_range": 4, "mileage_range_pct": 0.75, "same_spec": False,
         "same_country": False, "same_city": False},
    ]

    for tier in tiers:
        comps = query_comps(make, model, year, mileage_km, tier)
        if len(comps) >= min_comps:
            break

    # Score and rank
    scored = [score_comp(c, make, model, year, mileage_km, spec, country)
              for c in comps]
    scored.sort(key=lambda c: c.score, reverse=True)

    return scored[:max_comps]


def score_comp(comp, make, model, year, mileage_km, spec, country) -> CompListing:
    """Weighted scoring. All weights transparent and configurable."""
    score = 100.0

    # Recency (newer listings are more relevant)
    days_old = (datetime.now() - comp.last_seen_at).days
    if days_old <= 7:    score -= 0
    elif days_old <= 30:  score -= 5
    elif days_old <= 90:  score -= 15
    else:                 score -= 30

    # Mileage closeness
    if comp.mileage_km and mileage_km:
        delta_pct = abs(comp.mileage_km - mileage_km) / mileage_km
        score -= delta_pct * 25  # up to -25 for 100% difference

    # Year match
    year_delta = abs(comp.year - year)
    score -= year_delta * 8

    # Spec match (GCC premium)
    if spec and comp.spec:
        if comp.spec == spec:
            score -= 0
        elif comp.spec == "GCC" and spec != "GCC":
            score -= 5  # GCC comps are ok references for non-GCC
        else:
            score -= 15  # Different spec = less relevant

    # Country match
    if comp.country == country:
        score -= 0
    else:
        score -= 10

    # Quality bonus
    score += (comp.quality_score / 100) * 10  # up to +10

    # Sold comp bonus (sold = real transaction evidence)
    if comp.status in ("sold_confirmed", "probably_sold"):
        score += 5
    if comp.delisting_confidence and comp.delisting_confidence > 0.8:
        score += 3

    return CompListing(comp, score)


def query_comps(make, model, year, mileage_km, tier) -> list[dict]:
    """SQL with hard filters, scored and limited in Python."""
    query = """
        SELECT *, %(score_expr)s AS similarity_score
        FROM listings
        WHERE make = %(make)s
          AND model = %(model)s
          AND year BETWEEN %(year_min)s AND %(year_max)s
          AND status IN ('active', 'probably_sold', 'sold_confirmed')
          AND quality_score >= 60
          {spec_filter}
          {country_filter}
          {mileage_filter}
        ORDER BY last_seen_at DESC
        LIMIT %(limit)s
    """
    # ... parameter binding
```

**Why this is better:**
1. **Explainable.** Every comp and its score is visible. "This listing scored 85 because it's recent (-0), close mileage (-3), GCC spec (-0)..." The user sees the comps.
2. **Debuggable.** If a valuation is wrong, you trace it to which comps were selected and why.
3. **Faster.** Indexed queries on make/model/year/status vs vector distance scan.
4. **No embedding maintenance.** No need to recompute embeddings on every update.

**pgvector stays installed** for future use (text search in descriptions, image similarity for damage detection), but it's not the primary comp finder.

---

## 6. Valuation Engine

### 6.1 Engine Architecture

```
POST /v1/valuate {make, model, year, mileage, spec, city, country}
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. IDEMPOTENCY CHECK                                            │
│    cache_key = SHA256(make|model|year|mileage|spec|city|country │
│                       |date)                                    │
│    If exists in valuation_queries AND < 24h old → return cached │
└─────────────────────────────────────────────────────────────────┘
    │ (cache miss)
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. COMP FINDER                                                  │
│    Tiered hard filters + weighted scoring → ranked comps        │
│    (see Section 5)                                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. STATISTICAL MODEL (always runs, even when ML is active)      │
│                                                                 │
│    a. Compute P25, P50, P75 of comp asking prices               │
│    b. Adjust P50 for mileage delta:                             │
│       - Per-km depreciation factor (varies by segment)          │
│       - mileage_adj = (comp_median_mileage - query_mileage)     │
│                       × dep_per_km                              │
│    c. Adjust for spec:                                          │
│       - GCC spec multiplier (from market data)                  │
│       - US spec multiplier (typically 0.75-0.85 vs GCC)         │
│       - Japan spec multiplier (typically 0.80-0.90 vs GCC)      │
│    d. Adjust for city (Dubai premium, etc.)                     │
│    e. Adjust for seller type (dealer +5-10%, private baseline)  │
│                                                                 │
│    Output: {estimate, range, confidence, adjustments}           │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. ML MODEL (if active and confidence threshold met)            │
│                                                                 │
│    a. Feature vector built from query + market context          │
│    b. LightGBM predicts transaction_price                       │
│    c. Cross-reference with statistical output                   │
│    d. If ML and statistical disagree by >15% → flag,            │
│       default to statistical with warning                       │
│                                                                 │
│    Output: {ml_estimate, ml_confidence, feature_contributions}  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. CONFIDENCE SCORING                                           │
│                                                                 │
│    HIGH:   ≥30 comps, price CV < 0.15, recent data (<30 days)   │
│    MEDIUM: ≥10 comps, price CV < 0.30                           │
│    LOW:    <10 comps, or price CV ≥ 0.30                        │
│    INSUFFICIENT: <5 comps → return error, not estimate          │
│                                                                 │
│    Confidence propagates to UI badge + range width.             │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. EXPLAINABILITY                                               │
│                                                                 │
│    Statistical:                                                 │
│    - "Based on N similar listings in {city}"                   │
│    - "Mileage adjustment: -X AED ({km} above segment avg)"      │
│    - "Spec adjustment: +Y AED (GCC premium)"                    │
│    - "City adjustment: +Z AED (Dubai market)"                   │
│                                                                 │
│    ML (when active):                                            │
│    - SHAP values for top 5 features                             │
│    - "Mileage contributed -8,200 AED"                           │
│    - "GCC spec contributed +12,500 AED"                         │
│    - "Recent market trend: +2,400 AED"                          │
│                                                                 │
│    LLM narrative (optional, V2):                                │
│    - Structured + SHAP → natural language explanation           │
│    - Grounded in data, not hallucinated                         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. KNOWLEDGE ENRICHMENT                                         │
│    - Model specs, generations, trims                            │
│    - Known issues for this model-generation                     │
│    - Estimated annual maintenance cost                          │
│    - Depreciation curve (year 1-10)                             │
│    - Market liquidity (avg days to sell)                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
Return full ValuationResponse
```

### 6.2 Confidence Intervals

Confidence is not just a badge. It's a numeric width:

```python
def confidence_interval(comps, confidence_level=0.80):
    """Bootstrap CI for the median."""
    medians = [
        np.median(np.random.choice(comps, size=len(comps), replace=True))
        for _ in range(1000)
    ]
    return np.percentile(medians, [(1-confidence_level)/2*100,
                                     (1+confidence_level)/2*100])
```

The `price_low` and `price_high` in the output are the 80% confidence interval around the point estimate. This is statistically honest — "we're 80% confident the fair value is between X and Y."

### 6.3 Good Deal Indicator

A consumer-facing signal computed alongside every valuation:

| Indicator | Condition | Meaning |
|---|---|---|
| **Great Deal** 🟢 | asking_price < P25 of comps AND quality_score ≥ 80 | "This car is priced below 75% of comparable listings." |
| **Fair Deal** 🟡 | asking_price between P25 and P75 of comps | "This car is priced within the normal market range." |
| **Above Market** 🔴 | asking_price > P75 of comps | "This car is priced above 75% of comparable listings. Consider negotiating." |
| **Not enough data** ⚪ | <10 comps OR confidence = "low" | No deal indicator shown. |

The indicator is only shown when the user provides a specific asking price to evaluate (i.e., they're evaluating a car they found, not just getting a generic valuation). The `POST /v1/valuate` endpoint accepts an optional `asking_price` parameter specifically for this purpose.

### 6.4 V1 Product Features (Data Already Available)

These ship in Phase 1-2 because the data pipeline produces them naturally:

| Feature | Data Source | Phase |
|---|---|---|
| **Price history chart** | `listing_snapshots` → price over time for the specific listing | Phase 2 |
| **Depreciation curve** | `depreciation_curves` table, computed from listing data + JATO MSRP | Phase 2 |
| **Market liquidity** | Median `days_on_market` before delisting, per segment | Phase 1 |
| **Ownership cost estimate** | `maintenance_costs` + Partsouq data | Phase 2 |
| **Dealer vs private comparison** | `seller_type` field, computed premium per segment | Phase 1 |

---

## 7. MLOps Architecture

### 7.1 Model Lifecycle (Revised)

```
┌──────────┐
│ TRAINING  │  Weekly cron. Train on current data.
└─────┬────┘
      │
      ▼
┌──────────────┐
│ EVALUATION   │  Holdout set (most recent week of data).
│              │  Metrics: MAE, MAPE, R².
│              │  Compare vs active model on same holdout.
│              │  Log all metrics to MLflow + model_registry.
└─────┬────────┘
      │
      │  New model MAE > active model MAE?
      │  ├── YES → archive (no improvement)
      │  └── NO  → proceed
      │
      ▼
┌──────────────┐
│ SHADOW       │  New model loaded alongside active.
│ DEPLOYMENT   │  Both predict on every query.
│              │  Active model's result returned to user.
│              │  Shadow predictions logged for comparison.
│              │  Runs for minimum 1 week.
└─────┬────────┘
      │
      │  After 1 week: shadow beats active on real traffic?
      │  ├── NO → archive shadow
      │  └── YES → flag for human review
      │
      ▼
┌──────────────┐
│ HUMAN        │  Dashboard shows:
│ APPROVAL     │  - Active vs shadow MAE over shadow period
│              │  - Prediction distribution comparison
│              │  - Feature importance comparison
│              │  - Top 10 predictions that changed most
│              │  - Drift status
│              │
│              │  Engineer reviews and clicks "Promote" or "Reject"
└─────┬────────┘
      │
      ▼
┌──────────────┐
│ ACTIVE       │  New model promoted.
│              │  Previous model marked 'rolled_back'.
│              │  Rollback = flip previous model to active.
│              │  All predictions tagged with model_version.
└──────────────┘
```

### 7.2 Rollback Strategy

```
┌─────────────────────────────────────────────────────────────┐
│ ROLLBACK TRIGGERS                                            │
│                                                              │
│ 1. MANUAL: Engineer observes issue, clicks rollback in admin │
│ 2. AUTOMATED: MAE on live queries > active_mae × 1.3        │
│    for >50 queries in a row → auto-rollback + alert          │
│ 3. DRIFT-BASED: PSI on input features > 0.3 sustained        │
│    for >2 hours → alert → manual review → possible rollback  │
└─────────────────────────────────────────────────────────────┘

Rollback procedure:
1. Flip model_registry.is_active: new_model → false, previous_model → true
2. Deploy previous model artifact (or reload from disk)
3. Log rollback event with reason
4. All valuation_queries now tagged with previous model_version
5. Post-mortem: why did the new model fail?
```

### 7.3 Drift Detection

Three drift types monitored:

| Drift Type | Metric | Threshold | Action |
|---|---|---|---|
| **Feature drift** | PSI (Population Stability Index) per feature, vs 4-week baseline | PSI > 0.2 | Warning. PSI > 0.3 → alert. Possible causes: new source added, site changed, market shift. |
| **Target drift** | Median normalized_price per segment, week-over-week | Change > 15% | Alert. Possible cause: genuine market move (oil shock, policy change). Not necessarily bad. |
| **Prediction drift** | MAE of active model on recent queries vs training MAE | MAE increase > 30% | Alert. Model may be stale. Evaluate retraining. |
| **Market drift** | Listing volume per segment, price volatility | Volume drop > 40% or volatility spike > 2× | Warning. Segment may be becoming illiquid. |

Implementation: compute PSI features weekly as part of post-scrape pipeline. Store in `drift_events` table. Grafana dashboard for visualization.

### 7.4 Experiment Tracking: MLflow

**Choice: MLflow** (self-hosted, open source).

| Factor | MLflow | W&B | Custom |
|---|---|---|---|
| Cost | Free (runs on same EC2) | $50+/month | Dev time |
| Python integration | Native | Native | N/A |
| Model registry | Built-in | Built-in | Would need to build |
| Experiment comparison | Good | Excellent | N/A |
| Overhead | Minimal (tracking server + artifact store) | None (SaaS) | None |

MLflow tracking server runs on the API instance. Artifacts (trained model files) stored locally or in S3. For a single data scientist/small team, this is more than sufficient.

### 7.5 Explainability (Mandatory per Prediction)

Every prediction includes:

```json
{
  "estimate": 125000,
  "range": {"low": 118000, "high": 132000},
  "confidence": "high",
  "explanation": {
    "comps_found": 34,
    "statistical_adjustments": [
      {"reason": "mileage", "amount": -5200,
       "detail": "Your car has 20,000 km more than segment average. Adjustment: -5,200 AED"},
      {"reason": "spec", "amount": 15000,
       "detail": "GCC spec commands a premium over US/Japan imports. Adjustment: +15,000 AED"},
      {"reason": "city", "amount": 3000,
       "detail": "Dubai prices average 2.5% above UAE national median. Adjustment: +3,000 AED"}
    ],
    "ml_shap": [
      {"feature": "mileage_km", "contribution": -8200},
      {"feature": "spec_GCC", "contribution": 12500},
      {"feature": "market_trend_4w", "contribution": 2400},
      {"feature": "seller_type_private", "contribution": -3000},
      {"feature": "days_to_sell_median", "contribution": 1800}
    ]
  },
  "knowledge": {
    "generation": "J200 (2008-2021)",
    "known_issues": ["Timing chain tensioner at ~120K km", "..."],
    "annual_maintenance_estimate": "4,500-6,500 AED",
    "market_liquidity": "Sells in ~18 days on average",
    "depreciation": {"year_1": 0.88, "year_3": 0.72, "year_5": 0.55}
  }
}
```

---

## 8. Feature Engineering

### 8.1 Modular Feature Pipeline

**Problem:** A single `features.py` becomes unmaintainable as feature count grows.

**Solution:** Modular feature directory with clear contracts.

```
engine/features/
├── __init__.py
├── base.py                  # BaseFeature abstract class
├── registry.py              # Feature registry (auto-discover)
│
├── listing_features.py      # Features from the listing itself
│   ├── MileageFeature
│   ├── SpecFeature
│   ├── AgeFeature
│   ├── SellerTypeFeature
│   └── PriceHistoryFeature
│
├── market_features.py       # Features from market context
│   ├── SegmentMedianPrice
│   ├── SegmentLiquidity
│   ├── PriceVolatility
│   ├── ListingVolume
│   └── MarketTrend4Week
│
├── vehicle_features.py      # Features from knowledge base
│   ├── BrandReliability
│   ├── DepreciationRate
│   ├── CommonIssueCount
│   └── PartsAvailability
│
├── temporal_features.py     # Time-based features
│   ├── DaysOnMarket
│   ├── PriceDropCount
│   ├── PriceDropMagnitude
│   └── SeasonalityIndex
│
└── geo_features.py          # Location-based features
    ├── CityPremium
    ├── CountryMarketSize
    └── ReexportHubProximity
```

Each feature implements:

```python
class BaseFeature(ABC):
    name: str
    version: str
    dependencies: list[str]  # other feature names this depends on

    @abstractmethod
    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        """Compute feature values for a DataFrame of listings."""
        ...

    @abstractmethod
    def compute_single(self, query: ValuationQuery,
                       context: MarketContext) -> float:
        """Compute feature value for a single valuation query."""
        ...
```

**Why this works:**
- Each feature is a ~30-line class with a single responsibility
- Tests are isolated per feature
- Adding a feature = new file + register it
- Feature version is tracked — if `MileageFeature` changes, `feature_version` bumps
- Dependencies are explicit — `MarketTrend4Week` declares it needs `SegmentMedianPrice`

**No feature store needed.** The `MarketContext` object is built on-demand from the database (cached per request). At this scale, querying PostgreSQL for market stats is a <50ms indexed query.

---

## 9. API Design

### 9.1 Endpoints

```
POST   /v1/valuate          # Submit car details, get valuation
GET    /v1/valuate/{id}     # Retrieve cached valuation by ID
GET    /v1/models            # List available makes → models → years
GET    /v1/models/{make}     # Models for a make
GET    /v1/models/{make}/{model}  # Years and trims
GET    /v1/trends            # Market trends (query params for segment)
GET    /v1/health            # Health check (public)
GET    /v1/stats             # Platform stats (listings count, coverage)
```

### 9.2 API Versioning Strategy

- **URL-based:** `/v1/valuate`, `/v2/valuate`
- **V1 is the only version until there's a breaking change.**
- **Breaking change definition:** removing a field, changing a field type, changing auth requirements
- **Non-breaking (no version bump):** adding new fields, adding new endpoints
- **Old versions:** deprecated with `Sunset` header, 6-month grace period, then removed
- **V2 trigger examples:** new valuation model with incompatible output schema, switch from JWT to OAuth

### 9.3 Idempotent Valuations

```python
def compute_cache_key(query: ValuationQuery) -> str:
    """Deterministic cache key for repeated valuation requests."""
    raw = (
        f"{query.make}|{query.model}|{query.year}|"
        f"{query.mileage_km or 'NA'}|{query.spec or 'NA'}|"
        f"{query.trim or 'NA'}|{query.city or 'NA'}|"
        f"{query.country}|"
        f"{datetime.now().strftime('%Y-%m-%d')}"  # same-day cache
    )
    return hashlib.sha256(raw.encode()).hexdigest()
```

- Same car details, same day → same cache key → return cached result
- Next day → new cache key → fresh valuation (market data may have changed)
- Cache stored in `valuation_queries` table with TTL of 24 hours
- If market data freshness is >24h (scraper failed), extend cache TTL and warn

### 9.4 Rate Limiting

```python
# Tiered rate limiting (FastAPI + slowapi)
RATE_LIMITS = {
    "anonymous":    "10/minute; 100/day",
    "registered":   "30/minute; 500/day",
    "enterprise":   "100/minute; 10000/day",
    "internal":     "unlimited",
}
```

Implemented via in-memory Redis-style counters (or actual Redis if needed). `X-RateLimit-Remaining` headers on every response.

---

## 10. Security Architecture

### 10.1 Security Layers

```
Internet
    │
    ▼
┌──────────────┐
│  CloudFront   │  DDoS protection, TLS termination, geo-filtering
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AWS WAF      │  Rate-based rules, SQL injection, XSS, bot control
└──────┬───────┘  (V2 — CloudFront built-in rules sufficient for V1)
       │
       ▼
┌──────────────┐
│  FastAPI      │
│  Middleware:  │
│  - Rate limiter (slowapi)                                │
│  - CORS (restrict to known origins)                      │
│  - Request validation (Pydantic)                         │
│  - Audit logging middleware                              │
│  - IP hash (for anonymous rate tracking, not PII)        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL   │  TLS, encrypted at rest, no public IP
└──────────────┘
```

### 10.2 Authentication

| Tier | Method | Scope |
|---|---|---|
| **Anonymous** | IP-based rate limit (hashed, not stored raw) | 10 valuations/day |
| **Registered user** | JWT (access + refresh tokens), Google/Apple sign-in | 50 valuations/day |
| **Enterprise** | API key (32-char random, stored hashed) | Contractual limits |
| **Internal** | Service account JWT | Unlimited, admin endpoints |

### 10.3 API Key Lifecycle

```
CREATE → ACTIVE → ROTATING → REVOKED
          │                       │
          │  User requests rotate  │
          ▼                       ▼
      ROTATING              REVOKED
    (old key still          (all access
     valid 48h)              denied)
```

API key stored as `SHA256(key)` in the database. The raw key is shown once at creation. Rotation generates a new key, old key invalidated after 48-hour overlap.

### 10.4 Secret Management

- **Development:** `.env` file (gitignored, never committed)
- **Production:** AWS Secrets Manager (or Doppler for simplicity)
- **Rotated secrets:** DB password, API signing keys, external API tokens
- **Rotation cadence:** 90 days for DB creds, on-compromise for API keys

### 10.5 Scraper Proxy & Anti-Detection

| Measure | When | Detail |
|---|---|---|
| **Residential proxy pool** | V2+ | Only if sources start blocking. BrightData or similar. $500+/month. |
| **User-Agent rotation** | V1 | Pool of 10 recent Chrome/Firefox UAs, rotate per request |
| **Fingerprint rotation** | V2 | Playwright with stealth plugin if needed |
| **CAPTCHA handling** | V2 | 2Captcha integration if needed. Not anticipated for these sources. |
| **Rate limiting (our side)** | V1 | 1-3 req/sec per source. Spread crawl across hours. |

**V1 stance:** Be a good citizen. Respect robots.txt. Identify yourself. Rate limit aggressively. If a source blocks us, we attempt contact before escalating to proxies. Most GCC classifieds do not employ sophisticated anti-bot measures.

### 10.6 Audit Logging

```python
# Middleware logs every API request:
{
    "timestamp": "2026-07-02T14:31:22Z",
    "method": "POST",
    "path": "/v1/valuate",
    "status_code": 200,
    "response_ms": 145,
    "ip_hash": "sha256:abc123...",
    "user_id": "user_xyz",           # null if anonymous
    "api_key_hash": "sha256:def456", # null if JWT
    "user_agent": "Mozilla/5.0...",
    "request_body_hash": "sha256:ghi789"  # for debugging, not PII
}
```

Audit logs stored in PostgreSQL (partitioned by month) with 90-day retention. For enterprise customers, audit logs are queryable via admin API.

---

## 11. Monitoring & Observability

### 11.1 Observability Stack

| Component | Tool | What It Tracks |
|---|---|---|
| **Metrics** | Prometheus + Grafana | API latency, request rate, error rate, scraper health, data freshness, model performance, drift |
| **Traces** | OpenTelemetry → Grafana Tempo (or Jaeger) | End-to-end request tracing: API → DB → model → response |
| **Logs** | structlog → stdout → Grafana Loki (or CloudWatch) | Structured JSON logs, correlated via trace_id |
| **Errors** | Sentry | Exception tracking, stack traces, error grouping |
| **Experiments** | MLflow | Model training runs, metrics, artifacts |
| **Alerts** | Grafana Alertmanager → Slack/email | Critical: scraper failure, model degradation, API down |

### 11.2 Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Every log line includes:
logger.info("valuation_computed",
    trace_id="abc123",
    cache_key="sha256:...",
    make="Toyota",
    model="Land Cruiser",
    year=2018,
    estimated_price=125000,
    confidence="high",
    comp_count=34,
    model_version="lightgbm_v2.3",
    response_ms=145)
```

No `print()`. No `logging.info("something happened")`. Every log is structured, searchable, and correlated.

### 11.3 Key Dashboards

**Dashboard 1: Platform Health**
- API: requests/min, p50/p95/p99 latency, error rate (5xx)
- DB: connection pool usage, query latency, deadlocks
- Scrapers: last success per source, records ingested, freshness

**Dashboard 2: Data Quality**
- Quality score distribution (histogram, per source)
- Rejection rate per source (sparkline over 12 weeks)
- Field extraction % per source (bar chart)
- Dead letter queue size

**Dashboard 3: Model Performance**
- Active model MAE over time (line chart, weekly)
- Shadow model comparison (side-by-side)
- Drift PSI per feature (heatmap)
- Prediction distribution (histogram, active vs shadow)

**Dashboard 4: Business Metrics**
- Valuations per day (by tier: anonymous, registered, enterprise)
- Top queried makes/models
- Low-confidence query % (are we covering the market?)
- Cache hit rate

### 11.4 Alerts

| Alert | Condition | Severity | Channel |
|---|---|---|---|
| Scraper failure | No successful run in 36h | Critical | Slack + email |
| API error rate >5% | 5xx/total > 0.05 for 5 min | Critical | Slack + PagerDuty |
| Data freshness >48h | Last successful scrape >48h ago | High | Slack |
| Model degradation | MAE > baseline × 1.3 for 50+ queries | High | Slack |
| Drift detected | PSI > 0.3 on any feature | High | Slack |
| DB disk >80% | Disk usage > 80% | Medium | Slack |
| Dead letter growth | Rejection rate >20% for a source | Medium | Slack |
| API latency p95 >2s | Sustained for 10 min | Medium | Slack |

---

## 12. Deployment Architecture

### 12.1 Infrastructure (AWS)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS (me-central-1, Bahrain)              │
│                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐           │
│  │  ECS Fargate (API)   │    │  ECS Fargate (Scraper)│          │
│  │  0.5 vCPU / 1 GB     │    │  1 vCPU / 2 GB        │          │
│  │  Auto-scale: 1-4     │    │  Cron schedule:       │          │
│  │  Docker: api:latest  │    │  Monday 02:00 GST     │          │
│  └──────────┬───────────┘    └──────────┬───────────┘           │
│             │                           │                        │
│             └───────────┬───────────────┘                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  RDS PostgreSQL 16 (db.t3.medium)                         │   │
│  │  2 vCPU / 4 GB / 50 GB SSD (gp3)                          │   │
│  │  Multi-AZ: no (V2)   Backups: automated, 7-day retention   │   │
│  │  Encryption: AWS KMS                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐           │
│  │  S3 (Raw Data)       │    │  CloudFront (CDN)     │           │
│  │  Standard tier       │    │  API cache            │           │
│  │  Lifecycle: 90-day   │    │  TLS termination      │           │
│  │  Compression: zstd   │    │                        │           │
│  └──────────────────────┘    └──────────────────────┘           │
│                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐           │
│  │  ECR (Docker images) │    │  Secrets Manager      │           │
│  └──────────────────────┘    └──────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 CI/CD Pipeline (GitHub Actions)

```
Pull Request
    │
    ▼
┌──────────────────┐
│  CI (every PR)    │
│  - lint (ruff)    │
│  - type-check     │
│  - test (pytest)  │
│  - coverage >80%?│
└──────┬───────────┘
       │  All green
       ▼
┌──────────────────┐
│  Merge to main    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  CD (main only)   │
│  - Build Docker   │
│  - Push to ECR    │
│  - Deploy to STG  │
│  - Smoke tests    │
│  - Deploy to PROD │
└──────────────────┘
```

### 12.3 Environments

| Environment | Purpose | Instance Size | Data |
|---|---|---|---|
| **dev** | Local Docker Compose. Full stack on developer machine. | Laptop | Synthetic/fixture data. Small scrape sample. |
| **staging** | AWS. Pre-production validation. | t3.small (API) + t3.micro (DB) | Subset of production data. No public access. |
| **production** | AWS. Public traffic. | t3.medium (API) + t3.medium (DB) | Full production data. |

### 12.4 Infrastructure as Code

**Terraform** (AWS-native, mature, widely understood):

```
infra/
├── terraform/
│   ├── main.tf              # Provider, state backend
│   ├── vpc.tf               # VPC, subnets, security groups
│   ├── rds.tf               # RDS PostgreSQL
│   ├── ecs.tf               # ECS cluster, services, tasks
│   ├── s3.tf                # Raw data bucket
│   ├── cloudfront.tf        # CDN
│   ├── secrets.tf           # Secrets Manager
│   ├── iam.tf               # Service roles
│   └── variables.tf         # Environment-specific vars
└── docker/
    ├── Dockerfile.api
    ├── Dockerfile.scraper
    └── docker-compose.yml   # Local dev
```

---

## 13. Development Phases & Roadmap

### Phase 0 — Foundation (Weeks 1-2)

**Goal:** Infrastructure, framework, one end-to-end scraper.

```
Deliverables:
├── Project scaffold (Python monorepo, Docker Compose)
├── PostgreSQL schema (all tables, indexes, partitions)
├── Scraper base class (rate limiter, retry, UA rotation, S3 raw storage)
├── Pandera schemas (validators for each source)
├── Quality scoring framework
├── Pipeline metadata framework
├── CI/CD pipeline (GitHub Actions)
├── MLflow server (self-hosted)
├── Terraform (dev + staging)
├── Structured logging setup (structlog + OpenTelemetry)
└── Dubizzle UAE scraper (end-to-end: fetch → parse → validate →
    score → promote → production, with raw S3 backup)
```

### Phase 1 — Core Data Pipeline + Statistical Engine (Weeks 3-6)

```
Deliverables:
├── P0 Scrapers:
│   ├── Dubizzle UAE + KSA
│   ├── YallaMotor (6 countries)
│   └── Haraj KSA
│
├── Post-scrape pipeline:
│   ├── Probabilistic delisting detection
│   ├── Cross-source deduplication
│   ├── Canonical vehicle resolution
│   └── Materialized view refresh
│
├── Statistical valuation engine:
│   ├── Hard-filter comp finder with weighted scoring
│   ├── Percentile computation + adjustments
│   └── Confidence scoring
│
├── API (/v1/valuate, /v1/models, /v1/trends, /v1/health)
│   ├── Idempotent cache keys
│   ├── Rate limiting
│   ├── API versioning
│   └── Audit logging
│
├── Monitoring:
│   ├── Prometheus metrics + Grafana dashboards
│   ├── Sentry error tracking
│   ├── Scraper health tracking
│   └── Pipeline run metadata
│
└── Knowledge base seed: Top 50 GCC models (specs, issues, costs)
```

### Phase 2 — Enrichment & First ML Model (Weeks 7-10)

```
Deliverables:
├── P1 Scrapers:
│   ├── CarSwitch UAE (inspection-grade listings)
│   ├── Emirates Auction (transaction prices)
│   └── OpenSooq (KW, OM, BH, QA)
│
├── ML pipeline:
│   ├── Feature engineering module (modular, per Section 8)
│   ├── Target construction (transaction price estimation)
│   ├── LightGBM training + evaluation
│   ├── SHAP explainability integration
│   ├── Shadow deployment mode
│   └── Human approval workflow
│
├── Drift detection (feature, target, prediction, market)
│
├── Product features:
│   ├── Price history chart (from snapshots)
│   ├── Depreciation curve per model
│   ├── Market liquidity indicator
│   ├── Good deal indicator
│   └── Ownership cost estimator
│
└── Monitoring dashboards (all 4 dashboards per Section 11.3)
```

### Phase 3 — Full GCC Coverage & Production Hardening (Weeks 11-14)

```
Deliverables:
├── P2 Scrapers:
│   ├── Syarah KSA
│   ├── Mazadak KSA (auction data for Saudi)
│   └── DubiCars UAE
│
├── Knowledge base expansion:
│   ├── JATO import (specs for all models)
│   ├── Partsouq scraper (parts pricing)
│   ├── DriveArabia community mining
│   └── Common issues database from listing text mining
│
├── Production deployment:
│   ├── AWS production environment (Terraform apply)
│   ├── CloudFront CDN
│   ├── Production monitoring + alerting
│   └── Load testing (verify 100 req/min sustained)
│
├── Security hardening:
│   ├── JWT auth (registered users)
│   ├── API key management (enterprise)
│   ├── WAF rules
│   └── Penetration test (basic)
│
└── Documentation:
    ├── Data dictionary
    ├── API reference (OpenAPI)
    ├── Scraper runbooks
    └── Deployment runbooks
```

### Phase 4 — V2 Features (Months 4-6+)

```
├── LLM valuation explanation
├── User accounts + saved valuations
├── Price alerts (email/push)
├── VIN decoding (JATO or other provider)
├── Dealer dashboard
├── Enterprise API tier (contracts, SLAs)
├── Mobile app (React Native, sharing API)
├── Image-based car detail extraction (OCR)
├── Recommendation engine ("cars you might like")
└── EV battery health estimation
```

---

## 14. Cost Estimates

### 14.1 Monthly Infrastructure (V1, AWS Bahrain)

| Resource | Spec | Monthly Cost |
|---|---|---|
| **ECS Fargate (API)** | 0.5 vCPU, 1 GB, 1-4 instances | $15–$40 |
| **ECS Fargate (Scraper)** | 1 vCPU, 2 GB, runs 4-6h/week | $3–$5 |
| **RDS PostgreSQL** | db.t3.medium, 50 GB gp3 | $80 |
| **S3 (raw data)** | ~10 GB stored, lifecycle auto-delete | $2 |
| **CloudFront** | ~5 GB egress/month | $2 |
| **Secrets Manager** | 5 secrets | $2 |
| **ECR** | Docker images | $1 |
| **Data transfer** | ~10 GB/month | $1 |
| **MLflow** | Self-hosted on API instance | $0 |
| **Grafana** | Self-hosted on API instance | $0 |
| **Sentry** | Free tier (5K errors/month) | $0 |
| **Claude API** | ~5K explanations/month, ~$0.003 each | $15 |
| **Exchange rate API** | Free tier | $0 |
| **Total** | | **$120–$150/month** |

### 14.2 One-Time Costs

| Item | Cost |
|---|---|
| JATO Middle East license (annual) | $5K–$15K |
| Domain name | $15/year |
| SSL certificates | Free (AWS ACM) |
| Terraform Cloud (free tier) | $0 |

### 14.3 Cost Optimization Built Into the Design

| Optimization | Saving |
|---|---|
| Single PostgreSQL (no separate search/vector/analytics DB) | $100–$200/month |
| No message queue (staging tables as queue) | $30–$50/month |
| Self-hosted MLflow + Grafana (no SaaS) | $50–$100/month |
| Scraper as spot instance (Fargate Spot) | 30% on scraper |
| CloudFront caching (reduce API hits) | Variable |
| S3 lifecycle policy (auto-delete raw after 90 days) | $5/month |
| Materialized views (avoid repeated expensive queries) | DB CPU savings |

---

## 15. Risk Assessment

### 15.1 Identified Risks

| # | Risk | Likelihood | Impact | Mitigation | V1 Acceptable? |
|---|---|---|---|---|---|
| 1 | **Source blocks scraping** | Medium | High — lose data pipeline | Proxy rotation, official API negotiation, diversify sources (not single-source dependent). If Dubizzle blocks us, we still have YallaMotor + CarSwitch + Haraj. | Yes — each source is replaceable. |
| 2 | **Legal challenge from source** | Low | High — may need to stop scraping a source | Respect robots.txt, rate limit, no republishing. Have partnership pitch ready. | Yes — risk is inherent to the model. |
| 3 | **No ground truth for ML** | Medium | Medium — ML accuracy limited | Emirates Auction data provides closest thing to transaction prices. Target construction from delisting patterns. Be transparent that estimates are market-based. | Yes — statistical model works without ground truth. |
| 4 | **GCC market seasonality** | High | Low — valuations fluctuate | Model includes seasonal features. Weekly retraining captures trends. | Yes — feature, not a bug. |
| 5 | **Model staleness in fast-moving market** | Medium | Medium — stale valuations | Weekly retraining + daily data freshness monitoring. Alert if data >48h stale. | Partially — acceptable for V1 with monitoring. |
| 6 | **Low comp count for rare cars** | High | Medium — inaccurate valuations | Tiered comp finder relaxes constraints. Confidence scoring warns users. Insufficient comps → return error, not bad estimate. | Yes — transparency is the mitigation. |
| 7 | **Parser breaks on site redesign** | Medium | High — data loss for that source | HTML structure hash monitoring. Alert on unexpected layout. Raw data preserved → can fix parser and re-process. | Yes — raw data preservation enables recovery. |
| 8 | **API abuse / scraping our API** | Medium | Medium — inflated costs, degraded service | Rate limiting, CloudFront, WAF (V2). Audit logs for detection. | Yes — rate limiting is sufficient for V1. |
| 9 | **DB performance degradation** | Low | Medium — slow valuations | Partitioning on snapshots. Index design. Materialized views. Query plan monitoring. | Yes — scale point is years away. |
| 10 | **Single point of failure (one DB instance)** | Medium | Medium — platform down | Multi-AZ in V2. Automated backups with point-in-time recovery. RTO: 1 hour. | Yes — acceptable for consumer tool at launch. |

### 15.2 Risk Not Mitigated in V1 (Acceptable)

- **Single AWS region:** If me-central-1 goes down, platform is down. Multi-region adds $80+/month and complexity. Acceptable for V1.
- **Single database instance:** No read replicas. Acceptable at <1,000 concurrent users.
- **No message queue for scraper:** If scraper crashes mid-run, restart from the beginning. Inefficient but acceptable for weekly batch.

---

## 16. Major Changes from Original Blueprint

| # | Change | Why | Impact |
|---|---|---|---|
| 1 | **Staging layer + quality pipeline** added | Raw → validate → normalize → score → promote. Prevents bad data from entering production. | Data reliability. ~1 week additional Phase 0 work. |
| 2 | **Raw data preservation** added (S3 + zstd) | Enables parser debugging, backfilling, and re-processing. Without it, bad parses are permanent. | ~$2/month S3. Critical for long-term maintainability. |
| 3 | **pgvector similarity search replaced** with hard filters + weighted scoring | Car comps are deterministic, not fuzzy. Hard filters are faster, more transparent, and more accurate for this domain. | Simpler, more explainable. pgvector kept for future use cases. |
| 4 | **Currency handling** — dual storage (original + normalized) | Overwriting prices with normalized values loses information. Corrections become impossible. | ~2 extra columns. Zero runtime cost. |
| 5 | **Delisting detection** changed from binary 404 to probabilistic | 404 isn't reliable. Multiple observations + confidence score = trustworthy sold signals. | Better transaction price proxy. |
| 6 | **Model promotion** changed from automated to shadow → human → production | Automated promotion without human review is dangerous for a consumer-facing product. | Safer. ~1 minute of engineer time per promotion. |
| 7 | **Feature engineering** modularized into directory structure | Single `features.py` becomes unmaintainable. Modular design enables independent testing and versioning. | Engineering quality. No runtime impact. |
| 8 | **Schema versioning** added to every ingestion table | Schemas evolve. Versioning enables safe migrations and rollbacks. | Essential for production data. |
| 9 | **Partitioning** added for `listing_snapshots` | Table will grow ~100K rows/week. Without partitioning, queries slow over time. | Query performance over years. |
| 10 | **Data lineage** added (pipeline_run_id everywhere) | Debugging a bad valuation requires tracing back through the pipeline. | Debuggability. Minimal storage cost. |
| 11 | **Batch metadata** added (pipeline_runs table) | Without run metadata, you can't answer "how healthy was last week's scrape?" | Operational visibility. |
| 12 | **Model registry** expanded with dataset hash, feature version, hyperparameters, approval status | The original registry was adequate but missed key metadata for debugging and rollback. | ML governance. |
| 13 | **Drift detection** added (feature, target, prediction, market) | Missing entirely from original blueprint. Models silently degrade without drift monitoring. | ML reliability. |
| 14 | **Explainability** made mandatory per prediction (SHAP + adjustments) | Original mentioned explainability but didn't design it into the response schema. | Core differentiator. Users trust what they understand. |
| 15 | **API versioning** (/v1/) and idempotent cache keys added | Prevent breaking changes from impacting consumers. Cache reduces compute for repeated queries. | API stability. |
| 16 | **Queue evaluated, rejected for V1** | Message queue adds operational complexity (RabbitMQ/Redis to manage, monitor, and pay for). Staging tables provide equivalent decoupling. | Explicit non-decision documented. |
| 17 | **Security expanded** — secret rotation, API key lifecycle, audit logs, proxy strategy, bot detection | Original had only basic security. Production API needs defense in depth. | Security posture. |
| 18 | **Pandera chosen** over Great Expectations for validation | GE is enterprise-grade overkill. Pandera fits the scale and integrates with the Python data stack. | Lower complexity, same validation quality. |
| 19 | **Observability expanded** — OpenTelemetry, structured logging, Grafana dashboards, alerts | Original monitoring was thin. Production needs traces, logs, metrics, and alerts. | Operational maturity. |
| 20 | **MLflow chosen** for experiment tracking | No experiment tracking in original. MLflow is free and sufficient. | ML reproducibility. |
| 21 | **Feature flags** added for safe rollout | Models, scrapers, endpoints need controlled rollout. | Deployment safety. |
| 22 | **Dead letter table** added | Rejected records shouldn't be silently dropped. Debugging needs visibility into what was rejected and why. | Data quality debugging. |
| 23 | **Scraper confidence scores** expanded to field-level extraction tracking | Original tracked scraper health as binary success/failure. Field-level tracking catches partial breakages. | Faster detection of parser issues. |
| 24 | **Deduplication** expanded to cross-source (canonical_vehicles table) | Same car on Dubizzle + YallaMotor should be recognized as one vehicle for market statistics. | More accurate market picture. |
| 25 | **Idempotent valuations** via hash-based cache keys | Repeated queries shouldn't recompute or create duplicate rows. | Performance + data cleanliness. |
| 26 | **Structured logging** (structlog) mandated over print/logging | Unstructured logs are useless at scale. Structured logs enable searching and correlation. | Operational maturity. |
| 27 | **Infrastructure as Code** (Terraform) specified | Manual AWS setup is not reproducible. Terraform ensures environments are identical. | DevOps maturity. |
| 28 | **Product feature prioritization** — Good Deal indicator, Price History, Liquidity promoted to V1 | Some features can ship in V1 because the data is already available. | Better V1 product. |
| 29 | **Cost optimization** — identified 7 specific savings | Original had no cost optimization analysis. | $100+/month saved. |
| 30 | **Risk assessment** added with acceptance criteria | Original had no risk analysis. | Informed decision-making. |

---

## 17. Engineering Scores

### Overall Engineering Score: **8.0 / 10**

| Dimension | Score | Notes |
|---|---|---|
| **Data quality** | 9/10 | Staging layer, validation, quality scoring, dead letter queue. Robust. |
| **MLOps** | 8/10 | Shadow deployment, human approval, drift detection, MLflow. Could add A/B testing framework. |
| **Observability** | 8/10 | OpenTelemetry, structured logging, Grafana, Sentry, alerts. Missing: synthetic monitoring for API endpoints. |
| **Security** | 7/10 | Defense in depth, API key lifecycle, audit logging. Missing: penetration test, WAF (deferred to V2). |
| **Scalability** | 7/10 | PostgreSQL handles 50 GB. Single instance. Design will scale to ~500K listings before needing architectural changes. Multi-AZ and read replicas deferred. |
| **Cost efficiency** | 9/10 | $120-150/month for full stack. Multiple cost optimizations identified. |
| **Maintainability** | 8/10 | Modular features, versioned schemas, raw data preservation, Terraform. Could use more integration tests. |
| **API design** | 8/10 | Versioned, rate-limited, idempotent, documented (OpenAPI). Missing: GraphQL alternative (not needed). |

### Production Readiness Score: **7.5 / 10**

**Ready for Phase 0-2 development. Not yet ready for public launch.** Gaps to close before public launch:

| Gap | Severity | Fix in Phase |
|---|---|---|
| Multi-AZ RDS for high availability | Medium | Phase 3 |
| WAF for API protection | Medium | Phase 2-3 |
| Penetration test | Medium | Phase 3 |
| Load testing (verify 100 req/min) | Medium | Phase 3 |
| Synthetic monitoring (health check from external region) | Low | Phase 3 |
| Disaster recovery test | Low | Phase 4 |

### Remaining Risks Acceptable for V1

1. **Scraping legal risk** — Acceptable because: diversified sources (no single-source dependency), public data only, good-citizen rate limiting. If any source objects, that source is removed without killing the platform.

2. **No transaction ground truth** — Acceptable because: statistical model works without it, Emirates Auction provides partial ground truth, confidence scores set user expectations correctly.

3. **Single region deployment** — Acceptable because: GCC users all connecting to Bahrain (<50ms latency), automated backups provide recovery, consumer tool doesn't need 99.99% uptime.

4. **No dedicated queue infrastructure** — Acceptable because: weekly batch is low-volume, staging tables provide recoverability, PostgreSQL is durable. Add queue only when scraping moves to continuous/daily.

---

*Blueprint v2.0 — End of Document*
