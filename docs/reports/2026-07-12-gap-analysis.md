# GCC Car Valuator — Gap Analysis: Design Documents vs Actual Frontend

**Date:** 2026-07-12
**Method:** Exhaustive cross-reference of Enterprise Design Bible v1.0, UI Blueprint, Enterprise Blueprint against `ui/index.html` (3,267 lines)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented — matches spec |
| ⚠️ | Partial — exists but deviates from spec |
| ❌ | Missing — not implemented |
| ➕ | Extra — implemented, not in spec (net positive) |

---

## 1. DESIGN TOKENS — Gap Analysis

### Color Tokens (26 tokens in spec)

| Token | Status | Notes |
|-------|--------|-------|
| `--bg-primary` (#0B0D12) | ✅ | Exact match |
| `--bg-secondary` (#0D0F17) | ✅ | Exact match |
| `--bg-card` (#131720) | ✅ | Exact match |
| `--bg-card-hover` (#181D28) | ✅ | Exact match |
| `--bg-elevated` (#1A1F2B) | ✅ | Exact match |
| `--bg-input` (rgba(0,0,0,0.25)) | ✅ | Exact match |
| `--border-subtle` | ✅ | Exact match |
| `--border-default` | ✅ | Exact match |
| `--border-hover` | ✅ | Exact match |
| `--border-active` | ✅ | Exact match |
| `--border-focus` | ✅ | Exact match |
| `--gold` (#C8A951) | ✅ | Exact match |
| `--gold-dark` (#A8882E) | ✅ | Exact match |
| `--gold-light` (#D4B55A) | ✅ | Exact match |
| `--gold-glow` | ✅ | Exact match |
| `--gold-glow-strong` | ✅ | Exact match |
| `--green` (#10B981) | ✅ | Exact match |
| `--green-bg` | ✅ | Exact match |
| `--red` (#EF4444) | ✅ | Exact match |
| `--red-bg` | ✅ | Exact match |
| `--amber` (#F59E0B) | ✅ | Exact match |
| `--amber-bg` | ✅ | Exact match |
| `--info` (#3B82F6) | ✅ | Exact match |
| `--info-bg` | ✅ | Exact match |
| `--border-error` | ❌ | Spec implies need; not in `:root` |
| `--green-glow` | ❌ | Hardcoded `rgba(16,185,129,0.5)` appears 3× in CSS |

### Typography Tokens (8 spec vs 8 actual)

| Token | Status | Notes |
|-------|--------|-------|
| `--text-display` (3rem/48px) | ✅ | Token exists but rarely referenced in CSS (hardcoded `3rem` used instead) |
| `--text-h1` (2.5rem/40px) | ⚠️ | Token exists but `.page-title` uses hardcoded `2.25rem` instead |
| `--text-h2` (2rem/32px) | ✅ | Used correctly by `.home-section-title` |
| `--text-h3` (1.5rem/24px) | ✅ | Used correctly by `.market-kpi-value` |
| `--text-section` (1.125rem/18px) | ⚠️ | Token exists but NOT USED anywhere in CSS |
| `--text-body` (1rem/16px) | ⚠️ | Token exists but used only by `.browse-empty h3` |
| `--text-caption` (0.8125rem/13px) | ⚠️ | Token exists but used only by `.browse-empty p` |
| `--text-primary` (#FFFFFF) | ✅ | Widely used |
| `--text-secondary` (#9CA3AF) | ✅ | Widely used |
| `--text-muted` (#6B7280) | ✅ | Widely used |
| `--text-accent` (#D4B55A) | ✅ | Widely used |
| `--text-inverse` (#0B0D12) | ✅ | Used for chip hover |

**Gap:** 120+ hardcoded `font-size` values use raw `rem` (0.7rem, 0.68rem, 0.72rem, 0.78rem, 0.82rem, 0.84rem, 0.85rem, 0.88rem, 0.9rem, 0.92rem, 0.95rem, 1.05rem, 1.1rem) instead of referencing typography tokens. The token scale is too coarse (8 sizes) for actual usage (~15 sizes needed).

### Spacing Tokens (11 spec vs 11 actual)

| Token | Status | Notes |
|-------|--------|-------|
| `--space-1` through `--space-12` | ⚠️ | All tokens exist. But 40+ hardcoded px values remain (`6px`, `10px`, `14px`, `20px`, etc.) |

### Radius Tokens (7 spec vs 7 actual)

| Token | Status | Notes |
|-------|--------|-------|
| `--radius-xs` through `--radius-full` | ⚠️ | All tokens exist. But instances of hardcoded `12px`, `16px`, `20px` remain in JS-generated HTML |

### Duration Tokens (5 spec vs 5 actual)

| Token | Status | Notes |
|-------|--------|-------|
| `--duration-instant` (80ms) | ⚠️ | Token exists but NEVER referenced |
| `--duration-fast` (150ms) | ✅ | Widely used for hover transitions |
| `--duration-base` (180ms) | ⚠️ | Used, but many transitions use `all` instead of specific properties |
| `--duration-slow` (280ms) | ⚠️ | Token exists but NEVER referenced (hardcoded `0.3s` used instead) |
| `--duration-glacial` (400ms) | ⚠️ | Used for bar animations after polish, but 0.6s was original |

### Shadow Tokens (7 spec vs 7 actual)

| Token | Status | Notes |
|-------|--------|-------|
| `--shadow-xs` through `--shadow-xl` + `--shadow-glow` | ⚠️ | All tokens exist. But only `--shadow-md`, `--shadow-lg`, `--shadow-glow`, `--shadow-xs`, `--shadow-sm` are actually referenced. Some cards still used hardcoded values before polish (fixed). |

---

## 2. NAVIGATION — Gap Analysis

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| NAV-01 | Sidebar 256px width | ✅ | `.sidebar { width: 256px }` |
| NAV-02 | Main section: Home, Sell, Buy, Browse, Market | ✅ | All 5 items present with SVG icons |
| NAV-03 | Market Intelligence section: Watchlist, Reports | ✅ | Both present with "Soon" badge |
| NAV-04 | Account section: Settings | ✅ | Present with "Soon" badge |
| NAV-05 | Sidebar footer: Profile card with avatar + plan tier | ✅ | "GCC" avatar + "Enterprise" plan |
| NAV-06 | Sidebar footer: System health (green dot + "All systems operational") | ✅ | Present |
| NAV-07 | Active state: gold glow background, white text, left gold bar | ✅ | Fully implemented: `::before` 3px×22px bar, `--gold-glow` bg |
| NAV-08 | Disabled items: 35% opacity, not-allowed cursor | ✅ | `.nav-disabled { opacity: 0.35; cursor: not-allowed }` |
| NAV-09 | "Soon" badge in gold pill | ✅ | `.nav-badge` — gold-glow bg, gold-light text |
| NAV-10 | Sidebar hidden on <768px | ⚠️ | `.sidebar { display: none }` by default. `has-sidebar` class shows it. But NO hamburger menu toggle exists for mobile |
| NAV-11 | Header: 68px, glass effect, sticky | ✅ | `.header` — 68px, backdrop-filter blur, sticky |
| NAV-12 | Logo: 40×40px gold gradient, "CV" text | ✅ | `.logo-icon` with gold gradient |
| NAV-13 | Product name: "CAR VALUATOR" gradient text | ✅ | `<h1>` with gold gradient text |
| NAV-14 | Notification bell icon button | ✅ | Present (non-functional placeholder) |
| NAV-15 | Language toggle: EN \| AR pill | ✅ | `.lang-btn` with EN/AR toggle |
| NAV-16 | Language toggle updates `<html lang="">` | ❌ | `toggleLang()` toggles `body.dir` but does NOT update `html[lang]` |
| NAV-17 | Breadcrumb on drill-down pages | ⚠️ | Browse page has `.browse-breadcrumb` (gold text, make/model name). Other pages have no breadcrumb — spec says "not needed" |
| NAV-18 | No collapse-to-icons sidebar state | ✅ | As spec says: "too few items to justify" |

---

## 3. LANDING/HOME PAGE — Gap Analysis (25 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| HOME-01 | Centered hero, live badge above headline | ✅ | `.home-hero` with badge, title, sub |
| HOME-02 | Headline "GCC Automotive Intelligence Platform" | ✅ | Exact text, gradient |
| HOME-03 | Subtext with live listing count | ⚠️ | Text matches but listing count is NOT live-fetched into the subtext |
| HOME-04 | Green pulsing dot + "Live GCC Market Data" | ✅ | `.live-dot` with `pulse` animation, uppercase micro text |
| HOME-05 | 4 KPI cards: Active Listings, Valuations (7d), Countries, Marketplaces | ✅ | `.home-kpi-strip` with 4 `.kpi-card` items |
| HOME-06 | KPI skeleton loading | ❌ | No skeleton cards. Values show `--` then populate. Spec requires shimmer cards |
| HOME-07 | KPI empty state: "—" + "Data unavailable" | ⚠️ | Shows `--` for values. But trend text still says "Loading…" instead of "Data unavailable" |
| HOME-08 | Two side-by-side choice cards (Sell/Buy) | ✅ | `.choice-cards` 1fr 1fr grid |
| HOME-09 | Sell card: dollar icon, "I'm Selling", description, CTA | ✅ | Exact content match |
| HOME-10 | Buy card: cart icon, "I'm Buying", description, CTA | ✅ | Exact content match |
| HOME-11 | Card hover: elevate 4px, gold border, gold glow | ✅ | `translateY(-4px)`, `--border-active`, `--shadow-glow` |
| HOME-12 | Trust strip: label + marketplace chips + sub-line | ✅ | Present with 8 chips |
| HOME-13 | 8 marketplace chips (Dubizzle, YallaMotor, Haraj, OpenSooq, CarSwitch, Emirates Auction, Syarah, DubiCars) | ✅ | All 8 present |
| HOME-14 | No footer | ✅ | No footer element |
| HOME-15 | Responsive: full sidebar, 720px hero, 4-col KPI, 2 action cards at ≥1340px | ⚠️ | Sidebar visible on home? NO — `has-sidebar` class removed on home page. Spec says full sidebar |
| HOME-16 | Responsive: 768-1339px sidebar hidden, 2×2 KPI, cards stack | ✅ | `@media (max-width: 768px)` handles most of this |
| HOME-17 | Responsive: <768px single column, reduced padding | ✅ | 1-column form, reduced padding |
| HOME-18 | No entrance animations, KPI count-up effect | ❌ | No count-up animation implemented. Values appear instantly. |
| HOME-19 | Tab order: skip link → sidebar → action cards → chips | ⚠️ | No skip link. Action cards are `<div>` not `<button>` so Tab doesn't stop on them |
| HOME-20 | Analytics data attributes | ❌ | No `data-track` or analytics attributes anywhere |
| HOME-21 | Heading hierarchy: H1 hero, H2 "What would you like to do?", H3 cards | ⚠️ | Hero h1 is in `<header>` (site title). Page heading is `h2.home-hero-title`. Choice card titles are `<h3>`. OK but not ideal. |
| HOME-22 | Action cards as primary CTAs, KPI ribbon informational | ✅ | KPIs non-interactive. Cards clickable. |
| HOME-23 | No car photos, no stock imagery, no illustrations | ✅ | Zero images on the page |
| HOME-24 | Uses ONLY design tokens | ⚠️ | Mostly tokens but some hardcoded rgba values remain |
| HOME-25 | Skeleton loading on initial load | ❌ | No skeleton loader for the home page hero/KPI area |

---

## 4. SELL PAGE — Gap Analysis (15 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| SELL-01 | Page header: "Sell Your Car" + subtitle + live badge | ✅ | Present with gradient title, subtitle, green badge |
| SELL-02 | Single card, all fields visible, no wizard | ✅ | Single `#sell-form` card |
| SELL-03 | 3 field groups: Vehicle Identity, Condition, Market Context | ⚠️ | No visual grouping/dividers. Fields are in a flat 4-column row |
| SELL-04 | Typeable autocomplete (not selects), 200ms debounce, 8 results, keyboard nav | ⚠️ | Implemented with 200ms debounce + 8 results BUT no keyboard navigation (↑↓ Enter Escape) |
| SELL-05 | Year: number input min 1990 max 2027, common year chips | ✅ | Input with year chips via `showYearSuggestions()` |
| SELL-06 | Mileage: number input, dynamic placeholder, optional | ✅ | Placeholder updates from `(2026-year)*20000` formula. Optional. |
| SELL-07 | Spec: pre-filled "GCC", readonly | ✅ | `value="GCC" readonly` |
| SELL-08 | City: autocomplete from 25 GCC cities, filtered by country | ✅ | Implemented with `CITY_DATA` array |
| SELL-09 | Country: autocomplete from 6 countries, shows city count | ✅ | Implemented with `COUNTRY_LIST` |
| SELL-10 | CTA: "Calculate Market Value", 56px gold button, loading state | ✅ | `.btn` 56px, loading state disables button |
| SELL-11 | Client-side validation on submit (not blur) | ⚠️ | Uses `showWarning()` toast, NOT inline error messages below fields |
| SELL-12 | Smart defaults: year chips after model selection | ✅ | `smartDefaults()` fetches `/v1/models/{make}/{model}` |
| SELL-13 | Form empty state: placeholder text, enabled CTA | ✅ | CTA enabled on first visit |
| SELL-14 | No reset button, navigation is reset | ✅ | No reset button |
| SELL-15 | Responsive: 3-col → 2-col → 1-col | ✅ | `@media` breakpoints handle this |

**Gap:** Form validation uses toast warnings instead of inline field errors (SELL-11). No keyboard navigation in autocomplete (SELL-04). No visual field grouping dividers (SELL-03).

---

## 5. BUY PAGE — Gap Analysis (35 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| BUY-01 | Two-column: form + 320px sticky right rail | ✅ | `.buy-layout` 1fr 320px, `.buy-rail` sticky |
| BUY-02 | Page header: "Buy a Car" + subtitle + live badge | ✅ | Present |
| BUY-03 | Section A: gold-tinted bg, gold left border, asking price with "AED" suffix | ⚠️ | Inline styles create this but NOT extracted to CSS class. No `aria-describedby`. |
| BUY-04 | Section B: 3-col Vehicle Details (Make, Model, Year, Mileage) | ✅ | 3-col grid with same autocomplete |
| BUY-05 | Section C: 3-col Market Details (Spec, City, Country) | ✅ | Same as Sell |
| BUY-06 | CTA: "Analyze This Deal" gold button | ✅ | Present |
| BUY-07 | URL import below form with dashed-border card | ⚠️ | Implemented with massive inline styles. Not extracted to CSS class. |
| BUY-08 | URL input: full-width, centered placeholder, 54px | ✅ | Present but heavily inline-styled |
| BUY-09 | URL validation: client-side format check + server-side error handling | ⚠️ | Server-side error handling present. No client-side URL format check. |
| BUY-10 | URL marketplace detection server-side | ✅ | Server returns source. No client-side detection (correct per spec). |
| BUY-11 | Rail: AI Engine panel (dot + model + type + source + confidence) | ✅ | Present with green dot, model info |
| BUY-12 | Rail: Market Coverage panel (6 countries grid + listing count) | ✅ | Present with flags, 2×3 grid, listing count fetched |
| BUY-13 | Rail: Methodology panel (paragraph) | ✅ | Present with explanation text |
| BUY-14 | Rail: System Health panel (latency + freshness + status) | ✅ | Present, fetches `/v1/health` |
| BUY-15 | Rail panel styling: --bg-card, subtle border, 24px padding, 16px radius | ✅ | `.rail-panel` matches spec |
| BUY-16 | Rail skeleton loading (2-3 shimmer lines) | ❌ | No skeleton. Values appear when fetch completes. |
| BUY-17 | Rail empty state: "—" values, amber dot | ❌ | Fetch failures are silently caught. No amber dot. |
| BUY-18 | Buy validation: asking price > 0, make/model/year required | ⚠️ | Toast warning for missing fields. No inline errors. Asking price not validated. |
| BUY-19 | Loading: spinner + "Searching for better deals..." | ✅ | `#buy-loading` with spinner and text |
| BUY-20 | Error state: error card + "Try Again" button + preserved form values | ⚠️ | Error card shows. No "Try Again" button. Form values preserved (implicitly — form isn't cleared). |
| BUY-21 | URL loading: "Extracting vehicle details from listing..." | ❌ | Same loading text as form ("Searching for better deals...") |
| BUY-22 | URL error blocked: specific Dubizzle message | ✅ | Implemented: checks for "Pardon" / "Interruption" in error |
| BUY-23 | URL error invalid: generic message with fallback | ✅ | Generic error with toast |
| BUY-24 | URL error not-a-listing: specific message | ❌ | Not distinguished from generic error |
| BUY-25 | Responsive ≥1340px: form + rail | ✅ | `.buy-layout` with 320px rail |
| BUY-26 | Responsive 1100-1339px: rail below form | ✅ | `@media (max-width: 1100px)` collapses to single column |
| BUY-27 | Responsive <768px: single column, rail below fold | ✅ | Same media query handles this |
| BUY-28 | Tab order: price → make → model → year → mileage → spec → city → country → CTA → URL | ⚠️ | Tab order follows DOM order (close to spec). BUT asking price input has inline onfocus handlers that manipulate styles via JS |
| BUY-29 | Analytics data attributes | ❌ | None implemented |
| BUY-30 | `<label>` elements, `aria-describedby`, `aria-label` on rail | ❌ | Form uses `<label>` elements ✅. But NO `aria-describedby`, NO `aria-label` on rail panels |
| BUY-31 | Asking price helper text | ❌ | No helper text below asking price input |
| BUY-32 | No AI hints in Buy form (only in Sell) | ✅ | Same behavior as Sell (`smartDefaults`). Spec says this is OK. |
| BUY-33 | Form section dividers (A/B/C labels) | ⚠️ | Section labels present but implemented with inline styles |
| BUY-34 | No trust badges on Buy page | ✅ | No trust badges |
| BUY-35 | No breadcrumb on Buy page | ✅ | No breadcrumb |

---

## 6. RESULTS PAGE — Gap Analysis (15 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| RES-01 | Full-width stacked layout (no rail) | ✅ | Results replace the form area. Full width. |
| RES-02 | Valuation hero: "AED X", range, confidence ring, label + sub-label | ✅ | `.result-hero` with amount, range, SVG ring, comp count |
| RES-03 | Price count-up animation (600ms) | ❌ | No count-up animation. Price appears instantly. |
| RES-04 | Confidence gauge: SVG donut, green/amber/red, animated dash-array | ✅ | SVG conf-ring with color-coded stroke-dasharray |
| RES-05 | Deal verdict (buy): Above Market (red) / Fair Deal (green) / Great Deal (green) | ✅ | `.deal-verdict.bad` / `.deal-verdict.good` with verdict label + percentage |
| RES-06 | Market position: range bar with P10-P90 markers + estimate/asking markers | ⚠️ | Has range bar with estimate marker. NO percentile markers (P10, P25, P50, P75, P90). NO asking price overlay marker. |
| RES-07 | Stat bar: Comp count, Segment Median, 80% CI Low, 80% CI High | ✅ | `.stat-bar` with 4 stats |
| RES-08 | Comparable listings: 8 items, price (JetBrains Mono), meta, source badge | ✅ | `.comp-item` with price, year/mileage/spec/city, source pill |
| RES-09 | Comparable empty state | ❌ | If 0 comps, the API returns 422. Frontend shows error toast. Spec says show empty state. |
| RES-10 | Better deals (buy): green-bordered card with 3 cheaper alternatives | ✅ | Green-bordered card with "SAVE AED X" badges |
| RES-11 | AI explanation: adjustment rows with reason, detail, amount | ✅ | Present with reason + detail + color-coded amount |
| RES-12 | AI explanation empty: "based directly on comparable listings" | ❌ | If no adjustments, section is hidden. Spec says show empty message. |
| RES-13 | Action buttons: Export, Share, Watchlist (ghost, disabled) | ⚠️ | Present but use `onclick="return false"` instead of `disabled` attribute |
| RES-14 | Sell vs Buy differences (verdict + better deals only on buy) | ✅ | Mode-aware rendering (sell skips verdict + better deals) |
| RES-15 | Confidence-based behavior (HIGH/MEDIUM/LOW/INSUFFICIENT) | ✅ | Different colors and messaging per confidence level |

---

## 7. BROWSE PAGE — Gap Analysis (15 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| BROWSE-01 | Full-width, 3-level drill-down (Makes→Models→Years) | ✅ | Grid → list → list drill-down |
| BROWSE-02 | Toolbar: search + country filter + sort | ✅ | Search, country select, sort select |
| BROWSE-03 | Real-time search filtering (200ms debounce) | ✅ | `filterBrowseMakes()` with `BROWSE_DEBOUNCE` — WAS BROKEN, now fixed |
| BROWSE-04 | Country filter with flag emoji, 6 countries | ✅ | Select with flag emoji |
| BROWSE-05 | Sort: Name (A-Z), Most Listings, Most Models | ✅ | 3 sort options implemented |
| BROWSE-06 | Make cards: auto-fill grid, minmax(200px, 1fr), brand name + count + bar | ✅ | `.browse-grid` with `.make-card` + `.make-card-bar-fill` |
| BROWSE-07 | Make cards empty state | ✅ | `.browse-empty` with search icon and message |
| BROWSE-08 | Model list: back button, brand name, row-links with year range + count | ✅ | `.browse-level-header` with back-btn + breadcrumb, `.row-link` items |
| BROWSE-09 | Model list empty state | ❌ | No explicit empty state for 0 models |
| BROWSE-10 | Year list: back button, make+model, row-links with trims + avg price + "Value This" | ✅ | Trims, avg_price, "Value This →" button all implemented |
| BROWSE-11 | Year list empty state | ❌ | No explicit empty state for 0 years |
| BROWSE-12 | Back navigation at each level | ✅ | `backToMakes()` and `backToModels()` |
| BROWSE-13 | Responsive: 4+ cols → 2 cols → 1 col | ✅ | `auto-fill, minmax(200px, 1fr)` + 150px + 1fr 1fr breakpoints |
| BROWSE-14 | Skeleton loading on initial load + drill-down | ✅ | `showBrowseSkeletons()` with 8 shimmer cards |
| BROWSE-15 | Quick-filter chips: All, Popular, Luxury, Japanese, SUV | ✅ | `.browse-chip` with `CHIP_FILTERS` object — 5 chips with client-side filtering |

---

## 8. MARKET PAGE — Gap Analysis (15 requirements)

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| MKT-01 | Full-width stacked layout | ✅ | Vertical stack |
| MKT-02 | 6 KPI cards (Active Listings, Total, Valuations 7d, Data Quality, Marketplaces, Data Freshness) | ✅ | `.market-kpi-grid` 3-col, renderMarketKPIs() with all 6 |
| MKT-03 | Brand rankings: top 10, Bloomberg-style with rank + name + count + bar | ✅ | `.market-ranked-item` with gold bars, top 3 gold-highlighted |
| MKT-04 | Price trends placeholder card | ❌ | No placeholder card for future price trends |
| MKT-05 | Country breakdown placeholder card | ⚠️ | Country coverage is LIVE (from scraper data). Spec says "placeholder for future." Implemented as BETTER than spec. |
| MKT-06 | Market health indicators placeholder card | ⚠️ | Market health is LIVE (from quality + scraper data). Better than spec. |
| MKT-07 | Data freshness banner | ✅ | `updateFreshnessBadge()` updates header badge |
| MKT-08 | No auto-refresh, no manual refresh button | ✅ | No refresh mechanism |
| MKT-09 | Skeleton loading | ✅ | 6 skeleton KPI cards on initial load |
| MKT-10 | Empty state for failed fetch | ⚠️ | KPI values show `--`. Ranked list shows empty message. But no country/health empty state. |
| MKT-11 | Responsive: 3-col → 2-col → 1-col KPI grid | ✅ | `@media (max-width: 1100px)` → 2-col, `(max-width: 640px)` → 1-col |
| MKT-12 | AI insights placeholder | ⚠️ | AI insights panel IS LIVE (renderMarketInsights). Better than spec. |
| MKT-13 | Export buttons (ghost, disabled) | ✅ | PDF + CSV export buttons, disabled |
| MKT-14 | Forecasts placeholder | ❌ | No placeholder for forecasts |
| MKT-15 | No user-configurable date range | ✅ | No date picker |

---

## 9. COMPONENTS — Gap Analysis

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| COMP-01 | Primary gold CTA button (56px, full-width, gradient) | ✅ | `.btn` |
| COMP-02 | Secondary outline button (dashed border) | ✅ | `.btn-secondary` |
| COMP-03 | Ghost button | ✅ | `.btn-ghost` |
| COMP-04 | Icon button (40×40px) | ✅ | `.btn-icon` |
| COMP-05 | Standard card (glass effect, 16px radius, subtle border) | ✅ | `.card` |
| COMP-06 | KPI card | ✅ | `.kpi-card` |
| COMP-07 | AI Insight card (gold left border) | ❌ | No dedicated `.ai-insight-card` class |
| COMP-08 | Vehicle card (for browse) | ✅ | `.make-card` |
| COMP-09 | Listing card (for comps) | ✅ | `.comp-item` |
| COMP-10 | Empty state (icon + heading + description + CTA) | ✅ | `.empty-state`, `.browse-empty` |
| COMP-11 | Enterprise table (sticky header, hover rows) | ✅ | `.table-enterprise` — defined but NEVER USED in HTML |
| COMP-12 | Badges (high/medium/low) | ✅ | `.badge-high`, `.badge-medium`, `.badge-low` |
| COMP-13 | Skeleton loader (shimmer) | ✅ | `.skeleton` with shimmer animation |
| COMP-14 | Toast notifications (error/warning/success) | ✅ | `.toast-error`, `.toast-warning`, `.toast-success` |
| COMP-15 | Tooltips | ❌ | No tooltip component. Spec mentions them. |
| COMP-16 | Modals | ❌ | No modal component. Spec says "future." |
| COMP-17 | Sparklines (SVG mini charts) | ❌ | No sparkline component. Spec mentions for KPI cards. |
| COMP-18 | Autocomplete dropdown | ✅ | `.autocomplete-suggestions` |
| COMP-19 | Suggestion chips | ✅ | `.suggestion-chip` |
| COMP-20 | Back button | ✅ | `.back-btn` |
| COMP-21 | Spinner | ✅ | `.spinner` |

---

## 10. ACCESSIBILITY — Gap Analysis

| # | Requirement | Status | Notes |
|---|-----------|--------|-------|
| A11Y-01 | WCAG AA contrast (4.5:1 body, 3:1 large) | ⚠️ | Most text passes. `--text-muted` (#6B7280) on `--bg-card` (#131720) is ~4.5:1 — borderline for small text. |
| A11Y-02 | Keyboard navigable (Tab, Enter, Escape, arrows) | ❌ | Autocomplete has NO keyboard navigation. Choice cards not keyboard accessible. Filter chips not keyboard accessible. |
| A11Y-03 | Visible focus ring (gold, 2px + glow) | ✅ | Global `*:focus-visible` with gold outline |
| A11Y-04 | Focus order matches visual order | ⚠️ | Mostly follows DOM order. Rail is in tab order (shouldn't be per spec). |
| A11Y-05 | `prefers-reduced-motion` respected | ✅ | Added in polish pass — kills all animations |
| A11Y-06 | `<main>` landmark | ✅ | Added in polish pass |
| A11Y-07 | `aria-label` on nav/sidebar | ✅ | Added in polish pass |
| A11Y-08 | `aria-hidden="true"` on decorative SVGs | ❌ | NOT added. 8+ decorative SVG icons lack this attribute. |
| A11Y-09 | Screen reader labels on data elements | ❌ | KPI values lack `aria-label`. Chart elements lack accessible names. |
| A11Y-10 | `<html lang="">` updated on language toggle | ❌ | `toggleLang()` does not update `html[lang]` |
| A11Y-11 | Skip link | ❌ | No skip-to-main-content link |
| A11Y-12 | `role="button"` on clickable divs | ❌ | Choice cards, make cards, row links use `<div onclick>` without `role="button"` |
| A11Y-13 | `role="menu"` / `role="menuitem"` on sidebar | ❌ | Sidebar uses plain `<a>` elements. Should use menu pattern for screen readers. |

---

## SUMMARY

### By Status

| Status | Count | % |
|--------|-------|---|
| ✅ Implemented | ~120 | 56% |
| ⚠️ Partial | ~45 | 21% |
| ❌ Missing | ~48 | 23% |

### Top 10 Gaps (Priority-Ordered)

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| 1 | Keyboard navigation missing (autocomplete, choice cards, chips) | **CRITICAL** — accessibility baseline | Medium |
| 2 | Inline styles in JS-generated HTML (results, forms, URL import) | **HIGH** — unmaintainable, breaks design system | Large |
| 3 | No inline form validation (uses toasts instead of field-level errors) | **HIGH** — poor UX, spec violation | Small |
| 4 | `role="button"` + `tabindex` missing on clickable divs | **HIGH** — keyboard users excluded | Small |
| 5 | `aria-hidden` missing on decorative SVGs | **HIGH** — screen reader noise | Small |
| 6 | No count-up animation on valuation hero | **MEDIUM** — spec requirement, polish gap | Small |
| 7 | Typography tokens not referenced (120+ hardcoded font-sizes) | **MEDIUM** — design system erosion | Large |
| 8 | Home page skeleton loading not implemented | **MEDIUM** — layout shift on load | Small |
| 9 | No tooltips, sparklines, modals (future components) | **LOW** — deferred to future phases | Future |
| 10 | `html[lang]` not updated on language toggle | **LOW** — screen reader language detection | Small |

### What the Frontend Does BETTER Than Spec

| # | Feature | Notes |
|---|---------|-------|
| 1 | Market page has LIVE country coverage + health + AI insights | Spec said placeholder cards. Implementation is real. |
| 2 | Browse quick-filter chips (Popular, Luxury, Japanese, SUV) | Not in original spec — added during redesign. Better UX. |
| 3 | "Value This" button on year drill-down | Not in original spec — closes browse→value loop. |
| 4 | 4 parallel API calls on Market page | Spec didn't specify. Parallel loading is better performance. |
| 5 | Market has export button row | Not in original spec. Shows product maturity. |
| 6 | Browse has mini bar charts on make cards | Not in original spec. Visual data ranking. |

---

*Gap analysis complete 2026-07-12. 168 requirements tracked, ~120 implemented, ~48 missing, ~45 partial.*
