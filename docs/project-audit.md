# GCC Car Value Platform — Repository Audit

**Date:** 2026-07-12  
**Current Branch:** `feature-url-valuation` (HEAD at `427804b`)  
**Audit Scope:** Complete repository — 85 Python source files, 24 scripts, 14 test files, UI, Docker, CI/CD, docs

---

## 1. Repository Structure

```
gcc-car-value/
├── pyproject.toml              # Project config, deps, lint/test tooling
├── .env.example                # 6 environment variables
├── .gitignore                  # Standard Python ignores
├── README.md                   # Project overview + quick start
│
├── src/                        # Main application package
│   ├── __init__.py
│   ├── config.py               # Pydantic Settings (26 config fields)
│   │
│   ├── api/                    # FastAPI application layer
│   │   ├── main.py             # App entry point, router registration, UI serving
│   │   ├── dependencies.py     # Rate limiter + DB session dependency
│   │   ├── routes/
│   │   │   ├── health.py       # GET /v1/health
│   │   │   ├── valuation.py    # POST /v1/valuate
│   │   │   ├── models.py       # GET /v1/models[/{make}/{model}]
│   │   │   ├── url_valuate.py  # POST /v1/valuate-url
│   │   │   └── admin.py        # GET /v1/admin/stats|scrapers|quality
│   │   └── schemas/
│   │       └── valuation.py    # Pydantic request/response models
│   │
│   ├── db/                     # Database layer
│   │   ├── base.py             # DeclarativeBase + cross-DB type decorators (UUID, JSONB, DATERANGE)
│   │   ├── session.py          # Async engine + session factory
│   │   └── migrations/
│   │       ├── alembic.ini
│   │       ├── env.py          # Auto-imports all models for autogenerate
│   │       └── versions/
│   │           └── c42f2f2afaa8_initial_schema.py  # Single migration
│   │
│   ├── models/                 # SQLAlchemy ORM models (18 tables)
│   │   ├── __init__.py         # Re-exports all models + Base
│   │   ├── base.py             # (empty — real base in db/base.py)
│   │   ├── listing.py          # Core listings table
│   │   ├── listing_snapshot.py # Time-partitioned price snapshots
│   │   ├── canonical_vehicle.py# Cross-source dedup anchor
│   │   ├── valuation_query.py  # Idempotent valuation cache
│   │   ├── pipeline_run.py     # Scraper run metadata
│   │   ├── dead_letter.py      # Rejected records
│   │   ├── scraper_health.py   # Field-level extraction stats
│   │   ├── model_registry.py   # ML model lifecycle tracking
│   │   ├── drift_event.py      # Feature/target/prediction drift
│   │   ├── feature_flag.py     # Feature rollout control
│   │   ├── car_spec.py         # Knowledge base: specs
│   │   ├── car_issue.py        # Knowledge base: issues
│   │   ├── maintenance_cost.py # Knowledge base: costs
│   │   ├── depreciation_curve.py# Knowledge base: depreciation
│   │   ├── model_rating.py     # Knowledge base: ratings
│   │   ├── user_account.py     # User auth (email/password/JWT)
│   │   ├── saved_valuation.py  # User-saved valuations
│   │   └── price_alert.py      # Price alert subscriptions
│   │
│   ├── pipeline/               # Data processing pipeline
│   │   ├── validator.py        # Pandera schema validation
│   │   ├── normalizer.py       # Make/spec/city/currency normalization
│   │   ├── quality.py          # Quality scoring (0-100)
│   │   ├── promoter.py         # Promote/reject → listings or dead_letter
│   │   └── orchestrator.py     # Coordinates scraper→pipeline flow
│   │
│   ├── engine/                 # Valuation & ML engine
│   │   ├── statistical.py      # Percentile-based valuation with adjustments
│   │   ├── comp_finder.py      # Tiered hard-filter comp finder with scoring
│   │   ├── trainer.py          # LightGBM training pipeline
│   │   ├── drift.py            # PSI-based drift detection
│   │   ├── llm_explainer.py    # Claude API + template explanations
│   │   ├── recommendations.py  # Content-based car recommendations
│   │   ├── vin_decoder.py      # VIN validation + WMI/decoding
│   │   └── features/
│   │       ├── base.py         # BaseFeature ABC + FeatureRegistry
│   │       ├── listing_features.py
│   │       ├── market_features.py
│   │       └── vehicle_features.py
│   │
│   ├── scrapers/               # Web scrapers (10 sources)
│   │   ├── base.py             # Abstract BaseScraper + ScraperResult
│   │   ├── rate_limiter.py     # Token-bucket rate limiter
│   │   ├── session.py          # httpx session factory
│   │   ├── raw_storage.py      # S3/local raw data preservation
│   │   ├── dubizzle_uae/       # Scraper + dedicated parser
│   │   ├── dubizzle_ksa/
│   │   ├── yallamotor/
│   │   ├── haraj_ksa/
│   │   ├── carswitch/
│   │   ├── emirates_auction/
│   │   ├── opensooq/
│   │   ├── syarah/
│   │   ├── mazadak/
│   │   └── dubicars/
│   │
│   ├── knowledge/              # Knowledge base
│   │   └── seed.py             # 32 models × 12 brands curated data
│   │
│   ├── auth/                   # Authentication
│   │   └── jwt.py              # JWT create/verify + API key management
│   │
│   └── observability/          # Monitoring
│       ├── logging.py          # structlog setup
│       └── metrics.py          # Prometheus metrics
│
├── tests/                      # Test suite (14 files, 60 tests)
│   ├── conftest.py             # DB + settings fixtures
│   ├── test_models.py          # Model instantiation tests
│   ├── test_integration.py     # API integration tests
│   ├── test_auth.py            # JWT + API key tests
│   ├── test_knowledge.py       # Knowledge base seeding tests
│   ├── test_phase4.py          # Phase 4 features (LLM, VIN, recs)
│   ├── pipeline/
│   │   ├── test_validator.py
│   │   ├── test_normalizer.py
│   │   └── test_quality.py
│   ├── engine/
│   │   ├── test_statistical.py
│   │   └── test_comp_finder.py
│   └── scrapers/
│       └── test_base.py
│
├── ui/                         # Static frontend
│   ├── index.html              # Main SPA (valuation, browse, market, i18n)
│   ├── browse-market.js        # Browse + Market page JS
│   ├── browse-test.js          # Browse page tests
│   ├── fix-forms.js            # Form polyfills
│   ├── test.html               # Test harness
│   └── previews/               # UI concept mockups
│       ├── a-minimal.html
│       ├── b-dashboard.html
│       └── c-gulf.html
│
├── scripts/                    # Build & utility scripts (24 files)
│   ├── build_ui.py, build_v2.py, rebuild_ui.py, update_ui.py
│   ├── step1.py, step1b.py, step2.py, final_fix.py
│   ├── add_browse_market.py, add_i18n.py, add_toasts.py
│   ├── autocomplete.py, all_typeable.py
│   ├── fix_applylang.py, fix_both.py, restructure_buy.py
│   ├── seed_all.py, seed_missing_brands.py
│   ├── scrape_prod.py, scrape_yallamotor.py, bulk_scrape.py
│   ├── dubicars_scraper.py, haraj_gql_scraper.py
│   └── write_final.py
│
├── docker/                     # Container config
│   ├── Dockerfile.api
│   ├── Dockerfile.scraper
│   └── docker-compose.yml      # 4 services: api, db, mlflow, localstack
│
├── .github/workflows/
│   └── ci.yml                  # Lint + type-check + test on PR/push to main
│
└── docs/
    ├── reports/
    │   └── 2026-07-12-progress-report.md
    └── superpowers/
        ├── specs/
        │   └── 2026-07-02-gcc-car-value-blueprint.md  # 1,903 lines
        └── plans/
            └── 2026-07-02-phase-0-foundation.md
```

---

## 2. Architecture Overview

### High-Level Architecture

```
Scrapers (10 sources) → Raw S3 → Parse → Validate (Pandera) → Normalize →
Quality Score → Deduplicate → Promote → PostgreSQL → Valuation Engine →
FastAPI (/v1/*) → Static UI (index.html)
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI (async) | Native async, automatic OpenAPI docs |
| Database | PostgreSQL 16 (via SQLAlchemy 2.0 async) | Handles 50 GB, mature, pgvector available |
| ORM | SQLAlchemy 2.0 async + Alembic | Industry standard, Alembic for migrations |
| Validation | Pandera (DataFrame-native) | Lighter than Great Expectations, Python-native |
| Queue | Staging tables as logical queue | V1 volume doesn't justify message broker |
| Comp finder | Hard filters + weighted scoring | Deterministic, transparent, no pgvector needed |
| ML | LightGBM + SHAP (MLflow tracking) | Gradient boosting works well for tabular pricing |
| Scraping | httpx + BeautifulSoup (no headless browser) | Sufficient for GCC classifieds |
| Auth | JWT (HS256) + API keys (SHA-256 hashed) | Simple, stateless, no external IdP needed |
| Logging | structlog (structured JSON) | Searchable, correlated via trace_id |
| Frontend | Single HTML file + vanilla JS | No build step, zero dependencies, fast iteration |

### Cross-Database Compatibility

The codebase includes `UniversalUUID`, `UniversalJSONB`, and `UniversalDATERANGE` type decorators in `src/db/base.py` that adapt between PostgreSQL native types and SQLite/CHAR fallbacks. This enables local development with SQLite while targeting PostgreSQL in production. **Notable:** The `asyncpg` driver requirement means PostgreSQL is effectively required at runtime.

---

## 3. Backend Modules

### 3.1 API Layer (`src/api/`)

**Entry point:** `src/api/main.py`
- Creates FastAPI app with CORS, rate limiting, structured logging
- Registers 5 routers under `/v1/` prefix
- Serves `ui/index.html` at `/` with no-cache headers
- Mounts `ui/` as static files

**Routers:**

| Router | Endpoints | Description |
|--------|-----------|-------------|
| `health.py` | `GET /v1/health` | DB connectivity check |
| `valuation.py` | `POST /v1/valuate` | Main valuation endpoint with caching |
| `models.py` | `GET /v1/models`, `/{make}`, `/{make}/{model}` | Dynamic dropdown population from listings |
| `url_valuate.py` | `POST /v1/valuate-url` | Paste listing URL, auto-parse + valuate |
| `admin.py` | `GET /v1/admin/stats\|scrapers\|quality` | Platform monitoring endpoints |

**Dependencies:**
- `get_db()` — yields async DB session
- `limiter` — slowapi rate limiter (10/min anonymous)

### 3.2 Database Layer (`src/db/`)

- `base.py`: `DeclarativeBase` + 3 cross-DB type decorators + `LineageMixin` (schema_version, parser_version, normalizer_version, pipeline_run_id, ingested_at)
- `session.py`: Async engine from `DATABASE_URL` env var, pool size 10, max overflow 5
- `migrations/`: Single Alembic migration (`c42f2f2afaa8`) creating all initial tables

### 3.3 Models (`src/models/`) — 18 Tables

**Core Data:**
- `listings` — Main production table (source, external_id UNIQUE, vehicle identity, dual price storage, quality, lineage)
- `listing_snapshots` — Time-series price snapshots per listing
- `canonical_vehicles` — Cross-source dedup anchor (UNIQUE make+model+year+generation)

**Pipeline:**
- `pipeline_runs` — Batch metadata (volume, quality distribution, errors, versions)
- `dead_letter` — Rejected records with rejection reason
- `scraper_health` — Field-level extraction rates per run

**ML Operations:**
- `model_registry` — Model lifecycle (training→evaluating→shadow→approved→active→rolled_back→archived)
- `drift_events` — PSI values, threshold exceeded, acknowledge status
- `feature_flags` — Name, enabled, rollout %, target users

**Knowledge Base:**
- `car_specs` — Engine options, transmission, drivetrain, fuel economy, warranty
- `car_issues` — Known issues with severity, mileage, repair cost estimates
- `maintenance_costs` — Service intervals, minor/major costs, insurance estimates
- `depreciation_curves` — Residual % by year (1-10)
- `model_ratings` — Reliability, comfort, performance, fuel, offroad, resale (1-5 scale)

**Users:**
- `user_accounts` — Email, PBKDF2-hashed password, tier, API key hash
- `valuation_queries` — Idempotent cache (SHA-256 key), full input+output storage
- `saved_valuations` — User-bookmarked valuations
- `price_alerts` — Email alerts for price changes on saved models

### 3.4 Pipeline (`src/pipeline/`)

Implements the blueprint's 7-step pipeline:

1. **Validator** (`validator.py`): Pandera `ListingSchema` — type checks, range checks, cross-field validation (year ≤ current+1, no test-post prices like 1/123/1234), suspicious price detection
2. **Normalizer** (`normalizer.py`): 32 make aliases, 12 spec aliases, 13 city aliases, 8 currency exchange rates (AED/SAR/QAR/KWD/BHD/OMR/USD), computes `normalized_price_aed`
3. **Quality Scorer** (`quality.py`): Base 100, -5 per missing optional field, -10 mileage outlier (>400K), -15 year anomaly (<1995), -30 suspicious price (<1000 AED), -20 high price (>5M AED)
4. **Promoter** (`promoter.py`): Score ≥ 60 → promote to `listings` (upsert by source+external_id). Below threshold → `dead_letter`
5. **Orchestrator** (`orchestrator.py`): Iterates scrapers, records `PipelineRun` metadata
6. **Deduplication**: Handled in promoter via source+external_id UNIQUE constraint
7. **Delisting Detection**: Handled via listing status + `delisting_confidence` field

### 3.5 Valuation Engine (`src/engine/`)

**Statistical Model** (`statistical.py`):
- Finds comps via `comp_finder.py` → computes P10/P25/P50/P75/P90
- Applies adjustments: mileage delta (0.25 AED/km), spec premium (GCC vs non-GCC), city premium
- Confidence scoring: HIGH (≥30 comps, CV<0.15), MEDIUM (≥10, CV<0.30), LOW (≥5), INSUFFICIENT (<5)
- Bootstrap 80% confidence interval (1000 iterations)
- Returns ≤10 comps with platform attribution (no URLs exposed)

**Comp Finder** (`comp_finder.py`):
- 3-tier hard filters: strict (year±2, mileage±30%, same spec+country) → relaxed (year±3, mileage±50%, any spec) → GCC-wide (year±4, mileage±75% any country)
- Weighted scoring: recency (0 to -30), mileage closeness (up to -25), year match (-8/yr), spec match (0 to -15), country match (0 to -10), quality bonus (+0 to +10), sold comp bonus (+5 to +8)
- Human-readable platform attribution: "Found on Dubizzle UAE, Dubai"

**LightGBM Trainer** (`trainer.py`):
- Builds training dataset from ≥1000 quality listings
- Target construction: asking price × 0.95 (if sold_confirmed) × 0.93 (if high delisting confidence)
- Trains LightGBM with 200 estimators, max_depth=7, learning_rate=0.05
- Reports MAE, MAPE, R²
- Registers model in `model_registry` table with dataset hash, feature version, hyperparameters

**Drift Detection** (`drift.py`):
- PSI (Population Stability Index) computation
- 4 drift types: feature (PSI>0.2), target (price median shift >15%), prediction (MAE degradation >30%), market (volume drop >40% or volatility spike >2x)
- Logs to `drift_events` table

**Feature Engineering** (`features/`):
- `BaseFeature` ABC with `compute()` and `compute_single()` methods
- `FeatureRegistry` with auto-discovery and topological dependency sort
- 3 feature modules: `listing_features.py`, `market_features.py`, `vehicle_features.py`
- `MarketContext` dataclass carries segment stats from DB for single-query feature computation

**Phase 4 Modules:**
- `llm_explainer.py`: Template-based explanations by default, Claude API enhancement when `CLAUDE_API_KEY` is set (targets `claude-sonnet-4-6`, falls back to template on error)
- `recommendations.py`: Content-based recommendations from budget, body type, family size, preferring GCC spec; scores by budget fit, popularity, knowledge base ratings
- `vin_decoder.py`: ISO 3779 VIN validation, WMI lookup (27 manufacturers), VIN year decoding (2010-2030)

### 3.6 Scrapers (`src/scrapers/`) — 10 Sources

| Source | Directory | Country Coverage | Parser Type |
|--------|-----------|-----------------|-------------|
| Dubizzle UAE | `dubizzle_uae/` | 🇦🇪 AE | Dedicated parser (`parser.py`) |
| Dubizzle KSA | `dubizzle_ksa/` | 🇸🇦 SA | Inline in scraper |
| YallaMotor | `yallamotor/` | AE, SA, QA, KW, BH, OM | Inline in scraper |
| Haraj KSA | `haraj_ksa/` | 🇸🇦 SA | Inline in scraper |
| CarSwitch | `carswitch/` | 🇦🇪 AE | Inline in scraper |
| Emirates Auction | `emirates_auction/` | 🇦🇪 AE | Inline in scraper |
| OpenSooq | `opensooq/` | KW, OM, BH, QA | Inline in scraper |
| Syarah | `syarah/` | 🇸🇦 SA | Inline in scraper |
| Mazadak | `mazadak/` | 🇸🇦 SA | Inline in scraper |
| DubiCars | `dubicars/` | 🇦🇪 AE | Inline in scraper |

**Base Scraper Pattern:**
- `BaseScraper` ABC with: `fetch_index()`, `fetch_listing()`, `parse()`, `run()`
- Rate limiter (token bucket, configurable RPS)
- Raw HTML preserved to S3/local before parsing
- Per-run `ScraperResult` with records_ingested, pages_crawled, errors

**Note:** Only Dubizzle UAE has a separate `parser.py` module. All other scrapers have parsing logic inline in `scraper.py`. Most scraper implementations are stubs (the abstract methods are defined but actual extraction logic varies in completeness).

### 3.7 Authentication (`src/auth/`)

- JWT creation/verification (HS256, 24-hour expiry)
- API key generation: `gccv_` prefix + 32 hex chars, stored as SHA-256 hash
- `UserAccount` model with PBKDF2-SHA256 password hashing (100K iterations)
- Token payload: `sub` (user_id), `tier` (registered/enterprise), `iat`, `exp`

### 3.8 Knowledge Base (`src/knowledge/`)

`seed.py` contains curated data for 32 models across 12 brands:
- **Toyota:** Land Cruiser, Prado, Camry, Corolla, Hilux, Fortuner, RAV4
- **Nissan:** Patrol, Sunny, Altima
- **Honda:** Accord, Civic, CR-V
- **Hyundai:** Tucson, Santa Fe, Elantra
- **Kia:** Sportage, Sorento
- **Mitsubishi:** Pajero, Lancer
- **Mazda:** CX-5, CX-9
- **Ford:** Explorer, Expedition
- **Chevrolet:** Tahoe
- **BMW:** 5 Series, X5
- **Mercedes-Benz:** E-Class, S-Class
- **Lexus:** LX, ES
- **GMC:** Yukon
- **Land Rover:** Range Rover

Each model includes: generation info, engine specs, transmission options, drivetrain, fuel economy, known issues (with severity/typical mileage/repair cost), maintenance schedules, depreciation curves (residual % at years 1/2/3/5/7/10), and 1-5 ratings across 7 dimensions.

---

## 4. Frontend (`ui/`)

### Architecture
- **Single HTML file** (`index.html`, ~421 lines) — no build step, no framework
- Inline CSS + vanilla JavaScript
- All JS functions defined inline in `<script>` tags
- Pages: Home (buyer/seller landing), Valuation Form, Results, Browse Models, Market Trends
- Communication: `fetch()` calls to `/v1/*` endpoints

### Key Features Implemented
- Buyer/seller landing page with role selection
- Valuation form with autocomplete (typeable inputs replacing dropdowns)
- URL paste: paste any listing URL → backend fetches + parses + valuates
- Results display: estimate, range, confidence, comps, adjustments, knowledge
- Deal indicator: Great Deal / Fair Deal / Above Market
- Browse Models: Make → Model → Year drilldown with listing counts
- Market Trends page: stats + top makes bar chart
- EN/AR language toggle with full RTL support + localStorage persistence
- Floating toast notifications (replacing `alert()`)
- Anti-bot blocking detection with site-specific messages
- Premium fonts: Playfair Display + DM Sans (Google Fonts)
- Gold-gradient branded "CAR VALUATOR" header
- Zero-cache headers on UI responses

### Supporting JS Files
- `browse-market.js` (70 lines): Browse + Market page logic
- `browse-test.js` (29 lines): Browse page test utilities
- `fix-forms.js` (7 lines): Form element polyfills

### Previews
- `a-minimal.html` (49 lines): Minimalist UI concept
- `b-dashboard.html` (61 lines): Dashboard-style layout
- `c-gulf.html` (60 lines): Gulf-themed variant

---

## 5. Database

### Tables (18 total)

**Production Data (3):**
- `listings` — 30+ columns including dual price storage, quality scores, lineage, S3 reference
- `listing_snapshots` — Time-partitioned (monthly), per-listing price history
- `canonical_vehicles` — UNIQUE(make, model, year, generation)

**Pipeline (3):**
- `pipeline_runs` — Batch metadata per scraper run
- `dead_letter` — Rejected records with rejection reasons
- `scraper_health` — Field-level extraction statistics

**ML Operations (3):**
- `model_registry` — Full model lifecycle (9 statuses)
- `drift_events` — PSI values with acknowledge tracking
- `feature_flags` — Name, enabled, rollout %, target users

**Knowledge Base (5):**
- `car_specs`, `car_issues`, `maintenance_costs`, `depreciation_curves`, `model_ratings`

**Users & Engagement (3):**
- `user_accounts` — PBKDF2-hashed passwords, API key hashes
- `saved_valuations`, `price_alerts`

**Cache (1):**
- `valuation_queries` — SHA-256 cache key, full input+output, 24h TTL

### Indexes
- `(source, external_id)` UNIQUE on listings
- `(make, model, year)` on listings
- `(status)` on listings
- `(country, city)` on listings
- `(quality_score)` on listings
- `(canonical_vehicle_id)` FK index
- `(pipeline_run_id)` on listings and snapshots
- `(listing_id, captured_at)` on snapshots
- `(cache_key)` UNIQUE on valuation_queries
- `(queried_at)` on valuation_queries
- `(started_at)` on pipeline_runs
- `(detected_at, drift_type)` on drift_events

### Migration Status
- **1 migration:** `c42f2f2afaa8_initial_schema.py` — Creates all 18 tables
- Migrations run via Alembic in Docker Compose startup

---

## 6. API Endpoints

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|-----------|-------------|
| `GET` | `/v1/health` | None | None | DB health check |
| `POST` | `/v1/valuate` | None | 10/min | Valuation with 24h cache |
| `POST` | `/v1/valuate-url` | None | None | URL paste → auto-parse + valuate |
| `GET` | `/v1/models` | None | None | List makes with counts |
| `GET` | `/v1/models/{make}` | None | None | List models for make |
| `GET` | `/v1/models/{make}/{model}` | None | None | List years + trims |
| `GET` | `/v1/admin/stats` | None | None | Platform statistics |
| `GET` | `/v1/admin/scrapers` | None | None | Scraper health status |
| `GET` | `/v1/admin/quality` | None | None | Quality score distribution |
| `GET` | `/` | None | None | Serves `ui/index.html` |

**Notable:** Admin endpoints have no authentication — this is a security gap for production.

---

## 7. ML Components

### Training Pipeline
1. `build_training_dataset()` — Queries ≥1000 quality listings, builds DataFrame
2. `_construct_target()` — Estimates transaction price from asking price + signals
3. `train_model()` — 85/15 split, LightGBM regressor, returns model + metrics
4. `train_and_register()` — Full pipeline → `ModelRegistry` row with dataset hash

### Model Lifecycle
```
training → evaluating → shadow → approved → active
                ↓            ↓          ↓
             archived    rolled_back  archived
```

### Feature Engineering
- Modular feature directory with `BaseFeature` ABC
- Feature registry with topological dependency sort
- 3 feature modules (listing, market, vehicle) — referenced but implementation is thin

### Drift Detection
- Feature drift: PSI > 0.2 warning, > 0.3 alert
- Target drift: Median price change > 15%
- Prediction drift: MAE degradation > 30%
- Market drift: Volume drop > 40% or volatility spike > 2x

### Explainability
- Statistical adjustments exposed per valuation (mileage, spec, city)
- SHAP values planned for ML model (referenced in schemas)
- Claude API integration for natural-language explanations (with template fallback)

---

## 8. Scrapers

### Base Framework
- `BaseScraper` ABC with standardized `run()` method
- Token-bucket rate limiter (configurable RPS, default 2.0)
- httpx async HTTP client with configurable User-Agent and timeouts
- Raw storage abstraction (S3 in production, local filesystem in dev)
- `ScraperResult` dataclass tracking per-run stats

### Source Coverage
- **P0 (Phase 0-1):** Dubizzle UAE, Dubizzle KSA, YallaMotor, Haraj KSA
- **P1 (Phase 2):** CarSwitch, Emirates Auction, OpenSooq
- **P2 (Phase 3):** Syarah, Mazadak, DubiCars

### Scraper Health Monitoring
- `scraper_health` table tracks field-level extraction rates
- Admin endpoint `/v1/admin/scrapers` reports last run + staleness
- Alert: no successful run in 36h → critical
- Alert: field extraction rate drops >20% WoW → warning

### Known Issues
- Dubizzle blocks automated access (detected via anti-bot page indicators)
- URL valuation endpoint has specific error handling for blocked sites
- Most scraper implementations are structural stubs — actual extraction logic varies in completeness
- Only Dubizzle UAE has a dedicated parser module

---

## 9. Configuration

### Settings (`src/config.py`)

26 configuration fields via Pydantic `BaseSettings`, loaded from `.env`:

| Category | Fields | Default |
|----------|--------|---------|
| Database | `database_url`, `database_url_sync`, `db_pool_size`, `db_max_overflow` | localhost:5432 |
| Scraping | `scraper_rate_limit_rps` (2.0), `scraper_max_retries` (3), `scraper_retry_delay_seconds` (5.0), `scraper_user_agent`, `scraper_request_timeout` (30) | Varies |
| S3 | `s3_bucket`, `s3_endpoint_url`, `s3_access_key`, `s3_secret_key`, `s3_region` | me-central-1 |
| Quality | `quality_promotion_threshold` | 60 |
| API | `api_rate_limit_anonymous` (10/min), `api_rate_limit_registered` (30/min), `api_cors_origins`, `api_title`, `api_version` | localhost:3000 |
| Observability | `log_level` (INFO), `otel_enabled` (False) | — |
| Environment | `environment` | development |
| Auth | `jwt_secret` | Hardcoded dev default |

**Risk:** `jwt_secret` has a hardcoded default (`"dev-secret-change-in-production-gcc-car-value-2026"`). No validation that it's been changed in production.

### Environment Variables (`.env.example`)
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gcc_car_value
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/gcc_car_value
S3_BUCKET=gcc-car-value-raw-dev
S3_ENDPOINT_URL=http://localhost:4566
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

---

## 10. Observability

### Implemented
- **structlog** for structured JSON logging (`src/observability/logging.py`)
- **Prometheus** client metrics (`src/observability/metrics.py`) — 9 lines, thin
- Per-request logging on valuation endpoints (cache hits, computations, URL parses)
- Pipeline run metadata in `pipeline_runs` table
- Scraper health tracking in `scraper_health` table
- Drift events logged to `drift_events` table
- Admin endpoints for stats, scraper health, quality metrics

### Not Implemented / Deferred
- OpenTelemetry tracing (disabled by default, `otel_enabled=False`)
- Grafana dashboards (referenced in blueprint but not implemented)
- Sentry error tracking (referenced but not configured)
- Structured logging not consistently applied (some modules use it, others don't)
- No alerting implementation (blueprint defines 8 alert rules, none wired up)

---

## 11. Infrastructure

### Docker Compose (4 services)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `api` | Dockerfile.api | 8000 | FastAPI app |
| `db` | pgvector/pgvector:pg16 | 5432 | PostgreSQL with pgvector |
| `mlflow` | python:3.12-slim | 5000 | MLflow tracking server |
| `localstack` | localstack/localstack | 4566 | S3 emulation for dev |

### CI/CD (GitHub Actions)
- **Trigger:** PR to main, push to main
- **Jobs:** lint (ruff) → type-check (mypy) → test (pytest with PostgreSQL service container) → coverage upload (Codecov)
- **Python:** 3.12
- **Test DB:** pgvector/pgvector:pg16

### Dockerfiles
- `Dockerfile.api`: API service container
- `Dockerfile.scraper`: Scraper service container (separate for independent scaling)

### AWS Infrastructure (Blueprint, Not Implemented)
The blueprint specifies Terraform for: ECS Fargate (API + Scraper), RDS PostgreSQL (t3.medium), S3 (raw data), CloudFront (CDN), Secrets Manager. This is **not implemented** in the current codebase — only docker-compose for local dev exists.

---

## 12. Current Branch: `feature-url-valuation`

### Status: Active development, 72 files ahead of master (+7,484 / -12 lines)

### Recent Commits (last 15)
| Commit | Type | Description |
|--------|------|-------------|
| `427804b` | docs | Add README, clean up debug files |
| `45a1d5a` | fix | Typeable inputs: datalists for spec/city/country, number for year |
| `3a3c699` | fix | Autocomplete wrapper auto-creation for dynamic forms |
| `551df81` | fix | Autocomplete using class-based selectors for dynamic forms |
| `61dc92e` | revert | Back to stable working state |
| `e50ebee` | feat | ALL fields typeable, zero dropdowns |
| `9e08ed1` | fix | Typeable autocomplete for Make/Model/Spec/City/Country |
| `d307c2f` | feat | Smart autocomplete for 20+ brands |
| `c2e8ea2` | feat | URL paste toggle button below Analyze |
| `48f55cc` | feat | Toast notifications replacing alerts |
| `8b74883` | fix | Chrome headers for URL fetch, Dubizzle blocking handled |
| `17c5534` | fix | Source-specific parsers before generic fallback |
| `afba2fe` | feat | Ultra-lenient URL parser, 21 seed cars |
| `f50e475` | feat | URL paste tab on buying page |

### Branch Chain (Linear, Never Merged)
```
master (5be0633)           ← Phase 0-1 complete
  ↓
phase-2-ml-enrichment (3e74b43)  ← Phase 2
  ↓
phase-3-production (0a5a412)     ← Phase 3
  ↓
phase-4-v2-features (2215c9d)    ← Phase 4
  ↓
feature-url-valuation (427804b)  ← Current HEAD
```

---

## 13. Completed Features

### Phase 0 (Foundation) ✅
- [x] Project scaffold (pyproject.toml, config, .env, .gitignore)
- [x] PostgreSQL schema (18 tables, indexes, type decorators)
- [x] Scraper base class with rate limiter, retry, UA rotation, raw storage
- [x] Pandera validation schemas
- [x] Quality scoring framework
- [x] Pipeline metadata framework
- [x] CI/CD pipeline (GitHub Actions: lint + type-check + test)
- [x] MLflow server (Docker Compose)
- [x] Structured logging setup (structlog)
- [x] Alembic migrations
- [x] Dubizzle UAE scraper (end-to-end)

### Phase 1 (Core Pipeline) ✅
- [x] YallaMotor scraper (6 countries)
- [x] Haraj KSA scraper
- [x] Dubizzle KSA scraper
- [x] Statistical valuation engine (percentile + adjustments)
- [x] Tiered comp finder with weighted scoring
- [x] Confidence scoring (high/medium/low/insufficient)
- [x] API endpoints (/valuate, /models, /health)
- [x] Idempotent cache keys (SHA-256)
- [x] Rate limiting (slowapi)
- [x] Knowledge base seed (32 models, 12 brands)

### Phase 2 (ML + Enrichment) ✅
- [x] Modular feature engineering (BaseFeature ABC + registry)
- [x] LightGBM training pipeline
- [x] Target construction (asking→transaction price)
- [x] Shadow deployment mode (model_registry)
- [x] Drift detection (PSI: feature, target, prediction, market)
- [x] CarSwitch, Emirates Auction, OpenSooq scrapers
- [x] Good Deal indicator (great/fair/above market)

### Phase 3 (Production Hardening) ✅
- [x] Syarah, Mazadak, DubiCars scrapers
- [x] JWT authentication (create/verify)
- [x] API key management (generation, hashing, verification)
- [x] User account model (PBKDF2 password hashing)
- [x] Admin monitoring endpoints (/admin/stats, /admin/scrapers, /admin/quality)
- [x] Normalizer (32 make aliases, 12 spec aliases, 8 currencies)
- [x] Promoter (quality threshold → listings or dead_letter)

### Phase 4 (V2 Features) ✅
- [x] LLM explainer (Claude API + template fallback)
- [x] VIN decoder (ISO 3779 validation, WMI lookup, year decoding)
- [x] User accounts, saved valuations, price alerts (models defined)
- [x] Recommendation engine (budget, body type, family size scoring)
- [x] Delisting detection (probabilistic confidence scoring)

### UI Polish (feature-url-valuation) ✅
- [x] Consumer-facing UI with forms, results, comps, knowledge base
- [x] URL paste valuation
- [x] EN/AR language toggle with RTL
- [x] Browse + Market pages with live API data
- [x] Smart autocomplete (20+ brands)
- [x] Toast notifications
- [x] All typeable inputs (no dropdowns)
- [x] Premium fonts + gold-gradient branding
- [x] Deal analysis with alternatives
- [x] README documentation

---

## 14. Incomplete Features

### Critical Gaps
- [ ] **Admin endpoints lack authentication** — `/v1/admin/*` has no auth guard
- [ ] **No Terraform/IaC** — Blueprint specifies Terraform for AWS, not implemented
- [ ] **No production deployment** — Only Docker Compose for local dev
- [ ] **No WAF** — Referenced in blueprint security architecture
- [ ] **No load testing** — Blueprint target: 100 req/min sustained

### Implementation Gaps
- [ ] **Scraper completeness** — Most scrapers are structural stubs; actual extraction logic varies
- [ ] **Feature engineering thin** — Feature modules referenced but implementation is skeletal
- [ ] **SHAP explainability** — Referenced in schema but not wired into valuation response
- [ ] **Knowledge base enrichment** — Not queried during valuation (Knowledge() returns empty defaults)
- [ ] **Delisting detection** — Probabilistic model defined but not executed (no cron/scheduler)
- [ ] **Cross-source dedup** — `canonical_vehicles` table exists but no matching logic
- [ ] **Materialized views** — Blueprint specifies segment_stats + market_trends views, not created
- [ ] **Currency exchange rate fetching** — Uses hardcoded rates, no API integration
- [ ] **Partitioning** — `listing_snapshots` defined with PARTITION BY RANGE but partition creation not automated

### Missing From Blueprint
- [ ] **Sentry error tracking** — Referenced but not configured
- [ ] **Grafana dashboards** — 4 dashboards specified, not implemented
- [ ] **OpenTelemetry tracing** — `otel_enabled` flag exists but no instrumentation
- [ ] **Alerting** — 8 alert rules defined, no alertmanager/pager integration
- [ ] **Synthetic monitoring** — External health check not configured
- [ ] **Penetration test** — Blueprint milestone, not performed
- [ ] **API documentation** — FastAPI auto-generates OpenAPI, but no Data Dictionary or Runbooks exist
- [ ] **JATO import** — Blueprint Phase 3 deliverable for spec data
- [ ] **Partsouq scraper** — Blueprint Phase 3 deliverable for parts pricing
- [ ] **Mobile app** — Blueprint Phase 4, not started

---

## 15. Technical Debt

### Code Quality
| Issue | Severity | Location | Detail |
|-------|----------|----------|--------|
| Hardcoded JWT secret default | **High** | `src/config.py` | `jwt_secret` defaults to a literal string "dev-secret-change-in-production..." |
| No admin auth | **High** | `src/api/routes/admin.py` | Admin endpoints have no authentication guard |
| Hardcoded exchange rates | **Medium** | `src/pipeline/normalizer.py` | `EXCHANGE_RATES_TO_AED` is a static dict |
| Knowledge base not wired | **Medium** | `src/api/routes/valuation.py` | `Knowledge()` returns empty defaults in valuation response |
| Stub scraper implementations | **Medium** | 9 scraper files | Most scrapers have structural stubs, extraction logic varies |
| UI as single HTML file | **Medium** | `ui/index.html` | 421-line monolithic file with inline CSS+JS |
| Scripts directory cruft | **Medium** | `scripts/` | 24 scripts, many are one-off build helpers with duplicate functionality |
| Coverage gaps | **Low** | `observability/`, `orchestrator.py`, `promoter.py` | 0% test coverage on these modules |
| Debug artifacts committed | **Low** | `haraj_debug2.txt` | Debug file in repo root |
| Preview HTML files in ui/ | **Low** | `ui/previews/` | 3 UI mockups — not production code but in repo |

### Architectural Concerns
| Issue | Detail |
|-------|--------|
| **Linear branch chain never merged** | 4 branches ahead of master, each building on the previous. Merge/consolidation needed before continuing. |
| **No environment segregation** | Single `Settings` class, no dev/staging/prod config files. All env-specific config via env vars only. |
| **Sync config needed for Alembic** | `database_url_sync` duplicates `database_url` in sync form — manual maintenance required. |
| **Rate limiter in-memory** | slowapi uses in-memory counters. Won't work across multiple API instances without Redis. |
| **ML model serialized with pickle** | `trainer.py` uses pickle for model serialization — not portable across Python versions. |
| **No database migration testing** | Single migration file, no downgrade tested, no migration CI check. |

---

## 16. Known Risks

### Production Risks
| # | Risk | Likelihood | Impact | Current Mitigation |
|---|------|-----------|--------|-------------------|
| 1 | Source blocks scraping | Medium | High | 10 diverse sources, URL paste fallback, site-specific error messages |
| 2 | Dubizzle anti-bot protection | High | Medium | Detected + user-friendly error, manual form fallback |
| 3 | No transaction ground truth | Medium | Medium | Statistical model works without ML, confidence scores set expectations |
| 4 | JWT secret unchanged in prod | Medium | Critical | No validation — relies on operator remembering to change it |
| 5 | Admin endpoints exposed | High | Medium | No auth guard — any user can access stats/scraper/quality data |
| 6 | Single DB instance | Medium | Medium | Docker Compose single db. No multi-AZ, no read replicas. |
| 7 | Model staleness | Medium | Medium | Weekly retraining designed but no scheduler configured |
| 8 | Stale exchange rates | Medium | Low | Hardcoded — GCC pegged currencies stable, but KWD/OMR/BHD float |
| 9 | Low comp count for rare cars | High | Medium | Tiered comp finder relaxes constraints, returns "insufficient" gracefully |
| 10 | Parser breaks on site redesign | Medium | High | HTML preserved in S3 → can fix parser and re-process |

### Operational Risks
| # | Risk | Detail |
|---|------|--------|
| 11 | No automated backups | DB backup not configured in docker-compose |
| 12 | No deployment pipeline | CI tests but no CD — manual deployment |
| 13 | No alerting wired up | Drift/scraper health tracked but no notifications |
| 14 | No secret rotation | JWT secret, API keys — no rotation mechanism |
| 15 | Single point of failure | One API instance, one DB — no HA |

---

## 17. Test Suite Summary

### 60 Tests, All Passing

| Test File | Tests | Focus |
|-----------|-------|-------|
| `test_models.py` | Multiple | Model instantiation, relationships |
| `test_integration.py` | Multiple | API endpoint integration |
| `test_auth.py` | Multiple | JWT create/verify, API key hash/verify |
| `test_knowledge.py` | Multiple | Knowledge base seeding |
| `test_phase4.py` | Multiple | LLM explainer, VIN decoder, recommendations |
| `pipeline/test_validator.py` | Multiple | Pandera validation rules |
| `pipeline/test_normalizer.py` | Multiple | Make/spec/city/currency normalization |
| `pipeline/test_quality.py` | Multiple | Quality scoring logic |
| `engine/test_statistical.py` | Multiple | Valuation computation |
| `engine/test_comp_finder.py` | Multiple | Comp finding + scoring |
| `scrapers/test_base.py` | Multiple | Scraper base class |

### Coverage Gaps
- **0%:** `observability/`, `pipeline/orchestrator.py`, `pipeline/promoter.py`
- **<50%:** Most scraper implementations, `pipeline/quality.py` (78%), `scrapers/base.py` (41%)
- **Untested:** Alembic migrations, Docker setup, UI JavaScript, CI pipeline

---

## 18. Recommendations

### Immediate (Before Production)
1. **Add auth to admin endpoints** — `GET /v1/admin/*` needs JWT or API key authentication
2. **Validate JWT secret in production** — Add startup check that `jwt_secret` != default
3. **Merge branch chain to master** — Consolidate `phase-2` → `phase-3` → `phase-4` → `feature-url-valuation` into master
4. **Set up automated DB backups** — At minimum, pg_dump cron in docker-compose

### Short-Term (Next 2 Weeks)
5. **Wire knowledge base into valuation** — Query `car_specs`/`car_issues`/`maintenance_costs` during `POST /valuate`
6. **Implement exchange rate API** — Replace hardcoded rates with exchangerate-api.com or similar
7. **Clean up scripts/** — Remove one-off build scripts, keep only operational scripts
8. **Complete scraper stubs** — Audit each scraper for extraction completeness
9. **Add CI migration check** — Test `alembic upgrade head` + `alembic downgrade -1` in CI

### Medium-Term (Next Month)
10. **Implement Terraform for AWS** — Per blueprint Phase 3
11. **Set up Sentry** — Error tracking for production
12. **Configure Grafana dashboards** — 4 dashboards per blueprint Section 11.3
13. **Implement alerting** — Wire up scraper health, model drift, API error rate alerts
14. **Add OpenTelemetry tracing** — Enable `otel_enabled` with real instrumentation

### Long-Term (Phase 4+)
15. **Mobile app** (React Native, sharing API)
16. **VIN API integration** (JATO or NHTSA for full decode)
17. **Image-based extraction** (OCR from listing photos)
18. **EV battery health estimation**
19. **Enterprise API tier** with SLAs and contracts

---

*Audit completed 2026-07-12. No production code was modified during this audit.*
