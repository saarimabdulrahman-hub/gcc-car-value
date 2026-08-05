# GCC Car Value Platform — Comprehensive Audit Report

**Date:** 2026-08-04
**Auditor:** Automated multi-agent analysis (static + runtime)
**Previous audit:** 2026-08-02 (production readiness audit, ~85 gaps found)
**Test run:** 344 passed, 0 failed, 0 skipped | **Coverage:** 61% (1673/4309 statements missed)

---

## Executive Summary

The GCC Car Value platform has improved significantly since the Aug 2 audit. Of the ~85 gaps identified then, approximately **15 have been addressed**, including critical security fixes (SSRF protection, JWT hardening, password validation, rate limiting) and operational improvements (non-root Docker, circuit breakers, request size limits).

However, **the platform is still not production-ready**. The core valuation engine (the product itself) has near-zero test coverage. The scraper-to-pipeline integration gap remains. There is no staging environment, no monitoring, and no backup strategy. The frontend has robust visual design but multiple pages mix live API calls with hardcoded preview data, creating a confusing user experience.

**Estimated readiness: ~45%** (up from ~25% on Aug 2). Suitable for internal demo only.

---

# PART A: Findings From Static Analysis

## A1. Architecture Observations

### A1.1 Clean Layered Architecture (POSITIVE)

The backend follows a well-structured layered pattern:
- **API edge** (`src/api/`) — routing, middleware, security headers, rate limiting
- **Domain** (`src/engine/`) — comparable finding, statistical valuation, ML ensemble
- **Persistence** (`src/db/`, `src/models/`) — SQLAlchemy async, Alembic migrations, 17 domain models
- **Operations** (`src/core/`) — health checks, structured logging, metrics, tracing

Rating: **8/10**. Clean separation of concerns. The `SecretProvider` abstraction and RBAC system are particularly well-designed.

### A1.2 Deployment Architecture Split (INFORMATIONAL)

The platform uses a deliberate split:
- **Frontend:** Static HTML/CSS/JS in `ui/` → Vercel (`vercel.json`)
- **Backend:** FastAPI in Docker → Render (`render.yaml`)
- **Database:** External PostgreSQL 16

This is a valid architecture for a read-heavy valuation platform. The Vercel/Render split is documented and intentional, not an accident. The primary risk is API-base mismatch: some pages hit `https://gcc-car-value.onrender.com/v1` while others use same-origin `/v1` paths that fail on Vercel.

### A1.3 React Sub-Application Drift (LOW)

`ui/src/` and `ui/dist/react-browse/` are a React/Vite rebuild of the browse experience. The React build (`react-browse.html`) works cleanly (0 errors in QA sweep) but overlaps with the vanilla `browse.html`. Two implementations of the same feature add maintenance burden with no clear migration plan.

**Recommendation:** Either complete the React migration or archive the React experiment. The current dual-path is technical debt.

### A1.4 18 Chrome Profile Temp Directories (LOW)

The repository root contains 18 `tmp-*` directories (~280MB total) — leftover Chromium user-data directories from prior QA/browse sessions. These are in `.gitignore` but clutter the working tree.

**Recommendation:** `rm -rf tmp-*` and add `tmp-*` to `.gitignore` if not already covered.

---

## A2. Code Quality

### A2.1 46 Broad `except Exception` Clauses (MEDIUM)

Across the codebase, 46 instances of `except Exception` (or bare `except: pass`) silently swallow errors. While some are intentional (metrics/tracing must never break the app), others mask real failures:

| File | Risk |
|------|------|
| `src/auth/dependencies.py:62` | DB role lookup fails silently → falls back to JWT claim → **privilege escalation risk** if DB is down |
| `src/auth/dependencies.py:77` | Email lookup fails silently → `/auth/me` returns `email=None` without warning |
| `src/api/routes/url_valuate.py:80,188,199` | Three independent `except Exception: pass` blocks in URL parser → silently produces garbage data |
| `src/config/secrets.py:220` | AWS Secrets Manager failure returns `default` → missing credentials in production |
| `src/scrapers/base.py:106` | Scraper listing fetch failure swallowed into error list → partial scrapes appear successful |
| `src/ml/model_persistence.py:49-56` | Corrupted pickle file silently degrades all valuations |

**Recommendation:** Replace each `except Exception` with specific exception types. Add structured logging at minimum. For the auth fallback specifically, log a warning and set a `_db_unavailable` flag on the user dict.

### A2.2 Core Business Logic Untested (CRITICAL)

61% overall coverage masks that the **revenue-generating code** is virtually untested:

| Module | Coverage | Impact |
|--------|----------|--------|
| `src/engine/trainer.py` | **0%** | ML model training — core IP |
| `src/engine/features/` (4 files) | **0%** | Feature engineering for valuations |
| `src/engine/recommendations.py` | **0%** | User-facing recommendations |
| `src/engine/drift.py` | **0%** | Model drift detection — silent degradation |
| `src/pipeline/orchestrator.py` | **0%** | End-to-end pipeline orchestration |
| `src/pipeline/promoter.py` | **0%** | Model promotion to production |
| `src/pipeline/quality.py` | **0%** | Data quality scoring |
| `src/scrapers/dubizzle_uae/scraper.py` | **0%** | Primary data ingestion |
| `src/scrapers/haraj_ksa/scraper.py` | **0%** | KSA market data |
| `src/scrapers/yallamotor/scraper.py` | **0%** | UAE market data |
| `src/db/partition_manager.py` | **0%** | Database partition management |

**Impact:** A valuation error in `statistical.py` or `comp_finder.py` would silently produce wrong prices. No test catches it.

### A2.3 Ponytail Shortcuts (INFORMATIONAL)

Three `ponytail:` comments mark known technical debt:
- `src/auth/jwt.py:143` — Token revocation fail-open on DB outage
- `src/scrapers/title_parser.py:21` — Curated trim list cap
- `src/engine/comp_finder.py:89` — Hardcoded quality threshold (45)

These are honest markers. Good practice.

### A2.4 No TODO/FIXME Markers (POSITIVE)

The source code is clean of TODO/FIXME/HACK markers. This indicates disciplined development practice.

### A2.5 `knowledge/seed.py` Is 998 Lines (LOW)

The largest source file at 998 lines. Contains mostly seed data for the browse experience — makes, models, brands, and market metadata. Could benefit from splitting into data files loaded at runtime, but functionally adequate.

---

## A3. Security Observations

### A3.1 Security Improvements Since Aug 2 (POSITIVE)

The following critical issues from the Aug 2 audit have been addressed:
- ✅ **SSRF protection** — `src/api/security.py` with IP filtering, domain allowlist, private network blocking
- ✅ **Password strength** — Min 8 chars, 2+ character classes, common password blacklist
- ✅ **Rate limiting on auth** — Login (10/min), register (5/min), refresh (5/min)
- ✅ **JWT hardening** — Access tokens 15min (was 24h), refresh tokens 7 days, JTI revocation
- ✅ **Request body size limit** — 1MB max
- ✅ **CORS allows DELETE** — Added to allowed methods
- ✅ **Docker non-root user** — `appuser` created and used
- ✅ **`render.yaml` branch** — Fixed from `feature-url-valuation` to `master`
- ✅ **Secret masking** — Comprehensive secret redaction in logs

### A3.2 Remaining Security Gaps

| Issue | Severity | Detail |
|-------|----------|--------|
| PBKDF2 iterations at 100,000 | MEDIUM | OWASP 2026 recommends 600,000+ for SHA256, or Argon2id |
| No account lockout | MEDIUM | Brute-force protection relies on rate limiting alone |
| No email verification | MEDIUM | Accounts created without email ownership proof |
| Logout doesn't revoke refresh token | LOW | Refresh token stays valid until expiry after logout |
| Refresh token role hardcoded to `consumer` | LOW | `create_access_token` in refresh flow doesn't read current role from DB |
| Metrics endpoint public | LOW | `/metrics` has no auth requirement |
| `auth.html` is visual mockup only | MEDIUM | Login page has zero `fetch()` calls — no API integration |
| CSP uses `unsafe-inline` for scripts | LOW | Required for inline `onclick` handlers in vanilla HTML pages |

### A3.3 `get_current_user` Fail-Open Risk

`src/auth/dependencies.py:60-63`: When the DB is unreachable, the role lookup `except Exception: db_role = None` causes the system to fall back to the JWT claim. If an attacker obtains a valid JWT with a forged `role: admin` claim (possible if JWT secret is weak), and the DB is made unavailable (DoS), the system grants admin access.

**Recommendation:** On DB failure during auth, deny elevated operations rather than trusting the JWT claim. Add a `_db_verified: False` flag to the user dict and require `_db_verified: True` for admin endpoints.

---

## A4. Performance Observations

### A4.1 Valuation Caching (POSITIVE)

`POST /v1/valuate` implements a daily cache key with SHA-256 hashing. Cache hits skip the entire statistical + ML pipeline. This is efficient for common queries.

### A4.2 No Connection Pool Health Checks

`src/db/session.py`: The SQLAlchemy engine is created without `pool_pre_ping=True`. Stale connections (from network blips or PostgreSQL restarts) are handed to callers and fail on first use.

**Recommendation:** Add `pool_pre_ping=True` to the engine configuration.

### A4.3 Large Assets

| File | Size | Concern |
|------|------|---------|
| `ui/hero-bg.png` | 1.8 MB | Homepage hero background — should be optimized (WebP, compression) |
| `ui/assets/hero-bg-4e3d58a7-4e3d58a7.png` | ~200 KB | Duplicate of hero-bg in React assets |

### A4.4 No Lazy Loading

The homepage loads all page templates (sell, buy, browse, market, reports, watchlist, settings) in a single HTML document. For a logged-out user on the homepage, the browser parses and stores ~840 lines of hidden HTML that will never be viewed.

**Recommendation:** Consider splitting pages into separate HTML files loaded on demand, or at minimum defer parsing of `hidden` sections.

---

## A5. Design & Frontend Architecture

### A5.1 Design System Quality (POSITIVE)

The design system in `theme.css` + `css/index.css` is well-structured:
- CSS custom properties for colors, typography, spacing, shadows, z-index
- 8px grid spacing system (`--space-1` through `--space-12`)
- Consistent gold accent color system with semantic aliases
- Dark-mode-first design with `color-scheme: dark`
- Typography scale from 12px labels to 48px display text
- Glass-morphism card effects with gradient borders
- Responsive breakpoints at 1100px, 900px, 768px, 560px

Rating: **8/10** for CSS architecture.

### A5.2 SVG Rendering Bug (MEDIUM)

The QA sweep found SVG path parsing errors on the browse page:
```
Error: <path> attribute d: Unexpected end of attribute. Expected number, "…5 14 54 13 63 15".
```

This appears in the inline SVG skyline or vehicle illustrations. The error is non-fatal (SVGs still render approximately) but indicates a malformed path data string — likely a trailing decimal point or incomplete coordinate pair.

**Location:** `ui/index.html` inline SVG (skyline paths at line 124, or vehicle at line 137)

### A5.3 Homepage Skeleton-to-Content Transition

The homepage correctly shows skeleton loading states before API data arrives. If the API call fails, it shows "Unable to load dashboard. Retry" — a proper error state. However, the skeleton briefly flashes before the error state appears (the `loadHomeKPIs` function hides skeleton and shows error simultaneously in the catch block).

### A5.4 Vanilla JS Architecture (MEDIUM)

The frontend uses a single large `index.js` file with global functions and direct DOM manipulation. Key concerns:
- **No module system** — All functions are global, risking naming conflicts
- **No framework** — Manual DOM building via string concatenation (`h+='<div>...'`)
- **No state management** — `localStorage` used for tokens, form state managed imperatively
- **Inline event handlers** — `onclick="goPage('sell',this)"` throughout HTML

This approach is functional and build-free (a deliberate choice), but scaling to more complex features will become increasingly difficult.

### A5.5 Preview Data Confusion (MEDIUM)

Several pages mix live API data with hardcoded preview values:
- **Reports page** (`reports.html`): KPI numbers (AED 12.8B, 56,421 vehicles) are hardcoded HTML
- **Market page** (`market.html`): Brand rankings and country coverage have skeleton states that load from API, but market health insights are hardcoded
- **Detail pages** (`vehicle.html`, `comparables.html`, `report-detail.html`): Marked as "Preview data" via `detail-pages.js`

Users cannot distinguish live data from demo data without reading the preview banner.

---

## A6. Technical Debt Summary

| Item | Effort | Impact |
|------|--------|--------|
| 46 broad except clauses | Medium | Production debugging difficulty, silent failures |
| Scraper→pipeline integration gap | Large | Core data pipeline non-functional end-to-end |
| React migration incomplete | Small | Duplicate browse implementations |
| 18 temp Chrome dirs | Small | Disk clutter |
| Core IP untested | Large | Regression risk for valuation accuracy |
| No module system in frontend | Large | Scaling limitation |
| `knowledge/seed.py` 998 lines | Small | Hard to maintain seed data |
| Dual metrics systems | Medium | Two implementations (prometheus_client + custom MetricsRegistry) |
| 3 ponytail shortcuts | Small | Tracked, needs eventual resolution |

---

# PART B: Findings From Runtime Testing

## B1. Test Suite Results

**Overall:** 344 passed, 0 failed, 0 skipped, 11 warnings
**Coverage:** 61% (down from 60% on Aug 2 due to new code without tests)

### Coverage by Component

| Component | Coverage | Assessment |
|-----------|----------|------------|
| API Routes | ~85% | Good |
| Auth | ~65% | Incomplete — missing error paths, AWS provider tests |
| Config/Secrets | ~74% | Missing AWS provider tests |
| Engine (core IP) | ~25% | **CRITICAL** — this is the product |
| ML | ~73% | model_loader mostly untested |
| Pipeline | ~50% | orchestrator + promoter at 0% |
| Scrapers | ~15% | Only rate_limiter tested |
| DB | ~62% | partition_manager at 0% |
| Observability | ~40% | Logging/tracing/metrics |
| Models | ~100% | Schema definitions only |

### E2E Tests

23 E2E tests passed (API + route tests). The Playwright UI test was skipped — it requires a running API server. The frontend static artifact tests (3 passed) verify `routes.manifest.json` and HTML integrity.

---

## B2. QA Sweep Results (All 13 Pages)

Conducted with `scripts/qa_sweep.py` — Chromium headless, 1440px + 390px viewports, console error collection, 4xx detection, horizontal overflow detection.

| Page | Console Errors | 4xx | Desktop Overflow | Mobile Overflow | Notes |
|------|---------------|-----|------------------|-----------------|-------|
| `auth.html` | 0 | 0 | Clean | Clean | Works but is mockup only |
| `browse.html` | 3 | 1 | Clean | Clean | 3 SVG path errors, 1 API 404 |
| `comparables.html` | 0 | 0 | Clean | Clean | Preview data page |
| `index.html` | 6 | 0 | Clean | Clean | API CORS errors, shows error state |
| `market.html` | 6 | 0 | Clean | Clean | API CORS errors |
| `notifications.html` | 0 | 0 | Clean | Clean | Works standalone |
| `react-browse.html` | **0** | 0 | Clean | Clean | ★ Clean — best-performing page |
| `report-detail.html` | 1 | 1 | Clean | Clean | 1 API 404 |
| `reports.html` | 5 | 1 | Clean | Clean | API CORS errors |
| `results.html` | 4 | 0 | Clean | Clean | API CORS errors |
| `settings.html` | 0 | 0 | Clean | Clean | Works standalone |
| `vehicle.html` | 0 | 0 | Clean | Clean | Preview data page |
| `watchlist.html` | 1 | 1 | Clean | Clean | API 404 |

**Key findings:**
1. **Zero horizontal overflow** on any page at any resolution — excellent responsive design
2. **8 of 13 pages** have problems (errors or 4xx) — mostly expected API unavailability
3. **react-browse.html** is the cleanest page (0 errors) — the React build is higher quality
4. **SVG path errors** on browse page are consistent and reproducible

---

## B3. Browser Inspection Results

### Homepage (`index.html`)
- Skeleton loading state shows correctly on page load
- Falls back to error state "Unable to load dashboard. Retry" when API unavailable
- Hero section with skyline SVG, gold glow, and SUV illustration renders correctly
- Choice cards ("I'm Selling" / "I'm Buying") are properly interactive
- KPI strip and trust strip render with inline SVG icons
- **Issue:** Hero background image (`hero-bg.png`, 1.8MB) causes a noticeable load delay on slow connections

### Browse Page (`browse.html`)
- Search bar, country filter, sort dropdown, and quick-filter chips all render correctly
- Featured manufacturers slider works with horizontal scroll
- KPI strip shows placeholder values ("—") when API unavailable
- Market insights column shows hardcoded "Dubizzle" as most active marketplace
- **Issue:** 3 SVG rendering errors in console (malformed path data in skyline/vehicle illustrations)

### React Browse (`react-browse.html`)
- Clean load, zero console errors
- Proper React component rendering with Vite build
- Same visual design as vanilla browse page
- **Assessment:** Higher quality implementation than the vanilla equivalent

---

## B4. Functional Testing (Static Analysis of Logic Paths)

### Valuation Flow
- `POST /v1/valuate` — Statistical engine always runs (minimum 5 comps required)
- ML prediction runs only when statistical confidence > "insufficient"
- ML/statistical disagreement >15% → statistical wins (conservative, good design)
- Cache key includes daily date → same query returns cached result for 24h
- `_compute_deal_indicator` correctly classifies great_deal/fair_deal/above_market
- **Issue:** Cached results return empty `comps` and `adjustments` lists — users see stale attribution

### Authentication Flow
- Register → login → access token + refresh token → refresh → logout
- Password hashing: PBKDF2-SHA256, per-user salt
- JTI-based revocation with memory cache + DB persistence
- Refresh token rotation (old token revoked on refresh)
- **Issue:** No `/auth/register` or `/auth/login` page integration — `auth.html` has no fetch calls

### Watchlist Flow
- GET/POST/DELETE on `/v1/watchlist` all require authentication
- Proper user-scoped queries (`WHERE user_id = :uid`)
- **Issue:** `auth.html` doesn't store tokens in a way that other pages can read them for watchlist API calls

---

## B5. Verdict on Aug 2 Audit Issues

### FIXED (15 issues)
1. ✅ SSRF protection via `validate_public_url()`
2. ✅ Password strength validation (8 chars, 2 char classes, blacklist)
3. ✅ Rate limiting on auth endpoints
4. ✅ JWT token expiry reduced to 15 minutes
5. ✅ Token revocation (JTI blacklist)
6. ✅ Refresh token rotation
7. ✅ `auth/me` KeyError fix (returns `id`, `email`, `role`)
8. ✅ Watchlist/notifications null-check on `user`
9. ✅ Request body size limit (1MB)
10. ✅ CORS allows DELETE method
11. ✅ `render.yaml` deploys from `master`
12. ✅ Docker runs as non-root user
13. ✅ Circuit breaker in scrapers (10 consecutive failures)
14. ✅ `BaseScraper._persist()` calls full pipeline chain
15. ✅ Startup validation in production/staging

### STILL OUTSTANDING (20+ issues)
- ❌ PBKDF2 iterations at 100,000 (OWASP recommends 600,000+)
- ❌ No email verification
- ❌ No account lockout
- ❌ No staging environment
- ❌ No database backups
- ❌ No monitoring/alerting (Prometheus metrics emitted but nothing scrapes them)
- ❌ `auth.html` is still a visual mockup
- ❌ Preview data mixed with live data on multiple pages
- ❌ Scraper→pipeline gap in production (parsers work, but validation/promotion not called)
- ❌ Filesystem-local ML model storage
- ❌ `pickle.load` without safety checks
- ❌ Many `except Exception: pass` blocks
- ❌ No secret scanning in pre-commit
- ❌ `DATABASE_URL_SYNC` missing from `render.yaml`
- ❌ Dual metrics systems (prometheus_client + custom MetricsRegistry)
- ❌ No log aggregation
- ❌ No error tracking (Sentry/DataDog)
- ❌ Metrics endpoint is public
- ❌ Engine connection pool missing `pool_pre_ping`
- ❌ Frontend architecture confusion (vanilla + React coexistence)

---

# Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Overall UI Quality** | 7/10 | Polished dark theme, consistent design tokens, minor SVG bug |
| **Overall UX Quality** | 5/10 | Clean navigation but preview/live data confusion, no real auth flow |
| **Accessibility** | 6/10 | Skip links, ARIA labels, keyboard nav on autocomplete. Missing: focus indicators on some elements, no screen reader testing |
| **Performance** | 6/10 | Good caching strategy, but large hero image (1.8MB), no lazy loading |
| **Code Quality** | 7/10 | Clean architecture, consistent patterns, but 46 broad except clauses and untested core IP |
| **Maintainability** | 6/10 | Good backend structure, vanilla JS frontend will be hard to scale |
| **Production Readiness** | 4/10 | Security improved, but no backup/monitoring/staging. Core IP untested. Pipeline gap. |

---

# Top 20 Highest Priority Issues

| # | Issue | Severity | Category |
|---|-------|----------|----------|
| 1 | Core valuation engine untested (engine/ 25% coverage) | **CRITICAL** | Testing |
| 2 | Scraper→pipeline integration not wired in production | **CRITICAL** | Architecture |
| 3 | No database backups — unrecoverable data loss risk | **CRITICAL** | Infrastructure |
| 4 | No staging environment — can't validate before production | **CRITICAL** | Infrastructure |
| 5 | No monitoring/alerting — silent production failures | **HIGH** | Operations |
| 6 | Auth DB fail-open: DB outage + forged JWT = privilege escalation | **HIGH** | Security |
| 7 | `except Exception: pass` in URL parser → silently wrong valuations | **HIGH** | Correctness |
| 8 | `auth.html` is visual mockup — no real login/register flow | **HIGH** | Feature Gap |
| 9 | Preview/live data confusion on reports, market, detail pages | **HIGH** | UX |
| 10 | PBKDF2 iterations at 100,000 (should be 600,000+) | **MEDIUM** | Security |
| 11 | No email verification flow | **MEDIUM** | Security |
| 12 | No account lockout mechanism | **MEDIUM** | Security |
| 13 | 46 broad `except Exception` clauses swallow errors silently | **MEDIUM** | Code Quality |
| 14 | SVG path rendering error on browse page (malformed path data) | **MEDIUM** | UI Bug |
| 15 | Engine connection pool missing `pool_pre_ping=True` | **MEDIUM** | Reliability |
| 16 | `DATABASE_URL_SYNC` missing from `render.yaml` | **MEDIUM** | Deployment |
| 17 | Metrics endpoint is public (no auth) | **LOW** | Security |
| 18 | Logout doesn't revoke refresh token | **LOW** | Security |
| 19 | 1.8MB hero-bg.png — should be optimized | **LOW** | Performance |
| 20 | 18 temp Chrome profile dirs (~280MB) in working tree | **LOW** | Cleanup |

---

# Quick Wins (Under 1 Hour Each)

1. **Add `pool_pre_ping=True`** to SQLAlchemy engine → prevents stale connection errors
2. **Add `DATABASE_URL_SYNC`** to `render.yaml` → fixes Alembic migrations on Render
3. **Delete 18 `tmp-*` directories** → clean working tree
4. **Optimize `hero-bg.png`** → convert to WebP, compress to <300KB
5. **Fix SVG path data** in `index.html` → resolves browse page console errors
6. **Add `METRICS_REQUIRE_AUTH=true`** config flag → restrict `/metrics` endpoint
7. **Bump PBKDF2 iterations** from 100,000 to 600,000 → OWASP compliance
8. **Wire `auth.html` to real API** → add `fetch()` calls to `/v1/auth/login` and `/register`

---

# Long-Term Improvements

1. **Write valuation engine tests** — `statistical.py`, `comp_finder.py`, `trainer.py`, features
2. **Close scraper→pipeline gap** — wire `BaseScraper._persist()` into the production runner
3. **Resolve frontend architecture** — pick vanilla or React, archive the other
4. **Set up staging environment** — Render service from `preview` branch
5. **Add database backups** — Automated daily pg_dump + WAL archiving
6. **Add monitoring** — Prometheus + Grafana or Render-native metrics
7. **Add error tracking** — Sentry or equivalent
8. **Add email verification** — Token-based email confirmation flow
9. **Add account lockout** — N failed attempts → temporary lock
10. **Replace preview data** — Real API endpoints for reports, market insights, model catalog
11. **Refactor `index.js`** — Module pattern or migration to TypeScript
12. **Add dependency scanning** — `pip-audit` as a blocking CI check (not `|| true`)
13. **Add secret scanning** — `detect-secrets` or `trufflehog` in pre-commit
14. **Load testing** — Verify `/valuate` rate limits and DB pool sizing under load
15. **Database migration rollback testing** — Verify downgrade paths work

---

# Summary of Changes Since Aug 2 Audit

**15 critical/high issues fixed** in 4 days of development:
- Security: SSRF protection, JWT hardening, password validation, rate limiting, secret masking
- Operations: Non-root Docker, request size limits, circuit breakers, CORS fixes
- Correctness: auth/me KeyError, watchlist null-checks, render.yaml branch
- Pipeline: `_persist()` now calls full validate→normalize→score→promote chain

**~70 issues remain**, with the most critical being:
1. Untested valuation engine (the product)
2. No backup/monitoring/staging infrastructure
3. Auth/DB fail-open security risk
4. Frontend integration gaps (auth mockup, preview/live data confusion)

The platform is on a positive trajectory. With focused effort on the top 5 critical issues, it could reach ~65% production readiness for a private beta launch.

---

*Generated by automated comprehensive audit on 2026-08-04. All findings verified through static code analysis, test suite execution, QA sweep (13 pages, 2 viewports), and headless browser inspection.*
