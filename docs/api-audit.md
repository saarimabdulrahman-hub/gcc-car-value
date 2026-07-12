# GCC Car Value Platform — API Audit

**Date:** 2026-07-12  
**Base URL:** `http://localhost:8000`  
**API Prefix:** `/v1`  
**Framework:** FastAPI (auto-generated OpenAPI at `/docs`, `/openapi.json`)  
**App Entry:** `src/api/main.py`

---

## 1. Endpoint Index

| # | Method | Path | Router File | Auth | Rate Limit |
|---|--------|------|------------|------|-----------|
| 1 | `GET` | `/` | `main.py` | None | None |
| 2 | `GET` | `/v1/health` | `routes/health.py` | None | None |
| 3 | `POST` | `/v1/valuate` | `routes/valuation.py` | None | 10/min |
| 4 | `POST` | `/v1/valuate-url` | `routes/url_valuate.py` | None | None |
| 5 | `GET` | `/v1/models` | `routes/models.py` | None | None |
| 6 | `GET` | `/v1/models/{make}` | `routes/models.py` | None | None |
| 7 | `GET` | `/v1/models/{make}/{model}` | `routes/models.py` | None | None |
| 8 | `GET` | `/v1/admin/stats` | `routes/admin.py` | None | None |
| 9 | `GET` | `/v1/admin/scrapers` | `routes/admin.py` | None | None |
| 10 | `GET` | `/v1/admin/quality` | `routes/admin.py` | None | None |

**Blueprint-specified but missing:**
- `GET /v1/valuate/{id}` — Retrieve cached valuation by ID
- `GET /v1/trends` — Market trends with query params

---

## 2. App-Level Configuration

### Middleware Stack

| Layer | Implementation | Detail |
|-------|---------------|--------|
| CORS | `CORSMiddleware` | Origins: `settings.api_cors_origins` (default `["http://localhost:3000"]`). Methods: `*`. Headers: `*`. Credentials: `true`. |
| Rate Limiting | `slowapi.Limiter` | Keyed by `get_remote_address`. In-memory counters (not Redis-backed). |
| Exception Handler | `_rate_limit_exceeded_handler` | Returns 429 when slowapi limit exceeded. |
| Static Files | `StaticFiles` | Mounted at `/` serving `ui/` directory with `html=True`. |

### Global Dependencies

| Dependency | Scope | Purpose |
|-----------|-------|---------|
| `get_db()` → `AsyncSession` | Per-request | Yields async SQLAlchemy session, auto-closed after request |
| `limiter` | App-level | slowapi rate limiter instance on `app.state.limiter` |

**⚠️ No auth middleware.** JWT and API key logic exist in `src/auth/jwt.py` but are never wired into any endpoint as a `Depends()` guard. The `user_id` field in `ValuationQuery` is always NULL.

---

## 3. Endpoint Documentation

---

### 3.1 `GET /` — Serve UI

```
GET /
```

**Router:** Inline in `main.py` (`@app.get("/")`)

**Description:** Serves `ui/index.html` with no-cache headers.

**Request:** None.

**Response:** `text/html`

| Status | Content-Type | Body |
|--------|-------------|------|
| `200 OK` | `text/html` | Contents of `ui/index.html` |
| `404 Not Found` | `text/html` | `<h1>UI not found</h1>` |

**Headers:**
```
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

**Dependencies:** None (reads file from disk, no DB access)

**Notes:**
- The app also mounts `StaticFiles(directory="ui/", html=True)` at `/`. FastAPI resolves explicit routes before mounted apps, so `GET /` takes priority. Other paths under `/` (e.g., `/test.html`, `/previews/a-minimal.html`) are served by the static mount.
- **⚠️ Route conflict risk:** The static mount at `/` could shadow API routes if not careful — currently safe because `/v1/*` routes are registered before the mount.

---

### 3.2 `GET /v1/health` — Health Check

```
GET /v1/health
```

**Router:** `routes/health.py`

**Description:** Database connectivity check. Executes `SELECT 1` against PostgreSQL.

**Request:** None.

**Response:** `application/json`

| Status | Body |
|--------|------|
| `200 OK` | `{"status": "ok", "database": "healthy", "version": "0.1.0"}` |
| `200 OK` | `{"status": "degraded", "database": "unhealthy", "version": "0.1.0"}` |

**Schema:**
```json
{
  "status": "ok | degraded",
  "database": "healthy | unhealthy",
  "version": "0.1.0"
}
```

**Auth:** None

**Rate Limit:** None

**Dependencies:** `get_db()` → `AsyncSession`

**Error Handling:**
- Catches all exceptions from `SELECT 1`. On failure, returns 200 with `status: "degraded"` rather than a 5xx. This is intentional — the health endpoint itself never errors out.

---

### 3.3 `POST /v1/valuate` — Vehicle Valuation

```
POST /v1/valuate
```

**Router:** `routes/valuation.py`

**Description:** Computes a fair market value estimate for a vehicle using the statistical valuation engine. Results are cached for the same day (cache key includes date).

**Rate Limit:** 10 requests/minute (anonymous)

**Auth:** None (user_id left NULL)

---

#### Request

**Content-Type:** `application/json`

**Schema:** `ValuationRequest` (Pydantic)

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `make` | `string` | ✅ Yes | — | e.g. "Toyota" |
| `model` | `string` | ✅ Yes | — | e.g. "Land Cruiser" |
| `year` | `integer` | ✅ Yes | 1990 ≤ year ≤ 2027 | Manufacturing year |
| `mileage_km` | `integer` | No | 0 ≤ x ≤ 1,000,000 | Odometer reading |
| `spec` | `string` | No | "GCC", "US", "Japan", "European" | Vehicle specification |
| `trim` | `string` | No | — | e.g. "VXR" |
| `city` | `string` | No | — | e.g. "Dubai" |
| `country` | `string` | No | "AE", "SA", "QA", "KW", "BH", "OM" | GCC country code |
| `asking_price` | `float` | No | > 0 | Price to evaluate for deal indicator |

**Example:**
```json
{
  "make": "Toyota",
  "model": "Land Cruiser",
  "year": 2018,
  "mileage_km": 120000,
  "spec": "GCC",
  "trim": "VXR",
  "city": "Dubai",
  "country": "AE",
  "asking_price": 130000
}
```

**Validation:** Pydantic model validation at the framework level. Invalid JSON, missing required fields, or out-of-range values return **422 Unprocessable Entity** with FastAPI's default error detail.

---

#### Response

**Success: `200 OK`**

**Schema:** `ValuationResponse`

| Field | Type | Description |
|-------|------|-------------|
| `estimate` | `float` | Point estimate in AED |
| `price_low` | `float` | 10th percentile of comps |
| `price_high` | `float` | 90th percentile of comps |
| `confidence` | `string` | `"high"`, `"medium"`, `"low"` |
| `comp_count` | `integer` | Number of comparable listings found |
| `segment_median` | `float` | Raw median of comps before adjustments |
| `comps` | `array[CompSummary]` | Up to 10 comps with platform attribution |
| `adjustments` | `array[Adjustment]` | Price adjustments applied |
| `confidence_interval_80` | `[float, float] \| null` | Bootstrap 80% CI |
| `knowledge` | `Knowledge \| null` | Vehicle knowledge base info |
| `deal_indicator` | `string \| null` | `"great_deal"`, `"fair_deal"`, `"above_market"` |
| `deal_description` | `string \| null` | Human-readable deal verdict |

**CompSummary:**
```json
{
  "price_aed": 125000.0,
  "year": 2018,
  "mileage_km": 115000,
  "spec": "GCC",
  "city": "Dubai",
  "country": "AE",
  "status": "active",
  "found_on": "Found on Dubizzle UAE, Dubai",
  "platform": "Dubizzle UAE",
  "relevance_score": 92.5
}
```

**Adjustment:**
```json
{
  "reason": "mileage",
  "amount": -5200.0,
  "detail": "Your car has 20,000 km more than segment average. Adjustment: -5,200 AED"
}
```

**Knowledge:**
```json
{
  "generation": null,
  "known_issues": [],
  "annual_maintenance_estimate": null,
  "market_liquidity": null
}
```

**⚠️ Knowledge is always empty.** The `Knowledge()` object is constructed with all defaults — the knowledge base tables (`car_specs`, `car_issues`, `maintenance_costs`) are never queried during valuation.

**Full response example:**
```json
{
  "estimate": 125000.0,
  "price_low": 112000.0,
  "price_high": 145000.0,
  "confidence": "high",
  "comp_count": 34,
  "segment_median": 122000.0,
  "comps": [...],
  "adjustments": [
    {"reason": "mileage", "amount": -5200.0, "detail": "..."},
    {"reason": "spec", "amount": 15000.0, "detail": "GCC spec premium: +15,000 AED"},
    {"reason": "city", "amount": 3000.0, "detail": "Dubai market adjustment: +3,000 AED"}
  ],
  "confidence_interval_80": [118000.0, 132000.0],
  "knowledge": {
    "generation": null,
    "known_issues": [],
    "annual_maintenance_estimate": null,
    "market_liquidity": null
  },
  "deal_indicator": "great_deal",
  "deal_description": "This car is priced below the market range (130,000 vs 112,000–145,000 AED)."
}
```

---

#### Error Responses

| Status | Condition |
|--------|-----------|
| `422 Unprocessable Entity` | Invalid input (Pydantic validation failure) |
| `422 Unprocessable Entity` | Insufficient comps: `{"detail": "Not enough comparable listings for this vehicle. Try a more common make/model or broader criteria."}` |
| `429 Too Many Requests` | Rate limit exceeded (10/min) |

**Note:** If `confidence == "insufficient"` (fewer than 5 comps), the endpoint returns **422**, not 200 with a low-confidence result. This is a design choice — the blueprint says to return 200 with `confidence: "insufficient"`, but the implementation rejects the request entirely.

---

#### Cache Behavior

| Aspect | Detail |
|--------|--------|
| **Cache key** | `SHA256(make|model|year|mileage|spec|trim|city|country|YYYY-MM-DD)` |
| **TTL** | Same calendar day (key includes date) |
| **Storage** | `valuation_queries` table |
| **Cache hit** | Returns full `ValuationResponse` from stored data |
| **Cache miss** | Computes fresh valuation, stores in `valuation_queries`, returns response |
| **Cache hit limitations** | Returns empty `comps: []`, `adjustments: []`, `confidence_interval_80: null`, `deal_indicator: null`, `deal_description: null` — only the estimate/price_low/price_high/confidence/comp_count fields are restored |

---

#### Processing Pipeline

```
1. Compute cache_key (SHA-256 of inputs + today's date)
2. Check valuation_queries table for cache_key
3. If cache hit → return cached result (degraded — no comps/adjustments)
4. If cache miss:
   a. Call engine.statistical.valuate()
      ├── find_comps() — tiered hard filters
      ├── Percentile computation (P10, P25, P50, P75, P90)
      ├── Mileage adjustment (0.25 AED/km × delta from comp median)
      ├── Spec adjustment (50% of GCC/non-GCC premium)
      ├── City adjustment (30% of same-city/different-city premium)
      ├── Bootstrap 80% CI (1000 iterations)
      └── Confidence scoring (high/medium/low/insufficient)
   b. If confidence == "insufficient" → 422 error
   c. Compute deal_indicator (only if asking_price provided)
   d. Store result in valuation_queries table
   e. Return ValuationResponse
```

---

### 3.4 `POST /v1/valuate-url` — URL-Based Valuation

```
POST /v1/valuate-url
```

**Router:** `routes/url_valuate.py`

**Description:** Accepts a car listing URL, fetches the page with browser-like headers, parses vehicle details using source-specific or generic parsers, normalizes the data, and returns a valuation.

**Rate Limit:** None (no `@limiter.limit` decorator)

**Auth:** None

---

#### Request

**Content-Type:** `application/json`

**Schema:** `URLValuationRequest` (inline Pydantic model)

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `url` | `string` | ✅ Yes | Valid URL | Car listing URL |
| `asking_price` | `float` | No | — | Override extracted price |

```json
{
  "url": "https://uae.dubizzle.com/motors/used-cars/toyota/land-cruiser/2025/1/15/some-listing-123456/",
  "asking_price": null
}
```

---

#### Response

**Success: `200 OK`**

**Schema:** Inline dict (not a Pydantic model — returned as raw dict)

```json
{
  "parsed_from_url": {
    "make": "Toyota",
    "model": "Land Cruiser",
    "year": 2018,
    "mileage_km": 120000,
    "spec": "GCC",
    "city": "Dubai",
    "country": "AE",
    "price_found": 130000.0
  },
  "estimate": 125000.0,
  "price_low": 112000.0,
  "price_high": 145000.0,
  "confidence": "high",
  "comp_count": 34,
  "segment_median": 122000.0,
  "adjustments": [
    {"reason": "mileage", "amount": -5200.0, "detail": "..."}
  ],
  "comps": [...],
  "confidence_interval_80": [118000.0, 132000.0]
}
```

---

#### Error Responses

| Status | Condition |
|--------|-----------|
| `422 Unprocessable Entity` | URL cannot be fetched (network error, DNS failure, timeout) |
| `422 Unprocessable Entity` | Site is blocking automated access (Cloudflare, captcha detected) |
| `422 Unprocessable Entity` | Could not extract car details from the page |
| `422 Unprocessable Entity` | Insufficient comps for valuation |

**Anti-bot detection message format:**
```json
{
  "detail": "Dubizzle is blocking automated access with bot protection. Please use the manual entry form instead — it works for any car listing."
}
```

The endpoint detects these blocking indicators in the HTML:
- `pardon our interruption`
- `cf-browser-verify`
- `captcha`
- `access denied`
- `are you a robot`
- `verify you are human`
- `blocked`
- `cloudflare`
- `ddos-guard`

Site name is extracted from URL domain and mapped to human-readable brand names.

---

#### Processing Pipeline

```
1. fetch_url(url) — httpx with Chrome 131 headers, 20s timeout
2. Check for anti-bot page indicators → 422 if blocked
3. parse_listing_from_html_smart(html, url):
   a. Try Dubizzle UAE parser (if dubizzle in URL)
   b. Try YallaMotor scraper parse (if yallamotor in URL)
   c. Try Haraj KSA scraper parse (if haraj in URL)
   d. Fall back to generic parser:
      - Extract make/model from <h1>/<title>/heading classes
      - Extract year via regex (1990–current_year)
      - Extract mileage via /\d[\d,]*\s*km/i
      - Extract price via CSS selectors + meta tags
      - Detect spec (GCC/US/Japan) in English and Arabic
      - Match city from hardcoded list
      - Infer country from URL domain
      - Ultra-lenient fallback: Toyota Camry 2020, 100K AED
4. normalize_listing() — canonical forms, currency conversion
5. valuate() — same statistical engine as /v1/valuate
6. Return parsed details + valuation
```

---

#### Valuation Error Safety

The valuation step is wrapped in try/except — if valuation fails, it returns 422 rather than a 500:
```python
except Exception as e:
    raise HTTPException(status_code=422, detail=f"Error processing valuation: {str(e)[:200]}")
```

---

### 3.5 `GET /v1/models` — List Makes

```
GET /v1/models[?country={code}]
```

**Router:** `routes/models.py`

**Description:** Lists all distinct makes in the database with model and listing counts, optionally filtered by country.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | `string` | No | ISO country code: AE, SA, QA, KW, BH, OM |

---

#### Response

**Success: `200 OK`**

```json
{
  "makes": [
    {
      "make": "Toyota",
      "model_count": 7,
      "listing_count": 1250
    },
    {
      "make": "Nissan",
      "model_count": 3,
      "listing_count": 480
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `make` | `string` | Make name (title case) |
| `model_count` | `integer` | Distinct models for this make |
| `listing_count` | `integer` | Total listings for this make |

**Filtering:** Only includes listings where `quality_score >= 60`.

**Ordering:** Alphabetical by make name.

---

### 3.6 `GET /v1/models/{make}` — List Models for Make

```
GET /v1/models/{make}[?country={code}]
```

**Router:** `routes/models.py`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `make` | `string` | Make name, e.g. "Toyota" |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | `string` | No | ISO country code filter |

---

#### Response

**Success: `200 OK`**

```json
{
  "make": "Toyota",
  "models": [
    {
      "model": "Land Cruiser",
      "year_range": "2010–2024",
      "listing_count": 350
    },
    {
      "model": "Camry",
      "year_range": "2015–2024",
      "listing_count": 280
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `model` | `string` | Model name |
| `year_range` | `string` | e.g. "2010–2024" (min year – max year) |
| `listing_count` | `integer` | Total listings for this make+model |

---

### 3.7 `GET /v1/models/{make}/{model}` — List Years & Trims

```
GET /v1/models/{make}/{model}[?country={code}]
```

**Router:** `routes/models.py`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `make` | `string` | Make name |
| `model` | `string` | Model name |

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country` | `string` | No | ISO country code filter |

---

#### Response

**Success: `200 OK`**

```json
{
  "make": "Toyota",
  "model": "Land Cruiser",
  "years": [
    {
      "year": 2024,
      "listing_count": 45,
      "trims": ["VXR", "GXR", "EXR"]
    },
    {
      "year": 2023,
      "listing_count": 52,
      "trims": ["VXR", "GXR"]
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `year` | `integer` | Model year |
| `listing_count` | `integer` | Total listings for this make+model+year |
| `trims` | `array[string]` | Distinct trim levels found |
| `avg_price` | `float` (computed but not returned) | Average `normalized_price_aed` for the year+trim |

**⚠️ Note:** The SQL computes `avg_price` via `func.avg(Listing.normalized_price_aed)` but the response only includes `year`, `listing_count`, and `trims`. The average price is not exposed in the response body.

**Ordering:** Years descending (newest first).

---

### 3.8 `GET /v1/admin/stats` — Platform Statistics

```
GET /v1/admin/stats
```

**Router:** `routes/admin.py`

**Description:** Overall platform statistics — listing counts, valuation volume, last pipeline run, unacknowledged drift events.

**Auth:** ⚠️ **None** — should be admin-only but has no auth guard.

---

#### Response

**Success: `200 OK`**

```json
{
  "listings": {
    "total": 15230,
    "active": 11800
  },
  "valuations": {
    "total": 4500,
    "last_7_days": 320
  },
  "last_pipeline_run": {
    "source": "dubizzle_uae",
    "started_at": "2026-07-11T02:00:00+04:00",
    "completed_at": "2026-07-11T02:45:00+04:00",
    "success": true,
    "records_ingested": 1250
  },
  "unacknowledged_drifts": 2,
  "api_version": "v1"
}
```

**Queries executed:**
1. `COUNT(*) FROM listings` → total
2. `COUNT(*) FROM listings WHERE status = 'active'` → active
3. `COUNT(*) FROM valuation_queries` → total valuations
4. `COUNT(*) FROM valuation_queries WHERE queried_at >= NOW() - 7 days` → recent
5. `SELECT ... FROM pipeline_runs ORDER BY started_at DESC LIMIT 1` → last run
6. `COUNT(*) FROM drift_events WHERE acknowledged = false AND threshold_exceeded = true` → active drifts

---

### 3.9 `GET /v1/admin/scrapers` — Scraper Health

```
GET /v1/admin/scrapers
```

**Router:** `routes/admin.py`

**Description:** Health status of all scrapers — last run time and staleness check.

**Auth:** ⚠️ **None** — should be admin-only.

---

#### Response

**Success: `200 OK`**

```json
{
  "scrapers": [
    {
      "source": "dubizzle_uae",
      "last_run": "2026-07-11T02:45:00+04:00",
      "hours_since_last_run": 28.3,
      "status": "healthy"
    },
    {
      "source": "haraj_ksa",
      "last_run": "2026-07-09T18:00:00+04:00",
      "hours_since_last_run": 61.0,
      "status": "stale"
    }
  ]
}
```

**Staleness threshold:** > 36 hours since last run → `"stale"`. ≤ 36 hours → `"healthy"`.

**Query:** Groups `scraper_health` by source, takes most recent `captured_at` per source, orders by recency.

---

### 3.10 `GET /v1/admin/quality` — Quality Metrics

```
GET /v1/admin/quality
```

**Router:** `routes/admin.py`

**Description:** Data quality score distribution across all listings.

**Auth:** ⚠️ **None** — should be admin-only.

---

#### Response

**Success: `200 OK`**

```json
{
  "total_listings": 15230,
  "quality_distribution": {
    "high_quality": 9800,
    "medium_quality": 4200,
    "low_quality": 1230
  },
  "high_quality_pct": 64.3
}
```

**Buckets:**
- **high_quality:** `quality_score >= 80`
- **medium_quality:** `60 <= quality_score < 80`
- **low_quality:** `quality_score < 60`

---

## 4. Common Concerns

### 4.1 Authentication & Authorization

| Issue | Detail |
|-------|--------|
| **No auth on any endpoint** | JWT tokens and API keys are implemented in `src/auth/jwt.py` but never required by any route as a `Depends()` |
| **Admin endpoints exposed** | `/v1/admin/*` returns operational data (listing counts, scraper health, pipeline runs) to unauthenticated callers |
| **user_id never populated** | `ValuationQuery.user_id` and `ValuationQuery.ip_hash` are always NULL — no user tracking middleware exists |
| **Blueprint-specified tiers** | Blueprint §10.2 specifies anonymous/registered/enterprise tiers with different rate limits. Only anonymous (10/min) is implemented. |

### 4.2 Rate Limiting

| Endpoint | Limit | Implementation |
|----------|-------|---------------|
| `POST /v1/valuate` | 10/min | `@limiter.limit("10/minute")` |
| All others | None | No decorator |

**⚠️ In-memory counters.** slowapi uses in-memory storage. Behind a load balancer with multiple API instances, rate limits are per-instance, not global. Requires Redis for multi-instance deployments.

### 4.3 Input Validation

| Layer | Mechanism |
|-------|-----------|
| Pydantic model validation | `ValuationRequest` enforces types, ranges, required fields |
| FastAPI path/query parsing | Automatic type coercion for path and query params |
| Pandera (pipeline layer) | `ListingSchema` validates scraped data before DB insertion — not used at API level |
| No sanitization | User input is stored as-is in `valuation_queries`; no XSS/HTML sanitization (not needed for API, relevant if rendered in UI) |

### 4.4 Error Response Patterns

| Status | Pattern | Used By |
|--------|---------|---------|
| `200` | Success (even for degraded — see `/v1/health`) | health |
| `422` | Business logic errors (insufficient comps, blocked site, parse failure) | valuation, url_valuate |
| `422` | Pydantic validation errors (FastAPI default) | valuation (request body) |
| `429` | Rate limit exceeded (slowapi) | valuation |
| `404` | UI file not found | `/` (serve UI) |

**No 500 errors are intentionally raised** — all error paths in route handlers catch exceptions and return 422. However, unhandled exceptions in middleware or dependencies would still produce 500s.

### 4.5 Response Schema Consistency

| Issue | Detail |
|-------|--------|
| **Inconsistent response types** | `/v1/valuate` returns a Pydantic `ValuationResponse`; `/v1/valuate-url` returns a raw dict with overlapping but different shape |
| **Missing schema for URL valuation** | `URLValuationRequest` is defined inline in `url_valuate.py`, not in `schemas/` |
| **Cache hit degradation** | Cached responses from `/v1/valuate` return `comps: []`, `adjustments: []`, `confidence_interval_80: null` — a different shape than fresh responses |
| **Knowledge always empty** | `Knowledge()` is constructed with all defaults and never populated from the knowledge base |

---

## 5. Dependencies (per-endpoint)

| Endpoint | DB Session | Rate Limiter | External HTTP | Notes |
|----------|-----------|-------------|---------------|-------|
| `GET /` | No | No | No | File read only |
| `GET /v1/health` | Yes | No | No | `SELECT 1` |
| `POST /v1/valuate` | Yes | Yes (10/min) | No | Reads `valuation_queries` + `listings`; writes `valuation_queries` |
| `POST /v1/valuate-url` | Yes | No | **Yes** (httpx to listing URL) | Fetches external page; reads `listings` for comps |
| `GET /v1/models` | Yes | No | No | Reads `listings` aggregated |
| `GET /v1/models/{make}` | Yes | No | No | Reads `listings` aggregated |
| `GET /v1/models/{make}/{model}` | Yes | No | No | Reads `listings` aggregated |
| `GET /v1/admin/stats` | Yes | No | No | Reads `listings`, `valuation_queries`, `pipeline_runs`, `drift_events` |
| `GET /v1/admin/scrapers` | Yes | No | No | Reads `scraper_health` |
| `GET /v1/admin/quality` | Yes | No | No | Reads `listings` |

---

## 6. Blueprint Compliance

| Blueprint Spec (§9.1) | Status | Notes |
|------------------------|--------|-------|
| `POST /v1/valuate` | ✅ Complete | + Good Deal indicator (not in blueprint) |
| `GET /v1/valuate/{id}` | ❌ Missing | Retrieve cached valuation by ID |
| `GET /v1/models` | ✅ Complete | + country filter (not in blueprint) |
| `GET /v1/models/{make}` | ✅ Complete | + country filter |
| `GET /v1/models/{make}/{model}` | ✅ Complete | + country filter |
| `GET /v1/trends` | ❌ Missing | Market trends with segment query params |
| `GET /v1/health` | ✅ Complete | |
| `GET /v1/stats` | ⚠️ Redirected | Blueprint specifies `/v1/stats`; implemented as `/v1/admin/stats` |
| API versioning (`/v1/`) | ✅ Complete | |
| Idempotent cache keys | ✅ Complete | SHA-256, date-scoped, 24h TTL |
| Rate limiting | ⚠️ Partial | Only anonymous tier (10/min); registered and enterprise tiers not implemented |
| Audit logging middleware | ❌ Missing | Blueprint §10.6 specifies middleware logging every request |

**Unexpected endpoints (not in blueprint):**
- `POST /v1/valuate-url` — URL paste valuation
- `GET /v1/admin/scrapers` — Scraper health
- `GET /v1/admin/quality` — Quality metrics distribution
- `GET /` — UI serving

---

## 7. Security Assessment

| Finding | Severity | Detail |
|---------|----------|--------|
| Admin endpoints unauthenticated | **High** | `/v1/admin/*` returns operational data to anyone |
| No auth on any endpoint | **Medium** | JWT/API key logic exists but not wired |
| In-memory rate limiting | **Medium** | Won't work across multiple API instances |
| External URL fetch (SSRF risk) | **Medium** | `/v1/valuate-url` fetches arbitrary URLs via httpx — could be used to probe internal services |
| JWT secret hardcoded default | **High** | `"dev-secret-change-in-production-gcc-car-value-2026"` in `config.py` |
| No input size limits | **Low** | No max body size configured; URL param has no length validation |
| CORS allows all methods/headers | **Low** | Configured for specific origins but `allow_methods=["*"]` and `allow_headers=["*"]` |

---

## 8. Recommendations

### Critical
1. **Add authentication to admin endpoints** — `GET /v1/admin/*` needs JWT or API key guard
2. **Wire auth into valuation endpoints** — Populate `user_id` from JWT; enforce tier-based rate limits
3. **Validate JWT secret at startup** — Refuse to start with default dev secret in production

### High
4. **Implement `GET /v1/valuate/{id}`** — Retrieve cached valuation (blueprint spec)
5. **Implement `GET /v1/trends`** — Market trends endpoint (blueprint spec)
6. **Wire knowledge base into `/v1/valuate` response** — Query `car_specs`, `car_issues`, `maintenance_costs`
7. **Add audit logging middleware** — Log all requests per blueprint §10.6
8. **Add URL length validation** — Cap URL param at reasonable length for `/v1/valuate-url`
9. **Consistent error schema** — Use a standard error response model across all endpoints

### Medium
10. **Fix cache hit response degradation** — Return full response (comps, adjustments) from cache, or at minimum indicate it's a cached response
11. **Add `avg_price` to `/v1/models/{make}/{model}` response** — Already computed but dropped
12. **Add rate limiting to `/v1/valuate-url`** — Currently unlimited
13. **Add request timeout to external fetch** — `/v1/valuate-url` has 20s timeout on httpx but no overall request timeout
14. **Create `URLValuationRequest` in schemas** — Move from inline definition to `schemas/`

---

*API audit completed 2026-07-12. No production code modified.*
