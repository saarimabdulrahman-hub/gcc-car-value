# GCC Car Value Platform — Observability Audit

**Date:** 2026-07-12  
**Blueprint Reference:** §11 (Monitoring & Observability)  
**Files Audited:** `observability/`, `config.py`, `routes/health.py`, `routes/admin.py`, `engine/drift.py`, all `structlog` usage sites

---

## 1. Observability Architecture (Blueprint vs Reality)

| Component | Blueprint Spec | Implemented | Wired |
|-----------|---------------|-------------|-------|
| Structured logging (structlog) | ✅ Required | ✅ `logging.py` | ⚠️ Partial (8 of 30+ modules) |
| Prometheus metrics | ✅ Required | ✅ 5 metrics defined | ❌ Never incremented |
| `/metrics` endpoint | Implicit | ✅ `metrics_endpoint()` exists | ❌ Not registered in `main.py` |
| OpenTelemetry tracing | ✅ Required | ❌ Flag only (`otel_enabled`) | ❌ No instrumentation |
| Grafana dashboards (4) | ✅ Required | ❌ Not created | ❌ |
| Sentry error tracking | ✅ Required | ❌ Not configured | ❌ |
| Alerting (8 rules) | ✅ Required | ❌ Not implemented | ❌ |
| Health check | ✅ Required | ✅ `GET /v1/health` | ✅ |
| Drift detection | ✅ Required | ✅ `engine/drift.py` | ⚠️ Computes but doesn't alert |
| Pipeline run metadata | ✅ Required | ✅ `pipeline_runs` table | ✅ (via orchestrator) |
| Scraper health tracking | ✅ Required | ✅ `scraper_health` table | ✅ (via admin endpoint) |
| Admin monitoring endpoints | Not specified | ✅ 3 endpoints | ⚠️ No auth |
| Audit logging | ✅ Required (§10.6) | ❌ Not implemented | ❌ |

---

## 2. Logging

### 2.1 Configuration (`src/observability/logging.py`)

**Engine:** structlog over stdlib `logging`

**Processors (in order):**
1. `contextvars.merge_contextvars` — merges context-local variables
2. `filter_by_level` — respects log level
3. `add_logger_name` — includes logger name
4. `add_log_level` — includes level name
5. `TimeStamper(fmt="iso")` — ISO 8601 timestamps
6. `StackInfoRenderer` — stack traces on exception
7. `format_exc_info` — formatted exception info
8. `ConsoleRenderer` (dev) or `JSONRenderer` (prod) — output format

**Wrapper:** `structlog.stdlib.BoundLogger`  
**Root level:** Set from `settings.log_level` (default `"INFO"`, `.env.example` says `"DEBUG"`)

**Initialization:** `setup_logging()` is called at module import time in `main.py`. The `__init__.py` in `observability/` duplicates the same `setup_logging()` call — it runs if the package is imported.

### 2.2 Log Usage by Module

| Module | Logger | Events Logged | Quality |
|--------|--------|--------------|---------|
| `routes/valuation.py` | ✅ | `valuation_cache_hit`, `valuation_computed` | ✅ Structured key=value pairs |
| `routes/url_valuate.py` | ✅ | `url_parsed`, `valuation_error`, `dubizzle_parse_failed` | ✅ Structured |
| `routes/health.py` | ✅ | `db_health_check_failed` | ✅ Structured |
| `routes/admin.py` | ✅ | (logger defined but no log calls) | ❌ Defined, never used |
| `pipeline/orchestrator.py` | ✅ | `scraper_starting`, `scraper_complete` | ✅ Structured |
| `engine/trainer.py` | ✅ | `insufficient_training_data`, `model_trained` | ✅ Structured |
| `engine/drift.py` | ✅ | `drift_detected` | ✅ Structured |
| `knowledge/seed.py` | ✅ | `knowledge_base_seeded` | ✅ Structured |
| `routes/models.py` | ❌ | None | No logger defined |
| `api/dependencies.py` | ❌ | None | No logger defined |
| `pipeline/validator.py` | ❌ | None | No logger defined |
| `pipeline/normalizer.py` | ❌ | None | No logger defined |
| `pipeline/quality.py` | ❌ | None | No logger defined |
| `pipeline/promoter.py` | ❌ | None | No logger defined |
| `engine/statistical.py` | ❌ | None | No logger defined |
| `engine/comp_finder.py` | ❌ | None | No logger defined |
| `engine/llm_explainer.py` | ❌ | None | No logger defined |
| `engine/recommendations.py` | ❌ | None | No logger defined |
| `engine/vin_decoder.py` | ❌ | None | No logger defined |
| `engine/features/*.py` | ❌ | None | No logger defined |
| `scrapers/base.py` | ❌ | None | No logger defined |
| `scrapers/dubizzle_uae/parser.py` | ❌ | None | No logger defined |
| All 9 other scraper implementations | ❌ | None | No logger defined |
| `auth/jwt.py` | ❌ | None | No logger defined |
| `db/session.py` | ❌ | None | No logger defined |

**Coverage: 8 of 30+ modules (27%)** use structlog.

### 2.3 Log Quality Assessment

**Good patterns:**
- Key-value pairs in log calls: `logger.info("valuation_computed", make=..., model=..., year=..., estimate=..., confidence=..., comp_count=...)`
- Error context: `logger.error("db_health_check_failed", error=str(e))`
- Warning context: `logger.warning("drift_detected", type=..., feature=..., psi=...)`

**Missing patterns:**
- No `trace_id` / `request_id` in any log call (blueprint §11.2 specifies `trace_id` correlation)
- No request-scoped context (no middleware to inject request metadata into structlog context)
- No log calls in scrapers — scraper errors are captured as `result.errors` list but never logged
- No log calls in pipeline stages — promotion/rejection decisions are silent
- No log calls in API dependencies, model routes, or auth code
- `routes/admin.py` defines a logger but never calls it

### 2.4 Blueprint Compliance: Structured Logging

| Blueprint Requirement (§11.2) | Status |
|-------------------------------|--------|
| "Every log line includes `trace_id`" | ❌ Not implemented |
| No `print()` or bare `logging.info()` | ✅ No `print()` found; structlog is the only logger |
| Structured, searchable, correlated logs | ⚠️ Partially — logs are structured JSON (in prod) but not correlated |

---

## 3. Metrics

### 3.1 Prometheus Metrics Defined (`src/observability/metrics.py`)

| Metric | Type | Name | Labels | Purpose |
|--------|------|------|--------|---------|
| `valuation_requests` | Counter | `valuation_requests_total` | `tier`, `confidence` | Count valuations by user tier and confidence level |
| `valuation_duration` | Histogram | `valuation_duration_seconds` | — | Response time distribution (50ms–5s buckets) |
| `scraper_runs` | Counter | `scraper_runs_total` | `source`, `status` | Count scraper executions by source and success/failure |
| `scraper_listings_ingested` | Counter | `scraper_listings_ingested_total` | `source` | Count listings ingested per source |
| `data_freshness_hours` | Gauge | `data_freshness_hours` | `source` | Hours since last successful scrape per source |

### 3.2 Metrics Usage: NONE

**All 5 metrics are defined but never incremented, observed, or set anywhere in the codebase.**

A grep for `.inc()`, `.observe()`, `.set()`, `.labels()` across the entire `src/` directory returns zero matches. The metrics are imported only in `observability/metrics.py` itself.

### 3.3 `/metrics` Endpoint: NOT REGISTERED

The `metrics_endpoint()` function exists and would return Prometheus text format if called:
```python
def metrics_endpoint() -> Response:
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")
```

But it is **never registered** in `main.py`. There is no `app.add_route("/metrics", ...)` or `app.include_router(...)` for metrics. The Prometheus endpoint is unreachable.

### 3.4 Missing Metrics (Recommended)

| Metric | Type | Labels | Rationale |
|--------|------|--------|-----------|
| `api_requests_total` | Counter | `method`, `path`, `status_code` | Overall API traffic |
| `api_request_duration_seconds` | Histogram | `method`, `path` | Per-endpoint latency |
| `db_query_duration_seconds` | Histogram | `operation` | DB performance |
| `db_pool_size` | Gauge | — | Connection pool usage |
| `scraper_errors_total` | Counter | `source`, `error_type` | Scraper failure rates |
| `scraper_duration_seconds` | Histogram | `source` | Scraper run duration |
| `pipeline_records_total` | Counter | `source`, `stage`, `outcome` | Records through each pipeline stage (promoted/rejected) |
| `pipeline_quality_score` | Histogram | `source` | Quality score distribution |
| `valuation_cache_hits_total` | Counter | — | Cache efficiency |
| `valuation_insufficient_comps_total` | Counter | `make`, `model` | Track models needing more data |
| `model_prediction_mae` | Gauge | `model_version` | Active model performance |
| `drift_psi` | Gauge | `drift_type`, `feature` | Current PSI values |
| `external_http_errors_total` | Counter | `target` | URL fetch failures |

---

## 4. Health Check

### 4.1 Endpoint: `GET /v1/health`

**Implementation:** `src/api/routes/health.py`

**Check performed:** `SELECT 1` against PostgreSQL

**Response:**
```json
{"status": "ok", "database": "healthy", "version": "0.1.0"}
```

### 4.2 Health Check Assessment

| Aspect | Status | Detail |
|--------|--------|--------|
| Database connectivity | ✅ | `SELECT 1` via async session |
| Depth of check | ⚠️ Shallow | Doesn't check connection pool health, replication lag, or disk usage |
| Dependency checks | ❌ | Doesn't check S3 connectivity, MLflow, external exchange rate API |
| Uptime/version | ⚠️ Partial | Returns version string; no uptime, no git commit |
| Response on failure | ⚠️ Degraded 200 | Returns `200 OK` with `status: "degraded"` on DB failure — some load balancers won't detect this as unhealthy |
| Endpoint health | ❌ | No health check for scrapers, valuation engine, or URL fetcher |

### 4.3 Blueprint Compliance

| Blueprint Requirement | Status |
|-----------------------|--------|
| `/v1/health` endpoint | ✅ |
| Database health | ✅ (basic) |
| Synthetic monitoring (external region health check) | ❌ Not implemented |

---

## 5. Monitoring & Admin Endpoints

### 5.1 `GET /v1/admin/stats`

Returns platform-wide counters: total/active listings, total/recent valuations, last pipeline run, unacknowledged drift count.

**Queries: 6 sequential COUNT queries** — no materialized views, each request scans tables.

### 5.2 `GET /v1/admin/scrapers`

Returns per-scraper last run time and staleness (healthy if ≤36h, stale if >36h).

### 5.3 `GET /v1/admin/quality`

Returns quality score distribution: high (≥80), medium (60-79), low (<60) with percentages.

### 5.4 Admin Endpoint Limitations

| Issue | Detail |
|-------|--------|
| No auth | Anyone can access operational data |
| No caching | Every request runs fresh queries |
| Read-only | No ability to acknowledge drift events, retry failed scrapers, or change feature flags |
| No time range | Stats are all-time only; no way to filter by date range |

---

## 6. Drift Detection

### 6.1 Implementation (`src/engine/drift.py`)

| Drift Type | Metric | Threshold | Status |
|------------|--------|-----------|--------|
| Feature drift | PSI per feature vs 4-week baseline | PSI > 0.2 (warning), > 0.3 (alert) | ✅ Implemented |
| Target drift | Median price % change | > 15% | ✅ Implemented |
| Prediction drift | MAE degradation % | > 30% | ✅ Implemented |
| Market drift | Volume drop % / volatility ratio | Volume > 40% or vol > 2× | ✅ Implemented |

**`log_drift_event()`** persists results to the `drift_events` table. On `threshold_exceeded=True`, it logs at WARNING level.

### 6.2 Drift Detection Gaps

| Issue | Detail |
|-------|--------|
| **No scheduler** | Drift detection is never called automatically — no cron, no APScheduler job |
| **No baseline management** | No mechanism to define, store, or update baseline periods |
| **No alerting** | Exceeded thresholds are logged and stored but never trigger notifications |
| **No acknowledgment workflow** | `drift_events.acknowledged` column exists but no API to set it |
| **Feature drift never runs** | `check_feature_drift()` requires baseline and current feature distributions — no code builds these |

---

## 7. Tracing

### 7.1 Status: NOT IMPLEMENTED

The blueprint specifies OpenTelemetry for end-to-end request tracing (API → DB → model → response).

| Component | Status |
|-----------|--------|
| `otel_enabled` config flag | ✅ Exists in `config.py`, defaults to `False` |
| OpenTelemetry SDK | ❌ Not installed (not in `pyproject.toml` dependencies) |
| Instrumentation | ❌ No middleware, no decorators, no manual spans |
| Exporter (Jaeger/Tempo) | ❌ Not configured |
| Trace ID injection into logs | ❌ Not implemented |

---

## 8. Error Tracking

### 8.1 Status: NOT IMPLEMENTED

The blueprint specifies Sentry for exception tracking and error grouping.

| Component | Status |
|-----------|--------|
| Sentry SDK | ❌ Not installed (not in `pyproject.toml`) |
| Sentry initialization | ❌ Not configured |
| FastAPI integration | ❌ No middleware |
| Error grouping | ❌ Not available |

**Current error handling:**
- API routes catch exceptions and return HTTP 422 with `detail` string
- Structured logs capture `error=str(e)` in key-value pairs
- Scraper errors are collected in `ScraperResult.errors` list as dicts
- No centralized error aggregation, deduplication, or alerting

---

## 9. Alert Readiness

### 9.1 Blueprint Alert Rules vs Implementation

| # | Blueprint Alert Rule (§11.4) | Condition | Implemented | Wired |
|---|------------------------------|-----------|-------------|-------|
| 1 | Scraper failure | No successful run in 36h | ⚠️ Tracked in `scraper_health` | ❌ No notification |
| 2 | API error rate > 5% | 5xx/total > 0.05 for 5 min | ❌ No error rate tracking | ❌ |
| 3 | Data freshness > 48h | Last successful scrape > 48h | ⚠️ Tracked via `data_freshness_hours` gauge (never set) | ❌ |
| 4 | Model degradation | MAE > baseline × 1.3 for 50+ queries | ⚠️ `check_prediction_drift()` exists | ❌ Never called |
| 5 | Drift detected | PSI > 0.3 on any feature | ⚠️ `check_feature_drift()` exists | ❌ Never called |
| 6 | DB disk > 80% | Disk usage > 80% | ❌ No disk monitoring | ❌ |
| 7 | Dead letter growth | Rejection rate > 20% for a source | ❌ No rate tracking | ❌ |
| 8 | API latency p95 > 2s | Sustained for 10 min | ❌ No p95 tracking | ❌ |

**Result: 0 of 8 alert rules are operational.** Two have partial implementation (drift detection logic exists but never runs). Six have no implementation at all.

### 9.2 Alerting Infrastructure

| Component | Status |
|-----------|--------|
| Prometheus Alertmanager | ❌ Not in docker-compose |
| Slack webhook integration | ❌ Not configured |
| Email notifications | ❌ Not configured |
| PagerDuty integration | ❌ Not configured |

---

## 10. Dashboard Readiness

### 10.1 Blueprint Dashboards vs Reality

| Dashboard | Sections | Status |
|-----------|----------|--------|
| **Platform Health** | API req/min, p50/p95/p99 latency, error rate, DB pool, scraper freshness | ❌ No Grafana; no metrics pipeline |
| **Data Quality** | Quality score histogram, rejection rate sparkline, field extraction %, dead letter size | ❌ |
| **Model Performance** | MAE over time, shadow comparison, PSI heatmap, prediction distribution | ❌ |
| **Business Metrics** | Valuations/day by tier, top makes/models, low-confidence %, cache hit rate | ❌ |

**All 4 dashboards are not implemented.** No Grafana instance exists in docker-compose. No data source is configured. No dashboard JSONs exist in the repository.

---

## 11. Infrastructure Gaps

### 11.1 Docker Compose Observability Services

Current `docker-compose.yml` services:
- `api` — FastAPI app
- `db` — PostgreSQL + pgvector
- `mlflow` — MLflow tracking server
- `localstack` — S3 emulation

**Missing services:**
- ❌ Prometheus (metrics collection)
- ❌ Grafana (dashboards)
- ❌ Jaeger/Tempo (tracing)
- ❌ Alertmanager (alert routing)
- ❌ Sentry (error tracking — SaaS, no container needed)

### 11.2 CI/CD Observability

The GitHub Actions CI (`ci.yml`) does:
- Run pytest
- Upload coverage to Codecov

It does **not:**
- Run linters on observability configs
- Validate Prometheus metric naming conventions
- Check that metrics are incremented in code
- Run any integration test against the `/metrics` or `/health` endpoints

---

## 12. Summary Matrix

| Capability | Implementation | Wiring | Production Ready |
|-----------|---------------|--------|-----------------|
| Structured logging | ✅ structlog configured | ⚠️ 27% module coverage | ❌ No trace IDs, no request context |
| Prometheus metrics | ✅ 5 metrics defined | ❌ 0% incremented | ❌ Dead code |
| `/metrics` endpoint | ✅ Function exists | ❌ Not registered | ❌ Unreachable |
| Health check | ✅ `GET /v1/health` | ✅ | ⚠️ Too shallow for LB |
| Admin monitoring | ✅ 3 endpoints | ✅ | ⚠️ No auth, no caching |
| Drift detection | ✅ 4 drift types | ❌ Never scheduled | ❌ Logic exists, never runs |
| OpenTelemetry tracing | ❌ | ❌ | ❌ |
| Sentry error tracking | ❌ | ❌ | ❌ |
| Grafana dashboards | ❌ | ❌ | ❌ |
| Alerting (8 rules) | ❌ | ❌ | ❌ |
| Audit logging | ❌ | ❌ | ❌ |

**Overall Observability Score: 1.5 / 10**

---

## 13. Recommendations

### P0 — Critical

| # | Action | Effort |
|---|--------|--------|
| 1 | **Register `/metrics` endpoint in main.py** — 1 line: `app.add_route("/metrics", metrics_endpoint)` | Trivial |
| 2 | **Increment existing metrics** — add `.inc()`/`.observe()` calls in valuation route, scraper base, and orchestrator | Small |
| 3 | **Add Prometheus + Grafana to docker-compose** — enable metrics collection and visualization | Medium |
| 4 | **Make health check return 503 on failure** — current 200-on-degraded pattern won't trigger LB failover | Trivial |

### P1 — High

| # | Action | Effort |
|---|--------|--------|
| 5 | **Add structlog to all modules** — at minimum: valuation engine, scraper base, promoter, comp finder | Medium |
| 6 | **Add trace_id middleware** — generate UUID per request, inject into structlog context | Small |
| 7 | **Schedule drift detection** — APScheduler job to run weekly after scraper pipeline | Small |
| 8 | **Wire up alerting** — at minimum: scraper failure → Slack webhook | Medium |
| 9 | **Add Sentry SDK** — `pip install sentry-sdk`, 3 lines of FastAPI integration | Small |

### P2 — Medium

| # | Action | Effort |
|---|--------|--------|
| 10 | **Add OpenTelemetry** — auto-instrument FastAPI, SQLAlchemy, httpx | Medium |
| 11 | **Create Grafana dashboards** — 4 dashboards per blueprint §11.3 | Large |
| 12 | **Add missing Prometheus metrics** — 13 recommended metrics from §3.4 | Medium |
| 13 | **Add Prometheus alert rules** — 8 rules from blueprint §11.4 | Medium |
| 14 | **Add dead letter monitoring** — track rejection rate, alert on spikes | Small |
| 15 | **Add synthetic health check** — external cron hitting `/v1/health` from different region | Small |

### P3 — Future

| # | Action | Effort |
|---|--------|--------|
| 16 | **Distributed tracing with Jaeger/Tempo** — end-to-end request tracing | Large |
| 17 | **Real User Monitoring (RUM)** — frontend performance metrics | Medium |
| 18 | **SLO/SLI dashboard** — define and track service level objectives | Medium |

---

*Observability audit completed 2026-07-12. No production code modified.*
