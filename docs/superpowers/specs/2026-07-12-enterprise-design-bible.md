# GCC Car Valuator — Enterprise Design Bible v1.0 (Complete)

**Date:** 2026-07-12
**Status:** Awaiting approval
**Replaces:** All placeholder templates in `GCC_Car_Valuator_Enterprise_Design_Bible_v1.docx`

---

## 1. Vision & Product Principles

**Target customers:** Dealerships, banks, insurers, governments, fleet operators.
**Annual value:** $25k–100k+ per account.
**North Star:** Premium, data-first, AI-assisted, trustworthy.

**Core constraint:** Do not change backend, APIs, routing, or business logic. This is a UI-only transformation.

**Design influences (do not copy):** Bloomberg (data density, terminal feel), Linear (clarity, purpose), Stripe (polish, confidence), Ramp (efficiency, smarts), Datadog (monitoring, real-time), Palantir (intelligence, depth), Apple (typography, restraint).

---

## 2. Brand & Visual Identity

### 2.1 Color System

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0B0D12` | Page background |
| `--bg-secondary` | `#0D0F17` | Sidebar, header |
| `--bg-card` | `#131720` | Card surfaces |
| `--bg-card-hover` | `#181D28` | Card hover state |
| `--bg-elevated` | `#1A1F2B` | Elevated surfaces (dropdowns, modals) |
| `--bg-input` | `rgba(0,0,0,0.25)` | Input backgrounds |
| `--border-subtle` | `rgba(255,255,255,0.04)` | Subtle separators |
| `--border-default` | `rgba(255,255,255,0.06)` | Standard borders |
| `--border-hover` | `rgba(255,255,255,0.10)` | Hover borders |
| `--border-active` | `rgba(200,169,81,0.30)` | Active/selected borders |
| `--border-focus` | `rgba(200,169,81,0.45)` | Focus ring |
| `--gold` | `#C8A951` | Primary accent |
| `--gold-dark` | `#A8882E` | Darker gold (gradients) |
| `--gold-light` | `#D4B55A` | Lighter gold (text) |
| `--gold-glow` | `rgba(200,169,81,0.15)` | Glow effects |
| `--gold-glow-strong` | `rgba(200,169,81,0.28)` | Strong glow |
| `--green` | `#10B981` | **ONLY for live/status/success indicators** |
| `--green-bg` | `rgba(16,185,129,0.10)` | Green background |
| `--red` | `#EF4444` | Errors, above-market warnings |
| `--red-bg` | `rgba(239,68,68,0.10)` | Red background |
| `--amber` | `#F59E0B` | Warnings, medium confidence |
| `--amber-bg` | `rgba(245,158,11,0.10)` | Amber background |
| `--info` | `#3B82F6` | Information, links |
| `--info-bg` | `rgba(59,130,246,0.10)` | Info background |

**Rule:** Emerald/green is EXCLUSIVELY for live indicators, system health, success states, and deal-quality verdicts. Never use green for decoration, badges, or non-semantic elements.

### 2.2 Typography

| Scale | Size | Weight | Usage |
|-------|------|--------|-------|
| Display | 48px (3rem) | 900 | Hero valuation amounts |
| H1 | 40px (2.5rem) | 900 | Page titles |
| H2 | 32px (2rem) | 800 | Section headings |
| H3 | 24px (1.5rem) | 800 | Card headings |
| Section | 18px (1.125rem) | 700 | Subsection labels |
| Body | 16px (1rem) | 400 | Body text |
| Caption | 13px (0.8125rem) | 500 | Labels, metadata |
| Micro | 11px (0.6875rem) | 600 | Uppercase labels, badges |

**Fonts:** Inter (body, headings), JetBrains Mono (prices, numbers, code).
**Loading:** Google Fonts with `font-display: swap`.

### 2.3 Spacing (8px Grid)

| Token | Value |
|-------|-------|
| `--space-1` | 8px |
| `--space-2` | 16px |
| `--space-3` | 24px |
| `--space-4` | 32px |
| `--space-5` | 40px |
| `--space-6` | 48px |
| `--space-8` | 64px |
| `--space-10` | 80px |
| `--space-12` | 96px |

### 2.4 Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-xs` | 4px | Inline code, tiny badges |
| `--radius-sm` | 6px | Small buttons, chips |
| `--radius-md` | 10px | Standard buttons, inputs |
| `--radius-lg` | 12px | Cards, modals |
| `--radius-xl` | 16px | Large cards, KPI cards |
| `--radius-2xl` | 20px | Hero cards, result displays |
| `--radius-full` | 9999px | Pills, badges, avatars |

### 2.5 Elevation & Motion

**Shadows:** Subtle. Dark backgrounds mean shadows are depth, not decoration.
**Motion:** 180ms `ease` for all interactive transitions (hover, focus, expand).
**Page transitions:** None. Pages swap instantly (the content changes, not the chrome).
**Loading:** Skeleton screens with shimmer animation. No spinners except for < 500ms operations.
**Focus:** Gold focus ring (`0 0 0 3px var(--gold-glow)`) on all interactive elements.

---

## 3. Layout System

### 3.1 Grid

- **12-column CSS Grid** for page-level layouts
- **Max content width:** 1340px (without sidebar), 1120px (with sidebar)
- **Sidebar width:** 256px (fixed)
- **Right rail width:** 320px (fixed, where applicable)
- **Gutter:** 24px between columns
- **8pt baseline:** All spacing, padding, and margins on the 8px grid

### 3.2 Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| ≥ 1340px | Full layout: sidebar + main + optional rail |
| 1100–1339px | Right rail collapses below main content |
| 768–1099px | Sidebar collapses to icons; form grids go 2-column |
| < 768px | Sidebar hidden (hamburger); single column; reduced padding |

### 3.3 Z-Index Scale

| Layer | Value | Usage |
|-------|-------|-------|
| Dropdown | 200 | Autocomplete, selects |
| Sticky | 500 | Sticky headers, rails |
| Overlay | 800 | Sheet overlays, drawer backdrops |
| Modal | 1000 | Dialogs, modals |
| Toast | 9999 | Notifications |

---

## 4. Navigation

### 4.1 Sidebar (256px, persistent left)

**Main Section:**
- Home (dashboard icon)
- Sell (dollar-sign icon)
- Buy (cart icon)
- Browse (grid icon)
- Market (activity/trend icon)

**Market Intelligence Section:**
- Watchlist (heart icon) — "Soon" badge
- Reports (book icon) — "Soon" badge

**Account Section:**
- Settings (gear icon) — "Soon" badge

**Sidebar Footer:**
- Profile card: avatar (initials), name ("GCC Car Valuator"), plan tier ("Enterprise")
- System health: green dot + "All systems operational"

**Active State:**
- Gold glow background (`var(--gold-glow)`)
- White text
- Left-edge gold indicator bar (3px × 22px)

**Disabled Items:**
- 35% opacity
- `cursor: not-allowed`
- "Soon" badge in gold pill

**Sidebar Behavior:**
- On screens < 768px: hidden by default, revealed via hamburger
- No collapse-to-icons state (too few items to justify)

### 4.2 Header (68px, persistent top)

**Left:**
- Logo icon: 40×40px, gold gradient, "CV" text
- Product name: "CAR VALUATOR" in gradient text (white → gold)

**Right:**
- Notification bell (icon button, 40×40px)
- Language toggle: EN | AR pill button

**Header Behavior:**
- Sticky at top
- Glass effect: `backdrop-filter: blur(16px) saturate(180%)`
- Semi-transparent background: `rgba(13, 15, 21, 0.85)`

---

## 5. Page Specifications — FILLED DECISIONS

---

## 5.1 LANDING PAGE (Home) — 25 Decisions

### D01 — Hero Layout
**Decision:** Centered hero with live-status badge above, headline below, subtext below headline. No decorative graphics. The data IS the decoration.
**Hierarchy:** Live badge → headline → subtext → data ribbon → action cards.
**Why:** Enterprise buyers don't want marketing fluff. Lead with live data proving the platform is real and working.

### D02 — Hero Headline
**Decision:** "GCC Automotive Intelligence Platform" on line 1, gradient text (white → gold).
**Why:** States what it is, not what it does. Bloomberg doesn't say "We show you stock prices."

### D03 — Hero Subtext
**Decision:** One line: "Real-time valuations across 6 countries, 10 marketplaces, [live_count] active listings." The listing count is live-fetched.
**Why:** Social proof through data, not testimonials.

### D04 — Live Status Badge
**Decision:** Green pulsing dot + "Live GCC Market Data" in uppercase micro text. Fetches `/v1/health` on load. Dot pulses via CSS animation (2s ease-in-out infinite).
**Why:** Immediate trust signal. User knows data is real, not stale.

### D05 — KPI Data Ribbon
**Decision:** 4 KPI cards in a horizontal row, each with: label (uppercase micro), value (H3 weight), trend indicator (up/down arrow + text). Values fetched from `/v1/admin/stats`.
**Cards:**
1. Active Listings — number + "▲ X active" in green
2. Valuations (7d) — number + "▲ Last 7 days" in green
3. Countries Covered — "6" + "▲ GCC-wide" in green
4. Marketplaces — "10" + "▲ Live sources" in green
**Why:** Enterprise dashboards lead with KPIs. This is the Bloomberg influence.

### D06 — KPI Loading State
**Decision:** Skeleton cards (3:1 aspect ratio shimmer) until data loads. Replace with actual values via fade-in transition.
**Why:** Perceived performance. Layout doesn't jump.

### D07 — KPI Empty State
**Decision:** If `/v1/admin/stats` fails: show "—" for values, "Data unavailable" for trends in muted text. Do not show error toasts on the landing page (too aggressive).
**Why:** Graceful degradation. Landing page should never look broken.

### D08 — Action Cards (Sell / Buy)
**Decision:** Two side-by-side cards below the KPI ribbon. Each card has: icon (gold gradient circle, 56×56px), title (H3), description (body, muted), CTA text (gold, with arrow). Cards elevate on hover (translateY(-4px) + gold glow).
**Layout:** Equal width, 1fr 1fr grid.
**Why:** Binary choice is the simplest UX. One click to start either workflow.

### D09 — Sell Card Content
**Decision:** Icon: dollar sign. Title: "I'm Selling". Description: "Discover your car's true market value with real-time comparable analysis across the entire GCC." CTA: "Get Market Value →"
**Why:** Action-oriented. "Get Market Value" is a promise, not a feature description.

### D10 — Buy Card Content
**Decision:** Icon: cart. Title: "I'm Buying". Description: "Verify if a deal is fair with instant market comparison. Find better alternatives and save thousands." CTA: "Analyze This Deal →"
**Why:** Same pattern. "Save thousands" is the value proposition.

### D11 — Action Card Hover
**Decision:** 180ms ease transition. Card elevates 4px, border turns gold (`--border-active`), gold glow shadow appears. CTA text color intensifies from `--gold-light` to `--gold`.
**Why:** Subtle but clear affordance. Premium brands don't need dramatic hover effects.

### D12 — Trust Strip
**Decision:** Below the action cards, separated by a subtle border. Label: "Trusted by dealerships across the GCC" (micro, uppercase, muted). Row of marketplace name chips. Sub-line: "Aggregating real-time data from 10 marketplaces across 6 GCC countries" (caption, muted).
**Why:** Enterprise buyers need reassurance. Showing the data sources is honest and impressive.

### D13 — Marketplace Chips
**Decision:** 8 chips: Dubizzle, YallaMotor, Haraj, OpenSooq, CarSwitch, Emirates Auction, Syarah, DubiCars. Each chip: subtle background, subtle border, muted text. No logos (yet — future enhancement). Hover: border lightens, text lightens.
**Why:** Shows coverage breadth without visual clutter.

### D14 — Footer (or lack thereof)
**Decision:** No traditional footer. The trust strip is the terminal element on the landing page. The sidebar footer serves as the persistent app footer.
**Why:** SaaS apps don't need copyright footers on the home screen.

### D15 — Responsive: Home (≥1340px)
**Decision:** Full sidebar visible. Hero centered with max-width 720px. KPI ribbon: 4 equal columns. Action cards: 2 columns.
**Why:** The "full" experience. Sidebar provides persistent navigation.

### D16 — Responsive: Home (768–1339px)
**Decision:** Sidebar collapses to icons (future) or hidden. KPI ribbon: 2×2 grid. Action cards: remain 2 columns if space allows, stack if not. Padding reduced to `--space-4`.
**Why:** Data density maintained; non-essential chrome sacrificed first.

### D17 — Responsive: Home (<768px)
**Decision:** Single column. KPI ribbon: 2×2 grid. Action cards: stacked. Hero font sizes reduced (H1 → 2rem instead of 3rem). Padding: `--space-3`.
**Why:** Mobile-first degradation. Core CTAs remain prominent.

### D18 — Motion: Home
**Decision:** No entrance animations. KPI values animate from 0 to final value on load (count-up effect, 600ms). Cards have subtle hover elevation (180ms). No scroll-triggered animations. No parallax.
**Why:** Enterprise tools don't use scroll animations. Count-up adds polish without feeling like marketing.

### D19 — Keyboard: Home
**Decision:** Tab order: skip link → sidebar links → action cards → marketplace chips. Enter/Space activates action cards (they're `<button>` elements, not `<div>`).
**Why:** Accessibility baseline.

### D20 — Analytics: Home
**Decision:** All KPI clicks, action card clicks, and sidebar clicks are trackable via data attributes. No PII. No cross-site tracking.
**Why:** Enterprise product teams need usage data. But this is implementation-detail — hooks only, no actual analytics SDK.

### D21 — Accessibility: Home
**Decision:** Heading hierarchy: H1 (hero headline), H2 ("What would you like to do?"), H3 (card titles). Live badge has `aria-label="Live market data available"`. KPI values have `aria-label` with full text (e.g., "1,234 active listings").
**Why:** Screen-reader users get the same information.

### D22 — CTA Hierarchy
**Decision:** Action cards are the primary CTAs. KPI ribbon is informational (non-interactive). Trust strip is passive.
**Why:** The binary choice (Sell/Buy) is the most important action on the home page.

### D23 — Brand Identity: Home
**Decision:** No car photos. No stock imagery. No illustrations. The brand is communicated through typography, data, and the quality of the UI itself.
**Why:** "Automotive identity through subtle imagery and data — not decoration." Photos date quickly and feel like classifieds sites.

### D24 — Theme Consistency: Home
**Decision:** Uses ONLY design tokens from Section 2. No one-off colors, no hardcoded spacing. The `--green` is used ONLY for the live dot and KPI trend arrows.
**Why:** Enforces the visual system.

### D25 — Loading Skeletons: Home
**Decision:** On initial load, show: skeleton badge (120×24px), skeleton heading (400×48px, 60% width), skeleton text (300×18px), 4 skeleton KPI cards (160×100px each, shimmer).
**Why:** Layout stability. Content never jumps.

---

## 5.2 SELL PAGE — 15 Decisions

### D01 — Page Header
**Decision:** Left: page title "Sell Your Car" (H1, gradient text) + subtitle "Get an accurate market valuation based on live GCC listings across 6 countries." (body, muted). Right: live market badge (green dot + "GCC Live Market" in uppercase micro).
**Why:** Consistent header pattern across all pages.

### D02 — Form Layout
**Decision:** Single card containing all form fields. No multi-step wizard. All fields visible at once.
**Why:** The form is short enough (5–7 fields) that pagination adds friction without benefit.

### D03 — Form Field Grouping
**Decision:** Three logical groups separated by subtle dividers:
- **Vehicle Identity:** Make, Model, Year (3 fields, 3-column row)
- **Condition:** Mileage (1 field, with optional label)
- **Market Context:** Spec (pre-filled "GCC"), City, Country (3 fields, 3-column row)
**Why:** Mental model grouping. Identity first, then condition, then location.

### D04 — Make/Model Autocomplete
**Decision:** Typeable text inputs (not selects). Debounced search (200ms). Dropdown shows up to 8 matching results with listing counts. Keyboard navigation: ↑↓ to move, Enter to select, Escape to close. Selecting a make enables the model field. Selecting a model triggers smart defaults.
**Why:** 12 brands × 32 models is too many for a `<select>`. Type-to-filter is faster.

### D05 — Year Input
**Decision:** Number input, min 1990, max current+1. On model selection, show common years as clickable chips below the field. Clicking a chip fills the year and suggests mileage estimate.
**Why:** Smart defaults reduce friction. Year chips are data-driven suggestions, not constraints.

### D06 — Mileage Input
**Decision:** Number input (0–1,000,000 km). Placeholder updates dynamically based on selected year (e.g., "e.g. 120,000 km" for a 2020 vehicle using the formula `(current_year - year) × 20,000`). Optional field.
**Why:** Intelligent placeholder communicates expected value without being prescriptive.

### D07 — Spec Input
**Decision:** Text input, pre-filled with "GCC", readonly with muted styling. GCC is the correct default for this market. Advanced: allow edit for non-GCC specs.
**Why:** 90%+ of Gulf market vehicles are GCC spec. Pre-filling saves effort.

### D08 — City Input
**Decision:** Typeable input with autocomplete from 25 GCC cities. Filtered by country selection if country is already chosen. Shows city name + country in dropdown.
**Why:** 25 cities is the right threshold for autocomplete over select.

### D09 — Country Input
**Decision:** Typeable input with autocomplete from 6 GCC countries. Shows country name + city count in dropdown (e.g., "UAE — 7 cities"). Selecting a country updates the city placeholder.
**Why:** Consistent autocomplete pattern. City count provides context.

### D10 — CTA Button
**Decision:** Full-width gold gradient button: "Calculate Market Value". 56px height. Hover: elevates 2px, stronger glow. Loading: button text changes to "Analyzing Market Data..." with a subtle pulse animation; button is disabled. Success: no button change (results appear below). Error: button re-enables; error toast appears.
**Why:** Clear action verb. Gradient draws attention. Loading state prevents double-submit.

### D11 — Form Validation
**Decision:** Client-side validation on submit: Make, Model, Year required. Show inline error messages below each field (red micro text, field border turns red). Do not validate on blur (too aggressive). Validate on submit only.
**Why:** Inline errors are more scannable than toasts. Validating on submit is less annoying than blur validation.

### D12 — Smart Defaults (Model Selected)
**Decision:** After model selection, fetch `/v1/models/{make}/{model}` for year data. Show "Common years: [2020 (245)] [2019 (198)] [2018 (156)]" as clickable chips. Clicking a chip fills the year and updates the mileage placeholder.
**Why:** Data-driven guidance without being prescriptive. User can ignore suggestions.

### D13 — Form Empty State
**Decision:** On first visit to Sell page, the form is empty with placeholder text in all fields. The CTA button is enabled (validation happens on click, not via disabled button).
**Why:** Disabled buttons create confusion ("why can't I click this?"). Let them click and show validation.

### D14 — Form Reset
**Decision:** No explicit reset button. Navigating away and back rebuilds the form fresh. The form is ephemeral — it serves one valuation.
**Why:** Enterprise forms don't need reset buttons. Navigation is the reset.

### D15 — Responsive: Sell Form
**Decision:** ≥768px: 3-column form rows. <768px: 2-column, then 1-column at <640px. Full-width button always.
**Why:** Form density adapts to available space without breaking.

---

## 5.3 BUY PAGE — 35 Decisions

### D01 — Buy Page Layout
**Decision:** Two-column layout: main form (flexible width) + right rail (320px fixed). Right rail is sticky (top: 24px). On screens < 1100px, rail collapses below main content.
**Why:** The rail provides persistent context (AI status, coverage, methodology) without cluttering the form. Sticky keeps it visible during scroll.

### D02 — Page Header
**Decision:** Left: page title "Buy a Car" (H1, gradient) + subtitle "Verify if the asking price is fair against live GCC market data." (body, muted). Right: live market badge.
**Why:** Same header pattern as Sell. Consistency across workflows.

### D03 — Form Section A: Asking Price
**Decision:** Prominent section with gold-tinted background (`var(--gold-glow)` at 3% opacity), gold left border. Label: "A. Asking Price". Input: large number field (56px height, 1.2rem font, bold), currency suffix "AED". This is the hero input for Buy — visually distinct from the vehicle fields below.
**Why:** The asking price is the key differentiator between Sell and Buy. It deserves visual prominence.

### D04 — Form Section B: Vehicle Details
**Decision:** Standard 3-column grid (Make, Model, Year). Mileage in a separate row or as a 4th field. Same autocomplete behavior as Sell.
**Why:** Same vehicle identity pattern. Consistency reduces cognitive load.

### D05 — Form Section C: Market Details
**Decision:** 3-column grid (Spec, City, Country). Same behavior as Sell.
**Why:** Identical to Sell. Users who use both workflows benefit from the consistency.

### D06 — CTA Button
**Decision:** Full-width gold gradient button: "Analyze This Deal". Same behavior as Sell CTA.
**Why:** "Analyze This Deal" is more specific than "Calculate Market Value" — it implies the comparison that differentiates Buy from Sell.

### D07 — URL Import Section
**Decision:** Below the form, a subtle divider with "Or paste a listing URL from any GCC marketplace" (caption, muted, centered). Below that, a secondary-style button: "🔗 Paste a listing URL". Clicking reveals an inline URL input + "Analyze This URL" button. The section has a gold-tinted dashed-border card.
**Why:** URL import is a power-user feature. Tucking it below the form keeps the primary flow clean while still accessible.

### D08 — URL Input
**Decision:** Full-width URL input, centered placeholder text, 54px height. On focus: gold border + glow. Supports URLs from Dubizzle, YallaMotor, Haraj, OpenSooq, and other GCC marketplaces.
**Why:** Simple, focused. URL is the only input needed for this flow.

### D09 — URL Validation
**Decision:** Client-side: check URL format (must start with http(s)://). Server-side: `/v1/valuate-url` returns success or error. If the site blocks scraping, show a friendly message: "This marketplace is currently blocking automated access. Please use the manual form instead."
**Why:** Honest error messages build trust. Offering the fallback is helpful, not blaming.

### D10 — URL Marketplace Detection
**Decision:** No client-side detection. The server parses the URL and identifies the source. The response includes `parsed_from_url.source` (future enhancement).
**Why:** Marketplace detection is server-side logic. Don't duplicate in the frontend.

### D11 — Right Rail: AI Engine Panel
**Decision:** Rail panel with title "AI Engine" (uppercase micro). Shows: green dot + "Statistical v1" (or current model), model type, data source, confidence level. All values are static or fetched from valuation metadata.
**Why:** Transparency about the AI builds trust. Users know what's powering their valuation.

### D12 — Right Rail: Market Coverage Panel
**Decision:** Rail panel with title "Market Coverage" (uppercase micro). Shows: 6 GCC country flags + names in a 2×3 grid. Below: "X listings tracked" (live from `/v1/admin/stats`) and "10 marketplaces".
**Why:** Reassures users about data breadth. This is an enterprise buying signal.

### D13 — Right Rail: Methodology Panel
**Decision:** Rail panel with title "Methodology" (uppercase micro). Short paragraph (caption, muted): "Fair market value is computed from comparable active listings across all GCC marketplaces, adjusted for mileage, specification, and location premiums."
**Why:** Enterprise buyers want to understand the methodology. One paragraph is enough — link to full docs for detail.

### D14 — Right Rail: System Health Panel
**Decision:** Rail panel with title "System Health" (uppercase micro). Shows: API latency (from `/v1/health`), data freshness ("Real-time" or "Updated X min ago"), overall status (green "Operational").
**Why:** Datadog/Palantir influence. System observability is part of the product experience.

### D15 — Rail Panel Styling
**Decision:** Each rail panel: `--bg-card` background, subtle border, 24px padding, 16px border-radius. 16px gap between panels. Panel titles: uppercase micro, muted, with bottom border separator.
**Why:** Consistent panel design. Clean separation between rail items.

### D16 — Rail Loading State
**Decision:** Rail panels load with skeleton content (2–3 shimmer lines per panel). Health dot is skeleton circle. Values populate asynchronously after page load.
**Why:** Rail data is non-blocking. Show the structure immediately, fill in values as they arrive.

### D17 — Rail Empty State
**Decision:** If stats fetch fails: show "—" for values. Health dot turns amber with "Status unknown." No toast.
**Why:** Rail is secondary information. Failures should be visible but not alarming.

### D18 — Buy Form Validation
**Decision:** Must fill: asking price, make, model, year. Same inline validation pattern as Sell. Asking price must be > 0.
**Why:** Asking price is the key field. Without it, the deal analysis can't work.

### D19 — Buy Loading State
**Decision:** After clicking "Analyze This Deal": the form area shows a loading card with spinner + "Searching for better deals..." The rail remains visible. Results replace the loading card when ready.
**Why:** Loading state in context. The rail provides visual anchor during loading.

### D20 — Buy Error State
**Decision:** If valuation fails: error card replaces loading card. Error message in red, with a "Try Again" ghost button. Form values preserved (user doesn't lose their input).
**Why:** Preserving form state respects the user's effort.

### D21 — URL Loading State
**Decision:** Same as form loading, but text changes to "Extracting vehicle details from listing..."
**Why:** Different loading message sets expectations (URL parsing is slower than direct form valuation).

### D22 — URL Error: Blocked
**Decision:** Specific error: "Dubizzle is blocking automated access. Please use the manual form instead." with the form fields preserved.
**Why:** Actionable error. Don't just say "failed" — give the next step.

### D23 — URL Error: Invalid
**Decision:** "Could not extract vehicle details from this URL. Please check the link and try again, or use the manual form."
**Why:** Distinguishes between "blocked" and "invalid" — different causes, different user actions.

### D24 — URL Error: Not a Listing
**Decision:** "This URL doesn't appear to be a vehicle listing. Please paste a direct link to a car listing page."
**Why:** Helps the user understand what went wrong.

### D25 — Buy Responsive: ≥ 1340px
**Decision:** Full two-column layout: form (flex) + rail (320px).
**Why:** Optimal layout for the Buy workflow.

### D26 — Buy Responsive: 1100–1339px
**Decision:** Rail collapses below the form. Form takes full width.
**Why:** Rail is secondary. Form is primary.

### D27 — Buy Responsive: < 768px
**Decision:** Single column. Form fields go 2-column, then 1-column. Rail is below the fold.
**Why:** Mobile users prioritize form completion over contextual information.

### D28 — Buy Keyboard Navigation
**Decision:** Tab order: asking price → make → model → year → mileage → spec → city → country → CTA → URL button. Rail is not in the tab order (it's informational).
**Why:** Form-first tab order for efficiency.

### D29 — Buy Analytics
**Decision:** Track: form completions, URL paste attempts, URL success/failure rate, rail panel interactions. All via data attributes (implementation hooks only).
**Why:** Buy flow is the primary conversion path. Needs measurement.

### D30 — Buy Accessibility
**Decision:** Form labels are `<label>` elements properly associated with inputs. Asking price has `aria-describedby` pointing to helper text. Rail panels have `aria-label` for screen readers. Live indicators have `aria-live="polite"`.
**Why:** Full keyboard + screen reader support.

### D31 — Asking Price Helper Text
**Decision:** Below the asking price input: "Enter the seller's asking price to see if it's a good deal" (caption, muted). Above-market verdicts show red; fair deals show green.
**Why:** Micro-copy sets expectations for what the field does.

### D32 — AI Hints in Form
**Decision:** After model selection, show year suggestions (same as Sell). No additional AI hints in Buy (the intelligence is in the results, not the form).
**Why:** The form should be quick. Intelligence belongs in the analysis.

### D33 — Form Section Dividers
**Decision:** Thin horizontal rules (`1px solid var(--border-subtle)`) between sections A, B, and C. Each section has a label ("A. Asking Price", "B. Vehicle Details", "C. Market Details") in uppercase micro.
**Why:** Clear visual hierarchy. The sections tell a story: price → vehicle → location.

### D34 — Trust Badges
**Decision:** No trust badges on the Buy page. The rail's Market Coverage and Methodology panels serve this function more credibly.
**Why:** "Trusted by X dealerships" badges feel like marketing. Data about coverage is factual trust-building.

### D35 — Breadcrumb
**Decision:** No breadcrumb on Buy page. The sidebar active state provides sufficient navigation context.
**Why:** Breadcrumbs add visual noise for a 5-page app. The sidebar IS the navigation.

---

## 5.4 RESULTS PAGE — 15 Decisions

### D01 — Results Layout
**Decision:** Full-width stacked layout (no rail). Sections in order: Valuation Hero → Deal Verdict (buy only) → Market Position → Comparable Listings → AI Explanation → Actions. Each section is a card.
**Why:** Results are the product. They deserve full width. The rail was for the form context; results stand alone.

### D02 — Valuation Hero
**Decision:** Centered. Large price: "AED 127,350" in 3.5rem Display weight, gold gradient text. Below: "Market Range: AED 112,000 – AED 145,000" (body, muted). Below that: confidence ring (SVG, 64×64px) with label ("HIGH CONFIDENCE" in green/amber/red) and sub-label ("based on 23 comparable listings").
**Why:** The valuation amount is the most important number on the page. It should dominate visually.

### D03 — Price Animation
**Decision:** Price counts up from 0 to final value on display (600ms, easing-out). Range and confidence ring fade in after count-up completes (300ms delay).
**Why:** Count-up animation adds polish and draws attention to the result.

### D04 — Confidence Gauge
**Decision:** SVG donut chart (64×64px). Green (#10B981) for HIGH, Amber (#F59E0B) for MEDIUM, Red (#EF4444) for LOW. Stroke dash-array animates to confidence percentage over 1s. Label shows confidence level in uppercase. Sub-label shows comp count.
**Why:** Visual confidence indicator is faster to parse than a number. Color coding maps to urgency (red = careful, green = reliable).

### D05 — Deal Verdict (Buy Only)
**Decision:** If asking price provided: colored card at the top of results.
- **Above Market** (red background, red border): "ABOVE MARKET" label + "+X% above market" in large red text + "Asking: AED X vs Market: AED Y"
- **Fair Deal** (green background, green border): "FAIR DEAL" label + "Within market range" in green
- **Great Deal** (green background, green border): "GREAT DEAL" label + "−X% below market" in large green text + savings amount
**Why:** The verdict answers the buyer's core question: "Is this a good deal?" It should be impossible to miss.

### D06 — Market Position (Range Bar)
**Decision:** Horizontal range bar showing percentile distribution.
- Track: full width, subtle background
- Fill: gold gradient between P10 and P90
- Marker: gold circle at the estimate position
- If buying: red marker at the asking price position (if different from estimate)
- Labels: P10, P25, P50 (estimate), P75, P90 values in JetBrains Mono below the bar
**Why:** Bloomberg-style distribution visualization. Shows where the vehicle sits in the market, not just a single number.

### D07 — Stat Bar (Below Range)
**Decision:** 4 stats in a horizontal row: Comparable Listings count, Segment Median price, 80% CI Low, 80% CI High. Each stat: large number + micro label.
**Why:** Key metrics in one scannable row. The details behind the hero number.

### D08 — Comparable Listings
**Decision:** Card with up to 8 listings. Each listing: price (JetBrains Mono, bold) → year · mileage · spec · city (caption, muted) → source badge (gold pill with marketplace + city). Hover: subtle background highlight. Sorted by relevance score.
**Why:** Comparable listings are the evidence for the valuation. They should be scannable but detailed.

### D09 — Comparable Listings: Empty
**Decision:** If 0 comps: "No comparable listings found for this vehicle configuration." in empty-state pattern. Suggests broadening search criteria.
**Why:** Honest about data limitations.

### D10 — Better Deals (Buy Only)
**Decision:** If asking price is above market: green-bordered card showing 3 cheaper alternatives. Each alternative: price (bold), year · mileage · spec · city (caption), "SAVE AED X" badge (green), source line. Sorted by savings amount.
**Why:** Actionable intelligence. "This deal is bad" is useful. "Here are 3 better ones" is valuable.

### D11 — AI Explanation (Adjustments)
**Decision:** Card titled "How We Calculated This". Each adjustment: reason (bold, body), detail (caption, muted), amount (+AED X in green or −AED X in red, JetBrains Mono). Separated by subtle borders. Collapsible if > 5 adjustments (show first 5, "Show all N adjustments" button).
**Why:** Transparency builds trust. Every adjustment is a data point, not a black box.

### D12 — AI Explanation: Empty
**Decision:** If no adjustments: "This valuation is based directly on comparable listings with no adjustments needed." (caption, muted).
**Why:** "No adjustments" is itself useful information.

### D13 — Action Buttons
**Decision:** Three ghost buttons centered below all cards: Export (download icon), Share (share icon), Watchlist (heart icon). All are non-functional "coming soon" placeholders (opacity: 0.5, cursor: default). They communicate future capability without promising a date.
**Why:** Shows product maturity aspirations. Don't build features that aren't backed by APIs.

### D14 — Results: Sell vs Buy Differences
**Decision:**
- **Sell results:** No deal verdict. No better deals. Focus on market value + comparables + explanation.
- **Buy results:** Includes deal verdict, better deals section. Focus on deal quality.
**Why:** Same data, different framing. Sellers care about market value. Buyers care about deal quality.

### D15 — Results: Confidence-Based Behavior
**Decision:**
- **HIGH:** Full results. All sections shown. Green confidence ring.
- **MEDIUM:** Full results, but confidence ring is amber. "Medium confidence" label. All sections shown but comp count may be lower.
- **LOW:** Results shown with amber/red confidence. Warning text: "Limited comparable data available. Consider this an estimate, not a guarantee."
- **INSUFFICIENT:** HTTP 422 error returned by API. Show error card with explanation: "Not enough comparable listings for this vehicle. Try a more common make/model or broader criteria."
**Why:** Confidence transparency. Users should know how much to trust the number.

---

## 5.5 BROWSE PAGE — 15 Decisions

### D01 — Browse Layout
**Decision:** Full-width. Toolbar at top, results grid below. Three-level drill-down: Makes → Models → Years. Each level replaces the previous (breadcrumb navigation back).
**Why:** Progressive disclosure. 12 makes × 32 models × ~20 years = too much data to show at once.

### D02 — Browse Toolbar
**Decision:** Horizontal bar with: search input (left, with magnifying glass icon), country filter (select, right), sort dropdown (select, right). 48px height inputs.
**Why:** Filter before browse. Reduces the result set before the user sees it.

### D03 — Search Input
**Decision:** Text input with search icon. Filters the visible grid in real-time as the user types (200ms debounce). Searches make name. Placeholder: "Search makes..."
**Why:** Real-time filtering is faster than submit-on-enter for a small dataset.

### D04 — Country Filter
**Decision:** Select dropdown: "All GCC Countries" (default), then AE, SA, KW, QA, BH, OM each with flag emoji. Filters makes/models/years to show only listings from that country.
**Why:** Country is the primary market segmenter in GCC.

### D05 — Sort Options
**Decision:** Select dropdown: "Sort: Name" (default, alphabetical), "Sort: Most Listings" (by listing count descending).
**Why:** Two sort modes cover the two most common browse intents: "I know the brand" and "What's popular?"

### D06 — Make Cards Grid
**Decision:** CSS Grid: `repeat(auto-fill, minmax(180px, 1fr))`. Each card: make name (bold, body), model count + listing count (caption, muted), listing count (JetBrains Mono, gold). Hover: border turns gold, elevates 2px, subtle gold glow.
**Why:** Auto-fill grid adapts to screen width. Make cards are the entry point — they should be inviting.

### D07 — Make Card: Empty Search
**Decision:** "No manufacturers found matching '[search term]'" in empty-state pattern. Suggests clearing the filter.
**Why:** Clear feedback. Don't just show an empty grid.

### D08 — Models List (Level 2)
**Decision:** After clicking a make: back button ("← All Manufacturers"), make name in gold. List of models as row-links: model name (bold, body) → year range (caption, muted) → listing count (JetBrains Mono, gold, right-aligned). Each row clickable. Hover: subtle background highlight.
**Why:** Row-links are more scannable than cards for a list of models. The year range adds context.

### D09 — Models List: Empty
**Decision:** "No models found for [make] in [country]" if country filter is active. Suggests clearing the country filter.
**Why:** Actionable empty state.

### D10 — Years List (Level 3)
**Decision:** After clicking a model: back button ("← All Models"), "Make Model" in gold. List of years as row-links: year (bold, body) → trims (caption, muted, comma-separated) → listing count (JetBrains Mono, gold, right-aligned). Each row has a "Value This →" ghost button on the right that navigates to the Sell page with those fields pre-filled.
**Why:** The year drill-down is the terminal level. "Value This" connects browsing to action.

### D11 — Years List: Empty
**Decision:** "No listings found for [make] [model] in [country]." Suggests clearing filters.
**Why:** Consistent empty-state pattern.

### D12 — Back Navigation
**Decision:** Back buttons at the top of models and years views. Clicking "← All Manufacturers" returns to makes grid. Clicking "← All Models" returns to models list. Browser back button is NOT intercepted (this is a SPA, not a routed app).
**Why:** Clear escape hatches at every drill-down level.

### D13 — Browse: Responsive
**Decision:** ≥768px: toolbar horizontal, grid 4+ columns. <768px: toolbar stacks (search full width, filters below), grid 2 columns. <640px: grid 1 column.
**Why:** Filter-first on mobile. Search is the primary tool; filters are secondary.

### D14 — Browse: Loading
**Decision:** On first load: skeleton grid (8 skeleton cards, shimmer). On drill-down: skeleton rows (6 shimmer lines). On filter change: instant client-side filter for makes; brief loading for models/years fetch.
**Why:** Initial load needs skeleton. Drill-down can be faster (data may already be cached).

### D15 — Browse: Pagination
**Decision:** No pagination. All makes fit on one page. All models for a make fit on one page. Years for a model fit on one page. If a make has > 50 models in the future, add pagination then.
**Why:** Don't solve a problem that doesn't exist yet. Current data set is small.

---

## 5.6 MARKET PAGE — 15 Decisions

### D01 — Market Layout
**Decision:** Full-width stacked layout. Sections: KPI Row → Most Popular Makes → (future: Price Trends, Country Breakdown, Market Health).
**Why:** Dashboard-style vertical stack. Each section is a card.

### D02 — KPI Row
**Decision:** 4 stats in a horizontal stat bar: Total Listings, Active Listings, Valuations (7d), All-Time Valuations. Each: large number + micro label. Fetched from `/v1/admin/stats`.
**Why:** The "at a glance" market overview. Same pattern as the results stat bar.

### D03 — Most Popular Makes
**Decision:** Ranked table (1–10): rank number (JetBrains Mono, muted) → make name (body) → listing count (JetBrains Mono, right-aligned) → horizontal bar (gold gradient, proportional to the max). All 10 rows visible (no pagination).
**Why:** Bloomberg-style ranked list. The horizontal bar adds visual weight to the numbers.

### D04 — Price Trend Chart (Future)
**Decision:** Placeholder card with title "Price Trends" and empty-state message: "Historical price charts coming soon." Gold-bordered dashed card.
**Why:** Communicates roadmap without over-promising. The card structure is ready; data isn't.

### D05 — Country Breakdown (Future)
**Decision:** Placeholder card with title "Country Breakdown" and empty-state: "Geographic distribution analysis coming soon."
**Why:** Same pattern as D04. Placeholder cards make the page feel intentionally designed, not incomplete.

### D06 — Market Health Indicators (Future)
**Decision:** Placeholder card with title "Market Health" and empty-state: "Supply, demand, and liquidity metrics coming soon."
**Why:** Consistent future-feature pattern.

### D07 — Data Freshness Banner
**Decision:** Small banner below the KPI row: "Market data refreshed [X hours ago]. Next update: [scheduled time]." (caption, muted). Fetched from last pipeline run timestamp in `/v1/admin/stats`.
**Why:** Data transparency. Enterprise users need to know how fresh the data is.

### D08 — Refresh Mechanism
**Decision:** No auto-refresh. No manual refresh button. Data updates on page navigation. The freshness banner tells them when it was last updated.
**Why:** Market data changes weekly (pipeline runs), not in real-time. Auto-refresh would be misleading.

### D09 — Market: Loading
**Decision:** Skeleton KPI row (4 skeleton stat cards) + skeleton ranked list (10 shimmer rows with bar placeholders).
**Why:** Consistent skeleton pattern.

### D10 — Market: Empty
**Decision:** If stats fetch fails: KPI row shows "—" for all values. Ranked list shows empty-state: "Market data is currently unavailable. Please try again later."
**Why:** Graceful degradation. Never show a blank page.

### D11 — Market: Responsive
**Decision:** ≥768px: KPI row 4 columns, ranked list full width. <768px: KPI row 2×2 grid, ranked list full width. <640px: KPI row 1 column, ranked list with abbreviated info.
**Why:** KPI cards are the most important content. They adapt first.

### D12 — Insights Panel (Future)
**Decision:** Placeholder card for AI-generated market insights. Empty-state: "AI-powered market insights coming soon."
**Why:** Tees up future AI features without building them.

### D13 — Export Functionality
**Decision:** No export buttons. Enterprise reporting is a future phase.
**Why:** Don't show buttons that don't work. "Coming soon" badges are for sidebar items; placeholder cards are for page content.

### D14 — Forecasts (Future)
**Decision:** Placeholder card for price forecasts. Empty-state: "Price prediction models coming soon."
**Why:** Consistent placeholder pattern.

### D15 — Market Page: No User-Configurable Date Range
**Decision:** Data shown is current market snapshot. No date picker, no time range selector. Weekly pipeline runs means weekly granularity — a date picker would imply daily precision we don't have.
**Why:** Honest about data granularity. Don't build UI for data that doesn't exist.

---

## 5.7 REPORTS PAGE (Phase 8) — 15 Decisions

### D01–D15
**Decision:** All 15 decisions deferred to Phase 8. The page exists as a sidebar item with "Soon" badge. Full specification will be written when the Reports feature is ready for implementation.
**Preliminary direction:** Downloadable PDF reports with valuation history, market trends, and portfolio analysis. Bloomberg-style report builder. Dealer-facing.

---

## 5.8 SETTINGS PAGE (Phase 8) — 15 Decisions

### D01–D15
**Decision:** All 15 decisions deferred to Phase 8. The page exists as a sidebar item with "Soon" badge.
**Preliminary direction:** User profile, API key management, notification preferences, language/region defaults, theme (dark only — no light mode).

---

## 6. Component Library — Detailed Specs

### 6.1 Buttons

| Variant | Background | Border | Text | Hover | Disabled |
|---------|------------|--------|------|-------|----------|
| Primary | Gold gradient | None | White, 600 weight | Elevate 2px, stronger glow | 50% opacity, grayscale |
| Secondary | Transparent | 1px dashed `--border-hover` | `--text-secondary` | Gold border, light bg | 35% opacity |
| Ghost | Transparent | Transparent | `--text-secondary` | Light bg, white text | 35% opacity |
| Icon | Transparent | 1px `--border-subtle` | `--text-secondary` | Elevated bg, white text | 35% opacity |
| Danger | `--red-bg` | 1px `rgba(239,68,68,0.2)` | `--red` | Darker red bg | 50% opacity |

**Sizing:** Primary: 56px height, full width. Secondary/Ghost: 40–48px height, auto width. Icon: 40px × 40px.

### 6.2 Inputs

**All inputs:**
- Height: 54px
- Border: 1.5px `--border-default`
- Border-radius: 12px (`--radius-md` → corrected to 12px for inputs specifically)
- Background: `rgba(0,0,0,0.25)`
- Padding: 14px 16px
- Font: Inter, 0.92rem (body)
- Placeholder: `rgba(255,255,255,0.2)`
- Focus: Gold border + `0 0 0 3px var(--gold-glow)` box-shadow
- Hover: Border lightens to `rgba(255,255,255,0.1)`
- Disabled: 50% opacity, `cursor: not-allowed`
- Error: Red border + red glow

### 6.3 Cards

**Standard Card:**
- Background: `--bg-card` with subtle glass gradient
- Border: 1px `rgba(255,255,255,0.05)`
- Border-radius: 16px
- Padding: 40px 48px
- Hover: Border lightens to `rgba(255,255,255,0.08)`
- Card heading: uppercase micro, muted, bottom border

**KPI Card:**
- Background: `--bg-card`
- Border: 1px `--border-subtle`
- Border-radius: 16px
- Padding: 24px 32px
- Hover: Border to `--border-hover`, subtle shadow

**AI Insight Card:**
- Like standard card but with gold left border (3px)
- Subtle gold tint background: `linear-gradient(135deg, var(--gold-glow), transparent)`

**Vehicle Card:**
- For browse grids. Make name + listing count.
- Border-radius: 12px
- Padding: 24px
- Hover: Gold border + elevate 2px

**Listing Card:**
- For comparable listings. Price + metadata + source badge.
- Padding: 14px 0 (inline rows)
- Subtle bottom border between items

**Empty State Card:**
- Centered content, icon (64px circle), heading, description, optional CTA
- Padding: 64px 32px

### 6.4 Data Components

**Enterprise Table:**
- Full width, collapsed borders
- Sticky header with uppercase micro labels
- Rows: 12px 16px padding, subtle bottom border
- Row hover: `rgba(255,255,255,0.02)` background
- Sortable columns: click header to toggle asc/desc (future)

**Badges:**
- Pill shape (border-radius: 20px)
- Uppercase micro, 700 weight
- HIGH/good: green bg + green text (+ green left border for cards)
- MEDIUM/warning: amber bg + amber text
- LOW/bad: red bg + red text
- Neutral: subtle bg + muted text
- Gold: gold-glow bg + gold-light text (for marketplace sources)

**Sparklines:**
- SVG-based mini line charts
- 80×24px viewBox
- Gold stroke, no fill
- Last data point: gold dot (3px radius)
- For KPI cards, market trends, vehicle price history

**Tooltips:**
- Dark elevated background (`--bg-elevated`)
- 1px subtle border
- 12px border-radius
- 12px 16px padding
- Caption text
- Appear on hover (200ms delay)
- 8px offset from trigger element

**Toasts:**
- Fixed top-right, stacked with 8px gap
- Slide in from right (300ms), auto-dismiss (10s), slide out
- Error: red gradient. Warning: amber gradient. Success: green gradient
- Max width: 420px
- Clickable to dismiss

**Modals (Future):**
- Centered overlay with backdrop blur
- 560px max width
- 24px padding
- Gold focus ring trap
- Escape to close

### 6.5 Charts (Future Phase)

**Data visualization rules:**
- Gold primary series, gray secondary series
- Green for positive, red for negative
- No gradient fills (solid colors only)
- No 3D effects
- No pie charts (use bar or donut)
- Always show axes labels and data source
- JetBrains Mono for all numeric labels

---

## 7. Motion & Interaction

### 7.1 Transition Scale

| Duration | Easing | Usage |
|----------|--------|-------|
| 80ms | ease | Instant feedback (button press, checkbox) |
| 150ms | ease | Fast transitions (hover color, icon change) |
| 180ms | ease | **Default** (hover elevation, border change, expand) |
| 280ms | ease | Slow transitions (modal open, drawer) |
| 400ms | ease | Glacial (page sections appear, count-up animation) |

### 7.2 Interaction Patterns

**Hover:** 180ms ease to target state. Cards elevate 2–4px. Borders lighten. Backgrounds shift subtly.
**Focus:** Instant gold ring (no animation on focus — it's an accessibility feature, not decoration).
**Active/Press:** Instant. Button depresses. Card loses elevation.
**Loading:** Skeleton shimmer (1.5s infinite). No spinners except for sub-500ms operations.
**Page transitions:** None. Instant page swap. Content sections within a page fade in (280ms, staggered 50ms per section).

### 7.3 Accessibility Requirements

- All interactive elements: visible focus ring (gold, 2px + 3px glow)
- Focus order matches visual order
- Keyboard navigable (Tab, Shift+Tab, Enter, Space, Escape, Arrow keys in autocomplete)
- `prefers-reduced-motion`: disable all animations (instant transitions, no count-up, no shimmer)
- Minimum contrast: 4.5:1 for body text, 3:1 for large text (18px+ bold)
- All images/icons: `aria-hidden="true"` (decorative only)
- All data elements: `aria-label` with human-readable values

---

## 8. Implementation Roadmap

### Phase 1: Foundations (Week 1)
- Extract CSS to `ui/styles.css`
- Harden design tokens (add missing tokens, audit all existing)
- Clean up zombie files
- Add JS error boundaries and API client helper
- **Deliverable:** Clean project structure, no visible changes

### Phase 2: Navigation (Week 1, continued)
- Refine sidebar (active states, profile card, system health)
- Refine header (logo, language toggle)
- **Deliverable:** Polished navigation chrome on all pages

### Phase 3: Landing Page (Week 2)
- Transform home page per Section 5.1 (25 decisions)
- **Deliverable:** Enterprise command center landing

### Phase 4: Buy Flow (Week 3)
- Transform Buy page per Section 5.3 (35 decisions)
- **Deliverable:** Premium deal analysis experience

### Phase 5: Results Page (Week 4)
- Transform results rendering per Section 5.4 (15 decisions)
- **Deliverable:** Bloomberg-quality valuation display

### Phase 6: Sell Flow (Week 4, continued)
- Transform Sell page per Section 5.2 (15 decisions)
- **Deliverable:** Consistent form experience across Sell and Buy

### Phase 7: Browse Page (Week 5)
- Transform Browse per Section 5.5 (15 decisions)
- **Deliverable:** Premium vehicle discovery

### Phase 8: Market Page (Week 6)
- Transform Market per Section 5.6 (15 decisions)
- **Deliverable:** Market intelligence dashboard

### Phase 9: Polish (Week 7)
- RTL (Arabic) audit and fixes
- Responsive audit at all breakpoints
- Keyboard navigation audit
- Screen reader audit
- Performance pass
- **Deliverable:** Production-ready enterprise application

---

## 9. Appendix A — Design Token Reference (Complete)

### Surface Palette
| Token | Value | CSS Variable |
|-------|-------|-------------|
| Primary bg | `#0B0D12` | `--bg-primary` |
| Secondary bg | `#0D0F17` | `--bg-secondary` |
| Card bg | `#131720` | `--bg-card` |
| Card hover | `#181D28` | `--bg-card-hover` |
| Elevated bg | `#1A1F2B` | `--bg-elevated` |
| Input bg | `rgba(0,0,0,0.25)` | `--bg-input` |

### Border Scale
| Token | Value | CSS Variable |
|-------|-------|-------------|
| Subtle | `rgba(255,255,255,0.04)` | `--border-subtle` |
| Default | `rgba(255,255,255,0.06)` | `--border-default` |
| Hover | `rgba(255,255,255,0.10)` | `--border-hover` |
| Active | `rgba(200,169,81,0.30)` | `--border-active` |
| Focus | `rgba(200,169,81,0.45)` | `--border-focus` |

### Accent Gold
| Token | Value | CSS Variable |
|-------|-------|-------------|
| Gold | `#C8A951` | `--gold` |
| Gold dark | `#A8882E` | `--gold-dark` |
| Gold light | `#D4B55A` | `--gold-light` |
| Gold glow | `rgba(200,169,81,0.15)` | `--gold-glow` |
| Gold glow strong | `rgba(200,169,81,0.28)` | `--gold-glow-strong` |

### Semantic
| Token | Value | CSS Variable |
|-------|-------|-------------|
| Green | `#10B981` | `--green` |
| Green bg | `rgba(16,185,129,0.10)` | `--green-bg` |
| Red | `#EF4444` | `--red` |
| Red bg | `rgba(239,68,68,0.10)` | `--red-bg` |
| Amber | `#F59E0B` | `--amber` |
| Amber bg | `rgba(245,158,11,0.10)` | `--amber-bg` |
| Info | `#3B82F6` | `--info` |
| Info bg | `rgba(59,130,246,0.10)` | `--info-bg` |

### Typography
| Token | Value | CSS Variable |
|-------|-------|-------------|
| Display | `3rem` (48px) | `--text-display` |
| H1 | `2.5rem` (40px) | `--text-h1` |
| H2 | `2rem` (32px) | `--text-h2` |
| H3 | `1.5rem` (24px) | `--text-h3` |
| Section | `1.125rem` (18px) | `--text-section` |
| Body | `1rem` (16px) | `--text-body` |
| Caption | `0.8125rem` (13px) | `--text-caption` |
| Primary color | `#FFFFFF` | `--text-primary` |
| Secondary color | `#9CA3AF` | `--text-secondary` |
| Muted color | `#6B7280` | `--text-muted` |
| Accent color | `#D4B55A` | `--text-accent` |
| Inverse color | `#0B0D12` | `--text-inverse` |

### Spacing (8px grid)
| Token | Value |
|-------|-------|
| `--space-1` | 8px |
| `--space-2` | 16px |
| `--space-3` | 24px |
| `--space-4` | 32px |
| `--space-5` | 40px |
| `--space-6` | 48px |
| `--space-7` | 56px |
| `--space-8` | 64px |
| `--space-10` | 80px |
| `--space-12` | 96px |

### Radius
| Token | Value | Usage |
|-------|-------|-------|
| `--radius-xs` | 4px | Code, tiny badges |
| `--radius-sm` | 6px | Small buttons, chips |
| `--radius-md` | 10px | Buttons, inputs |
| `--radius-lg` | 12px | Cards, modals |
| `--radius-xl` | 16px | KPI cards, large cards |
| `--radius-2xl` | 20px | Hero cards |
| `--radius-full` | 9999px | Pills, badges, avatars |

### Shadows
| Token | Value |
|-------|-------|
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.18)` |
| `--shadow-sm` | `0 2px 4px rgba(0,0,0,0.22)` |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.30)` |
| `--shadow-lg` | `0 8px 32px rgba(0,0,0,0.40)` |
| `--shadow-xl` | `0 12px 48px rgba(0,0,0,0.50)` |
| `--shadow-glow` | `0 0 24px var(--gold-glow)` |

### Duration
| Token | Value | Usage |
|-------|-------|-------|
| `--duration-instant` | 80ms ease | Button press |
| `--duration-fast` | 150ms ease | Hover color |
| `--duration-base` | 180ms ease | Default transitions |
| `--duration-slow` | 280ms ease | Modal, drawer |
| `--duration-glacial` | 400ms ease | Page sections, count-up |

---

## 10. Appendix B — Page Checklist Summary

| Page | Decisions Filled | Decisions Deferred | Phase |
|------|-----------------|-------------------|-------|
| Landing (Home) | 25/25 | 0 | 3 |
| Sell | 15/15 | 0 | 6 |
| Buy | 35/35 | 0 | 4 |
| Results | 15/15 | 0 | 5 |
| Browse | 15/15 | 0 | 7 |
| Market | 15/15 | 0 | 8 |
| Reports | 0/15 | 15 (Phase 8) | Future |
| Settings | 0/15 | 15 (Phase 8) | Future |
| **Total** | **135** | **30** | — |

---

*Enterprise Design Bible v1.0 (Complete). All placeholder decisions filled 2026-07-12. Awaiting approval.*
