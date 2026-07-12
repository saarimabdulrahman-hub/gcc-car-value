# GCC Car Value Platform — Technical Debt Register

**Date:** 2026-07-12  
**Sources:** `docs/project-audit.md`, `docs/master-plan-validation.md`, `docs/database-audit.md`, `docs/api-audit.md`, `docs/observability-audit.md`, `docs/ml-audit.md`

---

## Summary

| Severity | Count | Definition |
|----------|-------|------------|
| 🔴 Critical | 8 | Production blocker — must fix before deployment |
| 🟠 High | 14 | Functional gap or security risk — fix before public launch |
| 🟡 Medium | 24 | Quality/coverage issue — fix within first month of launch |
| 🟢 Low | 16 | Cleanup/optimization — fix when convenient |
| ⚪ Future | 12 | Enhancement — roadmap items |

**Total: 74 items**

---

## 🔴 Critical (8 items)

### C-01: No production infrastructure (Terraform/AWS)
- **Source:** `master-plan-validation.md` §3, `project-audit.md` §11
- **Description:** The blueprint specifies Terraform for AWS (ECS Fargate, RDS, S3, CloudFront, Secrets Manager). Only Docker Compose exists for local dev. The platform cannot be deployed to production.
- **Business Impact:** Cannot launch. Zero path to production.
- **Engineering Effort:** Large (~2-3 weeks)
- **Dependencies:** AWS account, domain, SSL certs
- **Recommended Prompt:** `Implement Terraform for AWS infrastructure per blueprint §12 — ECS Fargate (API + Scraper), RDS PostgreSQL t3.medium, S3 raw data bucket with lifecycle policy, CloudFront CDN, Secrets Manager. Create dev + staging + prod workspaces.`

### C-02: Listing snapshots partition auto-creation missing
- **Source:** `database-audit.md` §6
- **Description:** `listing_snapshots` is partitioned by month. Only July and August 2026 partitions exist. INSERTs after August 2026 will fail with "no partition of relation." No pg_partman, no cron, no application-level partition manager.
- **Business Impact:** Data pipeline breaks in September 2026. Price history lost. Snapshots can't be recorded.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** None
- **Recommended Prompt:** `Add automatic monthly partition creation for listing_snapshots. Create partitions 3 months ahead. Add to scraper pipeline startup or as a cron/scheduler job. Use CREATE TABLE IF NOT EXISTS ... PARTITION OF listing_snapshots FOR VALUES FROM ... TO ...`

### C-03: Trained ML model discarded on training
- **Source:** `ml-audit.md` §3.5
- **Description:** `trainer.py` saves the trained LightGBM model via `pickle.dump()` to a `tempfile.NamedTemporaryFile`. The OS cleans up temp files. Models are never uploaded to S3 or MLflow. The `model_path` in the registry points to a path that won't exist.
- **Business Impact:** All ML training compute is wasted. No model can be loaded for inference or shadow deployment.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** S3 bucket or MLflow artifact store
- **Recommended Prompt:** `Fix model persistence in engine/trainer.py — upload trained pickle to S3 (or MLflow artifact store), store the S3 key/MLflow run ID in model_registry.model_path. Add a load_model() function that retrieves from S3/MLflow. Remove tempfile usage.`

### C-04: Admin endpoints have no authentication
- **Source:** `api-audit.md` §7
- **Description:** `GET /v1/admin/stats`, `/v1/admin/scrapers`, `/v1/admin/quality` return operational data (listing counts, scraper health, quality metrics) with zero authentication. Anyone can access.
- **Business Impact:** Operational data exposed. Scraper health, listing volumes, pipeline status visible to competitors or attackers.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** JWT auth already implemented in `auth/jwt.py`
- **Recommended Prompt:** `Add JWT authentication guard to all /v1/admin/* endpoints. Create an admin_required dependency that verifies the JWT token and checks for admin tier. Apply via Depends() on all admin routes.`

### C-05: JWT secret has hardcoded default
- **Source:** `project-audit.md` §9
- **Description:** `config.py` defaults `jwt_secret` to `"dev-secret-change-in-production-gcc-car-value-2026"`. No startup validation ensures it's been changed. If deployed with default, all JWTs are forgeable.
- **Business Impact:** Critical security vulnerability — anyone can mint valid admin tokens.
- **Engineering Effort:** Trivial (~15 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Add startup validation in config.py or main.py that refuses to start if jwt_secret equals the hardcoded default and environment != "development". Raise RuntimeError with clear message.`

### C-06: No UNIQUE constraint on listings (source, external_id)
- **Source:** `database-audit.md` §4.1, §9.2
- **Description:** Blueprint specifies `UNIQUE(source, external_id)`. Not enforced. Promoter uses SELECT-then-UPSERT — a race condition between two concurrent scraper runs creates duplicate rows for the same listing.
- **Business Impact:** Duplicate listings inflate comp counts and skew valuations. Silent data corruption.
- **Engineering Effort:** Small (~1 hour) — requires migration
- **Dependencies:** None (Alembic migration)
- **Recommended Prompt:** `Create an Alembic migration adding UNIQUE constraint on listings(source, external_id). Before adding, run a dedup query to remove existing duplicates. Then refactor promoter.py to use INSERT ... ON CONFLICT DO UPDATE instead of SELECT-then-UPSERT.`

### C-07: Prometheus metrics endpoint not registered
- **Source:** `observability-audit.md` §3.3
- **Description:** `metrics_endpoint()` exists in `observability/metrics.py` but is never registered in `main.py`. The `/metrics` endpoint is unreachable. All 5 Prometheus metrics are defined but never incremented anywhere in the codebase.
- **Business Impact:** Zero operational visibility. Can't monitor API traffic, valuation volume, scraper health, or latency.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** None
- **Recommended Prompt:** `Register /metrics endpoint in main.py. Add .inc()/.observe()/.set() calls to increment existing Prometheus metrics: valuation_requests in valuation.py, scraper_runs and scraper_listings_ingested in orchestrator.py, data_freshness_hours after scraper runs. Add a Prometheus service to docker-compose.yml.`

### C-08: 0 of 8 blueprint alert rules operational
- **Source:** `observability-audit.md` §9
- **Description:** Blueprint §11.4 specifies 8 alert rules (scraper failure, API error rate, data freshness, model degradation, drift, DB disk, dead letter growth, API latency). None are implemented. No Alertmanager, no webhook, no email integration.
- **Business Impact:** Production issues will go undetected. Scraper failures could mean days of stale data before anyone notices.
- **Engineering Effort:** Medium (~1 week)
- **Dependencies:** C-07 (metrics must be emitted first)
- **Recommended Prompt:** `Implement the 8 alert rules from blueprint §11.4. Add Prometheus Alertmanager to docker-compose. Create alert rules file with thresholds. Wire Slack webhook for critical alerts (scraper failure, API error rate >5%). Create alert rules config at infra/prometheus/alerts.yml.`

---

## 🟠 High (14 items)

### H-01: Knowledge base not wired into valuation responses
- **Source:** `api-audit.md` §3.3, `project-audit.md` §14
- **Description:** `POST /v1/valuate` always returns `Knowledge()` with all defaults (`generation: null`, `known_issues: []`, `annual_maintenance_estimate: null`). The `car_specs`, `car_issues`, `maintenance_costs`, `depreciation_curves`, and `model_ratings` tables are seeded with 32 models but never queried during valuation.
- **Business Impact:** Core differentiator missing. Competitors show specs, issues, and maintenance costs. Users get no ownership insight.
- **Engineering Effort:** Medium (~1 day)
- **Dependencies:** None (knowledge base tables already seeded)
- **Recommended Prompt:** `Query car_specs, car_issues, maintenance_costs, and depreciation_curves during POST /v1/valuate. Match by make+model+generation (generation inferred from year range). Populate the Knowledge schema with generation name, top 3 known issues, annual maintenance estimate string, and market liquidity. Add to both fresh and cached responses.`

### H-02: Cache hit response degraded
- **Source:** `api-audit.md` §3.3
- **Description:** Cached valuation responses return empty `comps: []`, `adjustments: []`, `confidence_interval_80: null`, `deal_indicator: null`. Only the estimate/price_low/price_high/confidence/comp_count survive the cache. Users refreshing the same car get a different response shape.
- **Business Impact:** Degraded UX for repeat queries. Missing comps and deal indicators on cached responses.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** None
- **Recommended Prompt:** `Store full ValuationResponse in valuation_queries cache (serialize comps, adjustments, knowledge, deal_indicator as JSONB columns). On cache hit, deserialize and return the complete response. Add a cache_hit: true field to the response so the UI knows it's cached.`

### H-03: Missing /v1/trends endpoint
- **Source:** `master-plan-validation.md` §1 (Phase 1), `api-audit.md` §6
- **Description:** Blueprint specifies `GET /v1/trends` for market trends with segment query params. Not implemented. Market data only available via `/v1/admin/stats` (total counts only) and `/v1/models` (per-model counts).
- **Business Impact:** Market trends page in UI has no data source for price trends, segment analysis, or time-series charts.
- **Engineering Effort:** Medium (~1 day)
- **Dependencies:** None (data available in listings + snapshots)
- **Recommended Prompt:** `Implement GET /v1/trends with query params: make, model, year_min, year_max, country. Return: weekly median price over past 12 weeks (from listing_snapshots), listing volume trend, average days on market, price volatility. Use listing_snapshots for price history, listings for current stats.`

### H-04: Missing /v1/valuate/{id} endpoint
- **Source:** `master-plan-validation.md` §1 (Phase 1), `api-audit.md` §6
- **Description:** Blueprint specifies `GET /v1/valuate/{id}` to retrieve a cached valuation by ID. Not implemented. Users can't bookmark or share valuations.
- **Business Impact:** No shareable valuation links. Poor UX for "send this valuation to a friend."
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** H-02 (need full cache response first)
- **Recommended Prompt:** `Implement GET /v1/valuate/{id} — look up valuation_queries by primary key id, return full ValuationResponse. If not found, return 404. Do not recompute — only return cached.`

### H-05: Audit logging middleware not implemented
- **Source:** `api-audit.md` §6, `master-plan-validation.md` §1 (Phase 1)
- **Description:** Blueprint §10.6 specifies middleware that logs every API request: timestamp, method, path, status_code, response_ms, ip_hash, user_id, api_key_hash, user_agent, request_body_hash. Not implemented at all.
- **Business Impact:** No audit trail. Can't investigate abuse, debug issues, or provide enterprise customers with usage reports.
- **Engineering Effort:** Medium (~1 day)
- **Dependencies:** PostgreSQL table for audit logs
- **Recommended Prompt:** `Create audit logging middleware per blueprint §10.6. Log every API request with: timestamp, method, path, status_code, response_ms, ip_hash (SHA-256 of remote IP), user_id (if authenticated), user_agent. Store in a new audit_logs table partitioned by month with 90-day retention. Use structlog for structured log emission.`

### H-06: Exchange rates hardcoded
- **Source:** `project-audit.md` §15
- **Description:** `pipeline/normalizer.py` has a static `EXCHANGE_RATES_TO_AED` dict. KWD, OMR, BHD are not pegged to USD and float. Hardcoded rates will drift from reality.
- **Business Impact:** Cross-currency valuations (Kuwait, Oman, Bahrain listings) become inaccurate over time. KWD at 11.94 vs actual could shift by 1-2%.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** Free exchange rate API key (exchangerate-api.com)
- **Recommended Prompt:** `Replace hardcoded EXCHANGE_RATES_TO_AED dict with a fetch from exchangerate-api.com (free tier) at pipeline start. Cache rates for the run duration. Store the fetched exchange_timestamp with each listing. Add fallback to hardcoded rates if API is unavailable.`

### H-07: Scraper implementations are structural stubs
- **Source:** `project-audit.md` §3.6, `master-plan-validation.md` §5
- **Description:** 9 of 10 scrapers have `parse()` methods that are structural stubs. Extraction logic varies in completeness. Only Dubizzle UAE has a dedicated parser module. The scrapers will not extract real data from their target sites without additional implementation.
- **Business Impact:** Data pipeline produces no data from most sources. Valuation engine has sparse comp coverage.
- **Engineering Effort:** Large (~2-3 weeks, one scraper at a time)
- **Dependencies:** Access to test listing pages from each source
- **Recommended Prompt:** `Complete scraper implementations one source at a time. For each: fetch real listing pages, identify CSS selectors for make/model/year/price/mileage/spec/city, implement parse(), test with 10+ sample pages, verify extraction rates >80%. Priority order: YallaMotor, Haraj KSA, CarSwitch, Emirates Auction, OpenSooq.`

### H-08: Health check returns 200 on database failure
- **Source:** `observability-audit.md` §4.2
- **Description:** `GET /v1/health` catches all exceptions from `SELECT 1` and returns `200 OK` with `{"status": "degraded"}`. Load balancers and orchestrators won't detect this as unhealthy and won't fail over.
- **Business Impact:** Load balancer won't route traffic away from a failing instance. Kubernetes won't restart an unhealthy pod.
- **Engineering Effort:** Trivial (~5 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Change /v1/health to return HTTP 503 when database is unhealthy. Keep 200 for healthy responses. Add optional query param ?deep=true that also checks S3 connectivity and MLflow.`

### H-09: SSRF risk in URL valuation endpoint
- **Source:** `api-audit.md` §7
- **Description:** `POST /v1/valuate-url` fetches arbitrary URLs via httpx. No URL validation, no IP allowlisting, no internal network blocking. Could be used to probe internal services.
- **Business Impact:** SSRF vulnerability — attacker could probe internal AWS metadata service, internal APIs, or localhost services.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** None
- **Recommended Prompt:** `Add URL validation to /v1/valuate-url: block private IPs (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x), block non-HTTP(S) schemes, enforce max URL length (2048 chars), resolve DNS and validate the IP is public before fetching. Add request timeout (15s max).`

### H-10: Rate limiting only on one endpoint
- **Source:** `api-audit.md` §4.2
- **Description:** Only `POST /v1/valuate` has rate limiting (10/min). URL valuation, model listing, and admin endpoints are unlimited. In-memory slowapi counters won't work across multiple API instances.
- **Business Impact:** URL valuation endpoint can be abused to fetch arbitrary URLs at server expense. Admin endpoints can be scraped. Multi-instance deployment breaks rate limiting entirely.
- **Engineering Effort:** Medium (~2 days)
- **Dependencies:** Redis (for multi-instance rate limiting)
- **Recommended Prompt:** `Add rate limiting to /v1/valuate-url (10/min), /v1/models/* (60/min), /v1/admin/* (30/min, authenticated only). For multi-instance support, evaluate slowapi with Redis backend or replace with a Redis-backed token bucket.`

### H-11: Drift detection never scheduled
- **Source:** `ml-audit.md` §9, `observability-audit.md` §6
- **Description:** `engine/drift.py` has complete PSI-based drift detection for 4 drift types. Never called by any scheduler, cron, or API. Drift events are logged to `drift_events` table but only if someone manually calls the functions.
- **Business Impact:** Model performance degradation goes undetected. Feature distribution shifts from site redesigns are invisible. Silent model staleness.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** C-02 (partitions needed for snapshot data to accumulate)
- **Recommended Prompt:** `Add APScheduler job to run drift detection weekly after scraper pipeline completes. Compute PSI for each feature vs 4-week baseline, check target drift, prediction drift, and market drift. Store results in drift_events. Log warnings on threshold exceeded.`

### H-12: ML model never used in API
- **Source:** `ml-audit.md` §3.6, §8
- **Description:** The API exclusively calls `engine.statistical.valuate()`. The LightGBM training pipeline, 15 features, FeatureRegistry, and model_registry are fully coded but completely disconnected from the inference path. The API hardcodes `model_type="statistical"`.
- **Business Impact:** All ML investment yields zero production value. Statistical model doesn't improve over time.
- **Engineering Effort:** Medium (~3 days)
- **Dependencies:** C-03 (model must be persisted), H-11 (drift detection must run), model must be trained and activated
- **Recommended Prompt:** `Wire the LightGBM model into the valuation inference path. After statistical valuation, if an active model exists in model_registry (status='active'), build a MarketContext from DB, compute features via FeatureRegistry, predict with the loaded model, cross-reference with statistical estimate. If ML and statistical disagree by >15%, default to statistical with a warning flag. Store model_type and model_version in the response.`

### H-13: Invalid Claude model string
- **Source:** `ml-audit.md` §10.1
- **Description:** `engine/llm_explainer.py` uses model ID `"claude-sonnet-4-6"` which is not a valid Anthropic model identifier. All Claude API calls will fail with a 404 or invalid model error.
- **Business Impact:** LLM explanation feature broken. Never produces Claude-generated explanations, always falls back to template.
- **Engineering Effort:** Trivial (~5 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Fix the model string in engine/llm_explainer.py from "claude-sonnet-4-6" to a valid Anthropic model ID. Use the latest Claude model available. Make the model string configurable via settings (e.g., claude_model).`

### H-14: SHAP explainability not implemented
- **Source:** `ml-audit.md` §7, `master-plan-validation.md` §1 (Phase 2)
- **Description:** SHAP is not in `pyproject.toml` dependencies. No SHAP computation code exists. `valuation_queries.shap_values` and `feature_importance` columns are never populated. Blueprint §6.1 specifies "SHAP values for top 5 features" per valuation.
- **Business Impact:** ML valuations lack feature-level explainability. Users can't see why the model produced a specific price. Regulatory/compliance risk.
- **Engineering Effort:** Medium (~2 days)
- **Dependencies:** H-12 (ML model must be used in API first)
- **Recommended Prompt:** `Install shap package. After LightGBM prediction in the valuation pipeline, compute SHAP values using shap.TreeExplainer. Store top 5 feature contributions in valuation_queries.shap_values. Add to ValuationResponse. Display in UI as "What affects this price" section.`

---

## 🟡 Medium (24 items)

### M-01: structlog coverage at 27%
- **Source:** `observability-audit.md` §2.2
- **Description:** Only 8 of 30+ modules use structlog. Scrapers, pipeline stages (validator, normalizer, quality, promoter), comp finder, statistical engine, features, and auth modules have zero logging.
- **Business Impact:** Can't debug scraper failures, pipeline decisions, or valuation computations from logs.
- **Engineering Effort:** Small (~3 hours) — add logger = structlog.get_logger() + key log calls to each module
- **Dependencies:** None
- **Recommended Prompt:** `Add structlog to all modules without logging: scraper base, all 9 scraper implementations, pipeline validator/normalizer/quality/promoter, comp finder, statistical engine, feature modules, auth/jwt.py. Log key events: scraper page fetch, parse completion, validation pass/fail, quality score, promotion decision, comp count, valuation result.`

### M-02: No trace_id in logs
- **Source:** `observability-audit.md` §2.3
- **Description:** Blueprint §11.2 specifies `trace_id` correlation in every log line. No request ID middleware exists. Logs from the same request can't be correlated.
- **Business Impact:** Can't trace a valuation request through cache check → comp finder → statistical engine → cache write.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** None
- **Recommended Prompt:** `Create a FastAPI middleware that generates a UUID trace_id per request, injects it into structlog context via structlog.contextvars.bind_contextvars(trace_id=...), and adds X-Trace-Id response header.`

### M-03: No Sentry error tracking
- **Source:** `observability-audit.md` §8
- **Description:** Blueprint specifies Sentry for exception tracking. Not installed, not configured. API exceptions are caught and returned as 422 — unhandled exceptions produce unstructured 500s with no aggregation.
- **Business Impact:** Production errors invisible. No error grouping, no stack traces, no frequency tracking.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** Sentry account (free tier sufficient)
- **Recommended Prompt:** `Install sentry-sdk, add sentry_sdk.init() to main.py with environment and traces_sample_rate config. Add SENTRY_DSN to Settings. The FastAPI integration auto-captures unhandled exceptions. Test by hitting an endpoint that raises.`

### M-04: No OpenTelemetry tracing
- **Source:** `observability-audit.md` §7
- **Description:** `otel_enabled` flag exists in config but no OpenTelemetry SDK is installed or configured. No spans for API requests, DB queries, or external HTTP calls.
- **Business Impact:** Can't trace request latency through the stack. Can't identify bottlenecks in valuation pipeline.
- **Engineering Effort:** Medium (~2 days)
- **Dependencies:** None (can add Jaeger to docker-compose)
- **Recommended Prompt:** `Install opentelemetry packages. Add auto-instrumentation for FastAPI, SQLAlchemy, and httpx. Configure OTLP exporter to Jaeger (add to docker-compose). Gate behind otel_enabled flag. Add manual spans for valuation computation and external URL fetch.`

### M-05: No Grafana dashboards
- **Source:** `observability-audit.md` §10
- **Description:** Blueprint §11.3 specifies 4 Grafana dashboards (Platform Health, Data Quality, Model Performance, Business Metrics). None exist. No Grafana in docker-compose.
- **Business Impact:** No visual monitoring. Engineers have no dashboard to check platform health.
- **Engineering Effort:** Medium (~3 days)
- **Dependencies:** C-07 (metrics must be emitted), Prometheus in docker-compose
- **Recommended Prompt:** `Add Grafana to docker-compose. Create 4 dashboards per blueprint §11.3. Platform Health: API req/min, p50/p95/p99 latency, error rate. Data Quality: quality score histogram, rejection rate, field extraction %. Model Performance: MAE over time, shadow comparison. Business Metrics: valuations/day, top makes/models, cache hit rate. Export as JSON to infra/grafana/dashboards/.`

### M-06: Add missing Prometheus metrics (13 recommended)
- **Source:** `observability-audit.md` §3.4
- **Description:** Only 5 metrics defined, 0 used. 13 recommended metrics are missing: api_requests_total, api_request_duration_seconds, db_query_duration_seconds, db_pool_size, scraper_errors_total, scraper_duration_seconds, pipeline_records_total, pipeline_quality_score, valuation_cache_hits_total, valuation_insufficient_comps_total, model_prediction_mae, drift_psi, external_http_errors_total.
- **Business Impact:** Incomplete operational visibility.
- **Engineering Effort:** Medium (~2 days)
- **Dependencies:** C-07
- **Recommended Prompt:** `Add the 13 recommended Prometheus metrics from docs/observability-audit.md §3.4. Wire increment/observe calls at the appropriate points in the codebase.`

### M-07: Add 12 missing database indexes
- **Source:** `database-audit.md` §3.2
- **Description:** 12 recommended indexes are missing: listings(normalized_price_aed), listings(last_seen_at), listings(mileage_km), canonical_vehicles(make,model,year), valuation_queries(user_id), saved_valuations(user_id), price_alerts(user_id,active), car_specs(make,model), car_issues(make,model), pipeline_runs(source), dead_letter(pipeline_run_id), scraper_health(source,captured_at).
- **Business Impact:** Comp finder queries sort on last_seen_at without index — performance degrades as listings grow. Admin scrapers query groups by source without index. Knowledge base lookups full-scan.
- **Engineering Effort:** Small (~2 hours) — Alembic migration
- **Dependencies:** None
- **Recommended Prompt:** `Create an Alembic migration adding the 12 missing indexes from docs/database-audit.md §3.2. Prioritize: idx_listings_last_seen_at, idx_listings_mileage_km, idx_canonical_vehicles_make_model_year, idx_scraper_health_source_date, idx_car_specs_make_model, idx_car_issues_make_model.`

### M-08: Add FK constraints on dead_letter and scraper_health
- **Source:** `database-audit.md` §4.2
- **Description:** `dead_letter.pipeline_run_id` and `scraper_health.pipeline_run_id` reference `pipeline_runs.run_id` but have no FK constraint. Orphaned rows possible if pipeline runs are deleted.
- **Business Impact:** Referential integrity not guaranteed. Debugging difficulty when pipeline_run_id points to non-existent run.
- **Engineering Effort:** Small (~30 minutes) — Alembic migration
- **Dependencies:** Ensure no orphaned rows exist before adding constraint
- **Recommended Prompt:** `Create an Alembic migration adding FK constraints: dead_letter.pipeline_run_id → pipeline_runs.run_id, scraper_health.pipeline_run_id → pipeline_runs.run_id. First check for and clean up any orphaned rows.`

### M-09: Add CHECK constraints on model_ratings
- **Source:** `database-audit.md` §4.3
- **Description:** Blueprint DDL specifies `CHECK (rating BETWEEN 1 AND 5)` on all 7 rating columns in `model_ratings`. Not created. Invalid ratings (e.g., 0 or 6) can be inserted.
- **Business Impact:** Data integrity risk. Bad ratings could skew recommendation engine scores.
- **Engineering Effort:** Trivial (~15 minutes) — Alembic migration
- **Dependencies:** Clean existing data first
- **Recommended Prompt:** `Create an Alembic migration adding CHECK constraints on model_ratings: reliability BETWEEN 1 AND 5, comfort BETWEEN 1 AND 5, performance BETWEEN 1 AND 5, fuel_economy BETWEEN 1 AND 5, offroad_capability BETWEEN 1 AND 5, resale_value BETWEEN 1 AND 5, overall BETWEEN 1 AND 5.`

### M-10: Add UNIQUE on canonical_vehicles (make, model, year, generation)
- **Source:** `database-audit.md` §4.1
- **Description:** Blueprint specifies `UNIQUE(make, model, year, COALESCE(generation, ''))` on `canonical_vehicles`. Not enforced. Cross-source dedup can create duplicate canonical entries.
- **Business Impact:** Same vehicle represented by multiple canonical IDs — market stats inflated.
- **Engineering Effort:** Small (~1 hour) — Alembic migration + dedup
- **Dependencies:** Clean existing duplicates first
- **Recommended Prompt:** `Create an Alembic migration adding UNIQUE constraint on canonical_vehicles(make, model, year, COALESCE(generation, '')). Before migration, run dedup to merge duplicate canonical vehicles and update referencing listing.canonical_vehicle_id FK.`

### M-11: Create materialized views for segment stats
- **Source:** `database-audit.md` §7, `master-plan-validation.md` §1 (Phase 1)
- **Description:** Blueprint post-scrape jobs specify `segment_stats` (median price, count, avg days to sell per segment) and `market_trends` (WoW price change per segment) materialized views. Not created.
- **Business Impact:** `/v1/admin/stats` runs 6 sequential COUNT queries per request. Segment analysis requires ad-hoc aggregation queries.
- **Engineering Effort:** Small (~2 hours) — SQL + migration
- **Dependencies:** C-02 (snapshots partition must work)
- **Recommended Prompt:** `Create materialized views per blueprint: segment_stats (make, model, year_range, country, median_price, listing_count, avg_days_to_sell) and market_trends (segment, week, median_price, listing_count, price_change_wow). Add REFRESH MATERIALIZED VIEW to post-scrape pipeline. Use for /v1/trends endpoint.`

### M-12: Create listings_staging table
- **Source:** `database-audit.md` §7, `master-plan-validation.md` §5
- **Description:** Blueprint §4.3 specifies a `listings_staging` table for preprocessing isolation before promotion to production `listings`. Pipeline writes directly to `listings` — no isolation between raw ingestion and production data.
- **Business Impact:** Bad data enters production before quality checks complete. No staging→production promotion boundary.
- **Engineering Effort:** Small (~2 hours) — table + migration + promoter refactor
- **Dependencies:** None
- **Recommended Prompt:** `Create listings_staging table per blueprint §4.3 (LIKE listings INCLUDING DEFAULTS, plus staging_id PK, validation_errors JSONB, promoted BOOLEAN). Refactor pipeline: scrapers → staging, then validate → normalize → score → promote (staging → listings). Truncate staging after successful promotion.`

### M-13: Remove or populate dead columns on listings
- **Source:** `database-audit.md` §10
- **Description:** `listings` has 10 columns never populated by any scraper: `doors`, `cylinders`, `engine_size`, `warranty`, `service_history`, `price_history`. These columns are always NULL/default.
- **Business Impact:** Schema bloat. Two features (HasWarrantyFeature, HasServiceHistoryFeature) always evaluate to 0.0 because columns are never populated.
- **Engineering Effort:** Small (~2 hours) — either add extraction to scrapers or create migration to drop
- **Dependencies:** None
- **Recommended Prompt:** `Audit all scraper parse() methods. For columns that can be extracted (engine_size from spec text, warranty from listing description), add extraction logic. For columns that cannot be reliably extracted (doors, cylinders), create an Alembic migration to drop them. Populate price_history JSONB array on price changes during promoter update.`

### M-14: Fix listing_snapshots migration type inconsistency
- **Source:** `database-audit.md` §5.2
- **Description:** `listing_snapshots` model uses `UniversalUUID` but the migration DDL uses `postgresql.UUID` directly. Works on PostgreSQL but breaks the cross-dialect compatibility pattern. Table can't be auto-created by `Base.metadata.create_all()`.
- **Business Impact:** Can't use SQLite for testing of snapshot-related code. Migration bypasses the type decorator system.
- **Engineering Effort:** Small (~1 hour) — new migration to alter column types
- **Dependencies:** None
- **Recommended Prompt:** `Create an Alembic migration to alter listing_snapshots columns from postgresql.UUID to the same type used by UniversalUUID. Update the initial migration's create_table to use UniversalUUID's PG type consistently. Or document this as intentional and add a comment explaining the deviation.`

### M-15: Fix cache key collision window
- **Source:** `api-audit.md` §3.3
- **Description:** Cache key uses current date (`YYYY-MM-DD`), which means the same car queried at 23:59 and 00:01 gets different valuations. Better: use the most recent pipeline run date as the cache boundary, not wall clock.
- **Business Impact:** Unnecessary recomputation for queries near midnight. Inconsistent valuations visible to users.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** None
- **Recommended Prompt:** `Change cache key to use the most recent pipeline run date (from pipeline_runs) instead of datetime.now(). This ensures cache TTL is tied to data freshness, not wall clock. Add a data_freshness_warning flag to the response if the most recent pipeline run is >48h old.`

### M-16: Expose avg_price in /v1/models/{make}/{model} response
- **Source:** `api-audit.md` §3.7
- **Description:** The SQL computes `func.avg(Listing.normalized_price_aed)` but the response drops it. Only `year`, `listing_count`, and `trims` are returned.
- **Business Impact:** Frontend can't show average prices in the browse drilldown.
- **Engineering Effort:** Trivial (~10 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Add avg_price to the /v1/models/{make}/{model} response for each year group. Round to nearest integer. The SQL already computes it — just include it in the response dict.`

### M-17: Add URL validation to /v1/valuate-url
- **Source:** `api-audit.md` §3.4
- **Description:** URL parameter has no max length validation. No scheme validation. Could accept non-HTTP URLs that cause httpx to error confusingly.
- **Business Impact:** Poor error messages for malformed URLs. Potential for very long URLs to cause issues.
- **Engineering Effort:** Small (~30 minutes)
- **Dependencies:** H-09 (SSRF fix overlaps)
- **Recommended Prompt:** `Add Pydantic field validation to URLValuationRequest.url: HttpUrl type, max_length=2048. This gives automatic validation and clear error messages for invalid URLs.`

### M-18: Move URLValuationRequest to schemas/
- **Source:** `api-audit.md` §4.5
- **Description:** `URLValuationRequest` is defined inline in `url_valuate.py`. All other request schemas live in `schemas/valuation.py`.
- **Business Impact:** Inconsistent code organization. Not visible in OpenAPI schema grouping.
- **Engineering Effort:** Trivial (~10 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Move URLValuationRequest from routes/url_valuate.py to schemas/valuation.py. Import from schemas in the route file.`

### M-19: UI is a monolithic 421-line HTML file
- **Source:** `project-audit.md` §4
- **Description:** `ui/index.html` contains all CSS, HTML, and JS inline. No component separation. 421 lines and growing. No build step, no linting, no testing.
- **Business Impact:** Hard to maintain. Every change risks breaking unrelated functionality. No JS error tracking.
- **Engineering Effort:** Large (~1-2 weeks) — would need framework migration
- **Dependencies:** Decision on frontend framework (keep vanilla, migrate to React per blueprint, or use a lightweight alternative)
- **Recommended Prompt:** `Evaluate frontend architecture. Options: (A) Extract JS into separate modules with a simple bundler, keep vanilla; (B) Migrate to React as originally specified in blueprint Phase 4. Given the current complexity (5 pages, i18n, autocomplete, charts), option B is recommended. Start with the valuation form page as a proof of concept.`

### M-20: Clean up scripts/ directory (24 files)
- **Source:** `project-audit.md` §15, `master-plan-validation.md` §4
- **Description:** 24 scripts in `scripts/`, most are one-off build helpers (`step1.py`, `step2.py`, `write_final.py`, `fix_both.py`, etc.) with overlapping functionality. Several are UI string-manipulation scripts that are no longer relevant.
- **Business Impact:** Confusion about which scripts are operational vs historical. Risk of running outdated build scripts.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** None
- **Recommended Prompt:** `Clean up scripts/ directory. Keep: seed_all.py, bulk_scrape.py, scrape_yallamotor.py, scrape_prod.py, haraj_gql_scraper.py, dubicars_scraper.py, seed_missing_brands.py. Archive the rest in scripts/archive/ or delete. Add a README.md in scripts/ documenting each operational script.`

### M-21: Consolidate linear branch chain to master
- **Source:** `project-audit.md` §12
- **Description:** 4 branches form a linear chain: `master` → `phase-2-ml-enrichment` → `phase-3-production` → `phase-4-v2-features` → `feature-url-valuation`. Never merged. Working on the wrong branch could lose work.
- **Business Impact:** Confusing branch structure. Risk of committing to an intermediate branch. 72 files ahead of master with no merge strategy.
- **Engineering Effort:** Small (~1 hour) — git merge or rebase
- **Dependencies:** Ensure all tests pass on each branch
- **Recommended Prompt:** `Merge the linear branch chain to master: checkout master, merge phase-2-ml-enrichment, merge phase-3-production, merge phase-4-v2-features, merge feature-url-valuation. Run full test suite after each merge. Push master. Archive merged branches.`

### M-22: Debug artifacts in repository root
- **Source:** `project-audit.md` §15
- **Description:** `haraj_debug2.txt` in repository root. UI preview mockups in `ui/previews/` are not production code.
- **Business Impact:** Minor — repo cleanliness.
- **Engineering Effort:** Trivial (~5 minutes)
- **Dependencies:** None
- **Recommended Prompt:** `Delete haraj_debug2.txt. Move ui/previews/ to docs/design-mockups/ or delete. Add to .gitignore if these are generated files.`

### M-23: No Alembic downgrade tested in CI
- **Source:** `project-audit.md` §17
- **Description:** CI runs `pytest` but never tests `alembic upgrade head` or `alembic downgrade -1`. Migration bugs caught only at deploy time.
- **Business Impact:** A broken migration discovered during deployment causes downtime.
- **Engineering Effort:** Small (~30 minutes)
- **Dependencies:** PostgreSQL service in CI (already exists)
- **Recommended Prompt:** `Add Alembic migration test to CI workflow: run alembic upgrade head, run alembic downgrade -1, run alembic upgrade head again. Fail CI if any step fails. Add a test that verifies the migration revision chain is intact.`

### M-24: Conftest fixtures are dead code
- **Source:** `project-audit.md` §17
- **Description:** `tests/conftest.py` defines `settings` and `db_session` fixtures that are never imported or used by any test. Every test creates its own SQLite engine or uses hardcoded settings.
- **Business Impact:** Confusion for new developers. Fixtures look useful but don't work.
- **Engineering Effort:** Small (~1 hour)
- **Dependencies:** None
- **Recommended Prompt:** `Fix tests/conftest.py: either update tests to use the existing db_session fixture (which points at PostgreSQL) or remove the dead fixtures. If keeping SQLite for tests, add an in-memory SQLite fixture that's actually used. Ensure all tests use the same fixture pattern.`

---

## 🟢 Low (16 items)

### L-01: No data dictionary
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies a data dictionary. Not created.
- **Business Impact:** New developers and data analysts have no reference for table/column meanings.
- **Engineering Effort:** Medium (~3 days to document 18 tables)
- **Recommended Prompt:** `Create docs/data-dictionary.md documenting all 18 tables: table name, description, each column with type, constraints, description, example values. Generate from SQLAlchemy model docstrings.`

### L-02: No scraper runbooks
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies scraper runbooks. Not created.
- **Business Impact:** No operational procedure for handling scraper failures, site redesigns, or adding new sources.
- **Engineering Effort:** Small (~2 hours)
- **Recommended Prompt:** `Create docs/runbooks/scrapers.md: how to run a scraper manually, how to add a new source, how to debug extraction failures, how to update selectors after a site redesign, how to interpret scraper_health metrics.`

### L-03: No deployment runbooks
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies deployment runbooks. Not created.
- **Business Impact:** No documented procedure for deploying to staging or production.
- **Engineering Effort:** Small (~2 hours)
- **Dependencies:** C-01 (Terraform must exist first)
- **Recommended Prompt:** `Create docs/runbooks/deployment.md: how to deploy to staging, how to promote to production, how to roll back, how to run database migrations safely, emergency hotfix procedure.`

### L-04: Missing /v1/stats endpoint (renamed to /v1/admin/stats)
- **Source:** `api-audit.md` §6
- **Description:** Blueprint specifies `GET /v1/stats` as a public endpoint. Implemented as `GET /v1/admin/stats`.
- **Business Impact:** Minor naming deviation from spec.
- **Engineering Effort:** Trivial (~10 minutes)
- **Recommended Prompt:** `Add GET /v1/stats as a public alias that returns the same data as /v1/admin/stats. Keep /v1/admin/stats for backward compatibility.`

### L-05: No pagination on model listing endpoints
- **Source:** `api-audit.md` §3.5-3.7
- **Description:** `/v1/models`, `/{make}`, `/{make}/{model}` return all results with no pagination. As the database grows, these responses could become large.
- **Business Impact:** Large JSON responses for makes with many models (Toyota has 7 models, but could have 30+ in future).
- **Engineering Effort:** Small (~2 hours)
- **Recommended Prompt:** `Add pagination to model listing endpoints: ?limit=50&offset=0. Return total count and a next page URL in the response. Current data volumes don't require it, but it's cheap to add now.`

### L-06: No compression on S3 raw storage
- **Source:** `project-audit.md` §3.6
- **Description:** Blueprint specifies zstd (level 3) compression for S3 raw HTML. `RawStorage.upload_text()` stores uncompressed text/html.
- **Business Impact:** Higher S3 storage costs. Blueprint estimates ~3:1 compression ratio on HTML.
- **Engineering Effort:** Small (~1 hour)
- **Recommended Prompt:** `Add zstd compression to RawStorage.upload_text() before S3 upload. Store with .zst extension and content-encoding header. Add decompression to any raw data re-processing path.`

### L-07: MLflow unused despite running container
- **Source:** `ml-audit.md` §6
- **Description:** MLflow container runs on port 5000. Zero `mlflow.log_*()` calls in the codebase. `trainer.py` tracks metrics manually in PostgreSQL `model_registry` instead.
- **Business Impact:** Wasted container resources. No experiment tracking UI despite having the infrastructure.
- **Engineering Effort:** Medium (~1 day)
- **Recommended Prompt:** `Integrate MLflow tracking into trainer.py: mlflow.set_tracking_uri(), mlflow.log_params(), mlflow.log_metrics(), mlflow.log_model(). Log each training run as an MLflow experiment. Store trained model as MLflow artifact. Use MLflow model registry alongside the custom model_registry PostgreSQL table.`

### L-08: Segmented market features are scalar constants
- **Source:** `ml-audit.md` §4.2
- **Description:** 7 of 15 features return the same value for every row in the training DataFrame. They are segment-level constants, not per-listing features. This reduces the model's discriminative power.
- **Business Impact:** Model less accurate than it could be. Features add noise without signal.
- **Engineering Effort:** Small (~2 hours)
- **Recommended Prompt:** `Refactor market and vehicle features to be per-listing where possible. For example: instead of one segment_median_price for all rows, compute the median excluding the listing itself (leave-one-out). For brand_reliability, compute per-model rather than per-brand. Or keep as-is and document that these serve as segment-level priors in the model.`

### L-09: No input sanitization on valuation request fields
- **Source:** `api-audit.md` §4.3
- **Description:** Make and model strings are stored as-is in `valuation_queries`. No trimming, no case normalization. " toyota " and "Toyota" produce different cache keys and DB rows.
- **Business Impact:** Cache fragmentation. Same car with slightly different input produces multiple cache entries. DB bloat.
- **Engineering Effort:** Small (~30 minutes)
- **Recommended Prompt:** `Add input normalization middleware or Pydantic validators on ValuationRequest: strip whitespace, title-case make/model. This ensures cache key consistency and clean DB storage.`

### L-10: Config database_url_sync duplicates database_url
- **Source:** `project-audit.md` §15
- **Description:** `settings.database_url` (async) and `settings.database_url_sync` (sync) are separate config fields. If one is updated and the other isn't, migrations fail.
- **Business Impact:** Configuration drift between async app and sync Alembic connections.
- **Engineering Effort:** Small (~30 minutes)
- **Recommended Prompt:** `Derive database_url_sync from database_url programmatically: replace +asyncpg with +psycopg2, or parse and reconstruct. Remove the separate DATABASE_URL_SYNC env var. This eliminates the drift risk.`

### L-11: Feature flags model has no runtime integration
- **Source:** `project-audit.md` §3.3
- **Description:** `feature_flags` table and `FeatureFlag` model exist but no middleware or service checks flags at runtime. Flags can be toggled in the DB but have zero effect.
- **Business Impact:** Can't do gradual rollouts, A/B tests, or emergency feature kills.
- **Engineering Effort:** Medium (~1 day)
- **Recommended Prompt:** `Implement a feature flag service that loads flags from the feature_flags table (with in-memory cache, 60s TTL). Create a FastAPI dependency is_feature_enabled(flag_name) that checks the flag. Use for: ML model shadow deployment, new UI features, rate limit tiers.`

### L-12: Pipeline orchestrator doesn't use PipelineOrchestrator
- **Source:** `project-audit.md` §3.4
- **Description:** `PipelineOrchestrator` class exists but is never instantiated or called. The scraper `run()` method is called directly. No orchestrator coordinates the full pipeline.
- **Business Impact:** Pipeline stages run ad-hoc. No centralized error handling, retry, or sequencing.
- **Engineering Effort:** Small (~2 hours)
- **Recommended Prompt:** `Wire PipelineOrchestrator into the scraper execution path. Create a CLI command or scheduler job that instantiates the orchestrator with a session factory and a list of scrapers, calls run_pipeline(), and logs results.`

### L-13: No conftest.py at src level for shared test configuration
- **Source:** `project-audit.md` §17
- **Description:** Test configuration is scattered — each test file creates its own engine, settings, and fixtures.
- **Business Impact:** Duplicate setup code. Inconsistent test patterns.
- **Engineering Effort:** Small (~1 hour)
- **Recommended Prompt:** `Consolidate test configuration: create a shared conftest.py with an in-memory SQLite fixture, a settings fixture, and helper functions for creating test data. Update all test files to use shared fixtures.`

### L-14: No Python type stubs for generated code
- **Source:** `project-audit.md` §2
- **Description:** `mypy` is configured with `strict=true` but `ignore_missing_imports=true`. Third-party packages without type stubs (lightgbm, pandera, slowapi) are silently ignored.
- **Business Impact:** Type checking is less effective than it could be. Some type errors from third-party packages slip through.
- **Engineering Effort:** Small (~1 hour)
- **Recommended Prompt:** `Add type stubs for key packages: pip install types-requests types-python-dateutil pandas-stubs. Configure mypy overrides for packages without stubs. Consider relaxing strict mode or adding per-module mypy configs.`

### L-15: Swap hardcoded API base URL in UI
- **Source:** `project-audit.md` §4
- **Description:** `ui/index.html` hardcodes `http://localhost:8000/v1` as the API base URL. Won't work in production without manual change.
- **Business Impact:** UI broken in any environment other than localhost:8000.
- **Engineering Effort:** Trivial (~5 minutes)
- **Recommended Prompt:** `Change the hardcoded API base URL in ui/index.html to use window.location.origin + '/v1'. This makes the UI work on any host/port without modification.`

### L-16: Inline Pydantic model for URLValuationRequest
- **Source:** `api-audit.md` §4.5
- **Description:** `URLValuationRequest` is defined inline in `routes/url_valuate.py` rather than in `schemas/valuation.py` with the other request schemas.
- **Business Impact:** Inconsistent code organization. Not visible in OpenAPI schema module grouping.
- **Engineering Effort:** Trivial (~10 minutes)
- **Recommended Prompt:** `Move URLValuationRequest class definition from routes/url_valuate.py to schemas/valuation.py. Import in the route file.`

---

## ⚪ Future (12 items)

### F-01: Mobile app (React Native)
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** Blueprint Phase 4 specifies a React Native mobile app sharing the API.
- **Business Impact:** Mobile users can't access the platform natively.
- **Engineering Effort:** Very Large (~2-3 months)
- **Dependencies:** API stability, auth, push notification infrastructure
- **Recommended Prompt:** `Scope and plan the React Native mobile app. Start with the valuation form + results screen as MVP. Share API types between frontend and mobile. Use Expo for faster iteration.`

### F-02: Enterprise API tier with SLAs
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** Blueprint Phase 4 specifies enterprise tier with contracts, SLAs, and higher rate limits.
- **Business Impact:** No monetization path for high-volume API consumers.
- **Engineering Effort:** Large (~2-3 weeks)
- **Dependencies:** Auth system (JWT+API keys already exist), billing integration, usage tracking
- **Recommended Prompt:** `Design the enterprise API tier: usage-based pricing, SLA-backed uptime (99.5%), dedicated rate limits, usage dashboard. Implement API key tier enforcement in rate limiter. Add usage tracking per API key. Create enterprise onboarding flow.`

### F-03: Dealer dashboard
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** Blueprint Phase 4 specifies a dealer dashboard for inventory valuation and market analysis.
- **Business Impact:** No B2B offering for dealerships.
- **Engineering Effort:** Large (~3-4 weeks)
- **Dependencies:** Auth, UI framework decision, knowledge base
- **Recommended Prompt:** `Design the dealer dashboard: bulk VIN valuation, inventory market analysis, price positioning vs market, days-on-market predictions. Start with bulk valuation upload as MVP.`

### F-04: Image-based car detail extraction (OCR)
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** Blueprint Phase 4 specifies OCR extraction of car details from listing photos.
- **Business Impact:** Can't extract data from image-only listings.
- **Engineering Effort:** Large (~3-4 weeks)
- **Dependencies:** Vision API (Claude Vision, Google Vision, or AWS Rekognition)
- **Recommended Prompt:** `Prototype image-based extraction: accept a listing image URL, send to Claude Vision API with a prompt to extract make/model/year/mileage/spec from dashboard/odometer/exterior photos. Evaluate accuracy on 50 sample images. Integrate into URL valuation flow as a fallback when HTML parsing fails.`

### F-05: EV battery health estimation
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** Blueprint Phase 4 specifies EV battery health estimation.
- **Business Impact:** Can't value EVs accurately — battery health is the primary value driver.
- **Engineering Effort:** Large (~3-4 weeks)
- **Dependencies:** EV market data, battery degradation models, manufacturer specs
- **Recommended Prompt:** `Research EV battery degradation models. Build a feature that estimates battery health from age + mileage + model. Integrate into valuation engine as an EV-specific adjustment. Start with Tesla Model 3 and Nissan Leaf as proof of concept.`

### F-06: JATO spec data import
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies JATO import for comprehensive vehicle specs. Currently using manually curated data for 32 models.
- **Business Impact:** Incomplete spec coverage. Manual curation doesn't scale beyond 50 models.
- **Engineering Effort:** Medium (~1-2 weeks)
- **Dependencies:** JATO license ($5K-$15K/year), data delivery format
- **Recommended Prompt:** `Evaluate JATO data delivery options. Design an import pipeline: parse JATO data → map to car_specs schema → deduplicate against existing curated data → validate completeness. Start with GCC-top-50 models as validation set.`

### F-07: Partsouq scraper for parts pricing
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies a Partsouq scraper for real parts pricing data.
- **Business Impact:** Maintenance cost estimates are static curated data, not live market prices.
- **Engineering Effort:** Medium (~1 week)
- **Dependencies:** Partsouq access, scraper framework
- **Recommended Prompt:** `Build a Partsouq scraper: search for common repair parts (brake pads, filters, belts, water pumps) for top 20 GCC models. Extract part numbers + prices. Store in a new parts_pricing table. Use to validate and update maintenance_costs estimates.`

### F-08: DriveArabia community mining
- **Source:** `master-plan-validation.md` §3
- **Description:** Blueprint Phase 3 specifies mining DriveArabia forums for common issues and ownership experiences.
- **Business Impact:** Car issue knowledge base is limited to manually curated data.
- **Engineering Effort:** Medium (~1-2 weeks)
- **Dependencies:** Web scraping, NLP/text extraction
- **Recommended Prompt:** `Build a DriveArabia forum scraper: fetch model-specific forum threads, extract issue descriptions using NLP (keyword extraction, sentiment analysis), match to car_issues schema. Flag as source='drivearabia', confirmed=False until human review.`

### F-09: Price alerts with email/push delivery
- **Source:** `master-plan-validation.md` §1 (Phase 4)
- **Description:** `PriceAlert` model exists but no scheduler checks alerts or delivers notifications.
- **Business Impact:** Price alert feature is non-functional despite having the data model.
- **Engineering Effort:** Medium (~1 week)
- **Dependencies:** Email service (SendGrid/SES), push notification infrastructure
- **Recommended Prompt:** `Implement price alert delivery: APScheduler job runs daily, queries active price_alerts, computes current median price for each alert's make/model/year range, if median <= target_price and alert hasn't triggered recently, send email notification. Update last_triggered_at.`

### F-10: Saved valuation sharing
- **Source:** `api-audit.md` §6
- **Description:** `SavedValuation` model exists but no API endpoint to create, list, or share saved valuations.
- **Business Impact:** Users can't save or share valuations despite having the data model.
- **Engineering Effort:** Small (~1 day)
- **Dependencies:** User auth wired to endpoints
- **Recommended Prompt:** `Create CRUD endpoints for saved valuations: POST /v1/valuations (save), GET /v1/valuations (list user's saved), DELETE /v1/valuations/{id}. Generate a shareable link with a short UUID. Add a public GET /v1/shared/{share_id} that returns the cached valuation.`

### F-11: A/B testing framework for model comparison
- **Source:** `ml-audit.md` §16
- **Description:** No framework to compare statistical vs ML model performance on live traffic.
- **Business Impact:** Can't measure whether the ML model actually improves valuations.
- **Engineering Effort:** Medium (~1 week)
- **Dependencies:** H-12 (ML model must run in API), feature flags (L-11)
- **Recommended Prompt:** `Build an A/B testing framework: randomly assign valuation requests to statistical-only (control) or statistical+ML (treatment) groups using a feature flag with rollout %. Log group assignment. Compare estimate accuracy against eventual sold prices. Track user satisfaction metrics per group.`

### F-12: Automated hyperparameter tuning
- **Source:** `ml-audit.md` §16
- **Description:** LightGBM hyperparameters are hardcoded. No tuning, no cross-validation beyond the single 85/15 split.
- **Business Impact:** Model may be significantly suboptimal. Manual tuning is time-consuming.
- **Engineering Effort:** Medium (~3 days)
- **Dependencies:** C-03 (model persistence), training scheduler
- **Recommended Prompt:** `Integrate Optuna for automated hyperparameter tuning. Define search space for LightGBM params (n_estimators, max_depth, learning_rate, num_leaves, min_child_samples, subsample, colsample_bytree). Run 50 trials with 5-fold cross-validation. Log all trials to MLflow. Select best params and update trainer.py defaults.`

---

## Debt by Module

| Module | Critical | High | Medium | Low | Future |
|--------|----------|------|--------|-----|--------|
| Infrastructure/Deployment | C-01 | — | M-21, M-23 | L-03 | — |
| Database | C-02, C-06 | — | M-07, M-08, M-09, M-10, M-11, M-12, M-13, M-14 | L-06, L-09 | — |
| API/Auth | C-04, C-05 | H-02, H-03, H-04, H-05, H-09, H-10 | M-15, M-16, M-17, M-18 | L-04, L-05, L-15, L-16 | F-10 |
| Observability | C-07, C-08 | H-08 | M-01, M-02, M-03, M-04, M-05, M-06 | — | — |
| ML/Engine | C-03 | H-06, H-07, H-11, H-12, H-13, H-14 | — | L-07, L-08 | F-06, F-07, F-08, F-11, F-12 |
| Frontend/UI | — | — | M-19 | — | F-03 |
| Knowledge Base | — | H-01 | — | — | F-06 |
| Cleanup/Docs | — | — | M-20, M-22, M-24 | L-01, L-02, L-10, L-11, L-12, L-13, L-14 | — |
| Product Features | — | — | — | — | F-01, F-02, F-04, F-05, F-09 |

---

*Technical debt register completed 2026-07-12. Compiled from 6 audit documents.*
