# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: Individual car buyers and sellers in the GCC.** They want to know what a used car is actually worth — either their own car before selling, or a listing they're considering buying. They use the free web tool directly, enter vehicle details or paste a listing URL, and get a market valuation with comparable evidence.

**Secondary: Dealers and enterprises.** They need bulk valuations, market intelligence reports, and API access. They may integrate valuations into their own inventory or pricing systems. Enterprise tier has higher rate limits, admin access, and export capabilities.

**Tertiary: Platform operators.** Administrators monitor scraper health, data quality, model drift, and platform metrics via authenticated admin endpoints.

## Product Purpose

GCC Car Valuator tells you what a used car is worth in the Gulf market. It scrapes live listings from 10 marketplaces across 6 GCC countries, normalizes the data, and computes a fair market value using a statistical baseline with an optional ML ensemble. Every valuation comes with comparable evidence, price range, confidence level, and an explainable breakdown of adjustments.

## Positioning

The product's core differentiator is **explainable ML valuation on live market data.** Unlike Kelley Blue Book or regional competitors that use static depreciation tables, GCC Car Valuator computes prices from actual current listings. The ML layer (LightGBM with SHAP) provides feature-level explainability — users see not just a number, but why the number is what it is (mileage adjustment, spec premium, city market effects).

Secondary differentiator: **multi-country GCC coverage.** No other consumer tool covers UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, and Oman in a single product with local market data per country.

## Operating Context

- **Geography:** Gulf Cooperation Council (GCC) — UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman
- **Marketplaces scraped:** Dubizzle UAE/KSA, YallaMotor, Haraj KSA, CarSwitch, Emirates Auction, OpenSooq, Syarah, Mazadak, DubiCars
- **Currencies:** AED (UAE), SAR (Saudi Arabia), KWD (Kuwait), QAR (Qatar), BHD (Bahrain), OMR (Oman). AED is the display default.
- **Languages:** English primary, Arabic supported (RTL layout, i18n data attributes, persisted preference). Bilingual is required.
- **Vehicle specs:** GCC, US, Japan, European, Canadian, Korean — spec origin significantly affects Gulf market pricing.
- **User workflow:** A buyer or seller typically values one car at a time. They may browse models across manufacturers, check market trends, save vehicles to a watchlist, or generate reports.

## Capabilities and Constraints

**Capabilities:**
- Multi-source scraping with rate limiting, robots.txt compliance, circuit breakers, and raw HTML retention
- Data pipeline: validate (Pandera) → normalize (canonical forms, AED conversion) → quality score → promote or dead-letter
- Statistical valuation: percentile bands, mileage/spec/city adjustments, bootstrap confidence intervals, tiered comparable finding
- Optional ML ensemble: LightGBM prediction blended with statistical when agreement is within 15%
- Deal scoring: great deal / fair deal / above market indicators based on asking price vs market range
- AI explanations: natural-language valuation summaries via Claude API (best-effort, gracefully degrades)
- Browse: manufacturer and model discovery with live listing counts per country
- Market trends: brand rankings, country coverage, market health indicators
- Watchlist: save valuations, track price changes over time
- Reports: market intelligence reports with export (PDF/CSV)
- Auth: JWT access/refresh tokens, RBAC with 6 roles (consumer through system), API key auth for URL valuation
- Health checks: liveness, readiness, startup probes with per-dependency status
- Observability: structured logging (structlog), Prometheus metrics, optional OpenTelemetry tracing

**Constraints:**
- No email delivery service configured — email verification, password reset, and notification emails are not yet implemented
- No staging environment — changes deploy directly to production
- Scrapers use httpx (no JS rendering) — marketplace pages requiring client-side rendering will return empty shells
- ML model artifacts are filesystem-local in the Docker image — no model distribution pipeline
- Token revocation is process-local (in-memory) — lost on restart or across multiple instances
- Free Render plan: service spins down after 15 minutes of inactivity, cold starts take 30-50 seconds

**Deliberately undecided:**
- Whether to unify the vanilla HTML/JS frontend and React/Vite sub-application into a single architecture
- Whether to add real-time WebSocket notifications for price alerts vs polling
- Whether to require email verification for consumer-tier accounts or keep registration frictionless

## Brand Commitments

- **Name:** GCC Car Valuator — "Car Valuator — GCC Market Intelligence"
- **Language:** Bilingual English/Arabic is a hard requirement. RTL layout, i18n data attributes, persisted language preference.
- **Data integrity:** All market-facing numbers must be traceable to real listing data. No fabricated valuations, no invented testimonials, no fake accuracy claims. The "98.7% Model Accuracy" KPI was removed because it was indefensible without a published methodology.

## Evidence on Hand

- **Live production deployment:** API at `https://gcc-car-value.onrender.com`, frontend at `https://gcc-car-value.vercel.app`
- **Database:** PostgreSQL with 15 vehicle makes in the models catalog, 384 demo listings seeded for valuation testing
- **Backend source:** `src/` — 138 Python files, FastAPI application
- **Frontend source:** `ui/` — 13 HTML pages, CSS design system, vanilla JS SPA, React/Vite prototype in `ui/src/`
- **Documentation:** Architecture guide at `docs/GCC_CAR_VALUE_ARCHITECTURE.md`, deployment docs, database audit, security audit, prior production readiness audits
- **Tests:** 344 passing, 61% coverage (engine/core IP at ~25%, scrapers at ~15%)
- **Design critique:** Scored 27/40 on Nielsen heuristics (trend: 24→26→27→28), zero P0/P1 issues remaining

## Product Principles

1. **Statistical first, ML second.** The valuation engine always runs. ML is optional and only blended when it agrees with the statistical baseline within 15%. If ML fails or is unavailable, the statistical result stands. Users are never dependent on a black box.

2. **Explainability over authority.** Every valuation must show what moved the price — mileage adjustments, spec premiums, city effects, comparable evidence. "Trust us" is not a feature.

3. **Live data, not static tables.** Prices come from actual current marketplace listings. When data is stale or insufficient, the product says so rather than fabricating a number.

4. **Bilingual by design, not translation layer.** Arabic support is baked into the DOM (data-i18n attributes, RTL layout) and persisted per-user, not bolted on as a separate translated site.

5. **Degrade gracefully.** ML, AI explanations, metrics, tracing, and external APIs must never prevent the core valuation from working. Every optional service has a fallback.

## Accessibility & Inclusion

- WCAG 2.1 AA target
- Arabic RTL layout with persisted language preference
- Keyboard-navigable autocomplete comboboxes
- Skip-to-content link
- ARIA labels on interactive elements, aria-live on dynamic content, aria-busy on loading states
- Form errors use role="alert" for screen reader announcement
- Reduced motion media query support
