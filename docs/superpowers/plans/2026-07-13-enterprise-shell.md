# Enterprise Application Shell — Implementation Plan

**Goal:** Transform the frontend into a persistent application shell with 12-column grid, standardized cards, premium hero, and page-specific layouts per the Enterprise Design Specification.

**Architecture:** Single-file `ui/index.html`. All changes are CSS/HTML/JS only. Backend untouched.

## Global Constraints
- Zero backend/API/database changes
- Zero new dependencies
- One page to production quality before moving to the next
- Commit after each phase

---

## Phase 1: Design Foundation — Grid, Typography, Card System

**Why first:** Every subsequent phase depends on the grid and card system being correct.

### 1.1 12-Column Grid

Add CSS grid classes for the 12-column system:

```css
.grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: var(--space-3); }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-7 { grid-column: span 7; }
.col-10 { grid-column: span 10; }
.col-12 { grid-column: span 12; }
```

Sidebar (256px) + Main (1fr) — the sidebar is outside the grid. The grid applies WITHIN the main content area.

### 1.2 Typography Scale — Match Spec

Update `:root` tokens to match spec exactly:
- Hero: 52px (was 48px)
- Statistics: 32px (was 24px)
- Card Title: 18px (was 24px)
- Body: 14px (was 16px)
- Input: 14px (was 15px)
- Label: 12px (was 11px)
- Nav: 13px

### 1.3 Standardize Card Anatomy

Every card gets explicit Header/Body/Footer structure:

```css
.card-header { padding: var(--space-3) var(--space-3) 0; }
.card-body { padding: var(--space-3); }
.card-footer { padding: 0 var(--space-3) var(--space-3); }
```

24px padding on all sides. Nothing touches edges.

### 1.4 Header — Add Theme Toggle

Add a theme toggle button (moon/sun icon) next to the language toggle. Currently non-functional (only dark theme exists). Shows intent per spec.

### Commit
```
feat: design foundation — 12-column grid, typography scale, card anatomy, theme toggle placeholder
```

---

## Phase 2: Home Page — Premium Hero

### 2.1 Hero Background

The hero consists of layered elements:
1. Dark gradient background (bottom layer)
2. Dubai skyline silhouette (CSS or SVG)
3. Gold ambient glow (radial gradient behind vehicle)
4. SUV illustration (right half of hero)
5. Content layer (left side: badge, headline, subtitle, CTAs)

**Implementation approach:** CSS-only using layered backgrounds + pseudo-elements. No external images — use SVG inline for the skyline and vehicle silhouette, CSS gradients for glow.

### 2.2 Hero Content (Left Side)

- Live badge: green dot + "Live GCC Market Data"
- Headline: "GCC Automotive Intelligence Platform" (52px, 900 weight, gradient)
- Subtitle: one-line description
- Two CTA cards: "I'm Selling" + "I'm Buying" (side by side, floating above the hero bottom edge)

### 2.3 Statistics Row

Below hero: 4 KPI cards in a row (Active Listings, Valuations 7d, Countries Covered, Marketplaces)

### Commit
```
feat: premium home hero with vehicle illustration, skyline, gold glow, layered backgrounds
```

---

## Phase 3: Buy Page — Form + Right Panel

### 3.1 Layout

12-column grid within main content:
- Form area: columns 1-9 (spans 9)
- Right panel: columns 10-12 (spans 3)

### 3.2 Form Structure

Per spec sections:
```
Deal Analysis (header)
↓
A. Asking Price [input + AED]
↓
B. Vehicle Details [Make, Model, Year, Mileage]
↓
C. Market Details [Country, City, Spec]
↓
Analyze Button (gold CTA)
↓
Paste URL (secondary action)
```

### 3.3 Right Panel

Two widgets:
1. **AI Features** card: Real Time status, AI Engine model, Intelligence metrics, Confidence level
2. **Countries** card: UAE, Saudi, Qatar, Kuwait flags + names

### 3.4 Form Refinements

- Taller inputs (56px)
- Better label placement
- Gold focus states (already done)
- Clear section dividers

### Commit
```
feat: buy page — 9+3 column layout, structured form sections, AI panel, country coverage widget
```

---

## Phase 4: Results Page

### 4.1 Layout

Full-width (all 12 columns within main content). Stacked cards:
1. Fair Market Value hero card
2. Market Position metrics
3. Comparable Listings table
4. AI Explanation (adjustments)

No right panel — confidence and metrics integrated directly.

### 4.2 Value Hero Card

- "AED 285,000" in large type
- Confidence gauge integrated
- Market range below

### Commit
```
feat: results page — full-width stacked cards, value hero, integrated confidence
```

---

## Phase 5: Browse + Market Pages

### 5.1 Browse

Full-width (12 columns). Search toolbar → Brand chips → Vehicle cards grid.

### 5.2 Market

Full-width (12 columns). KPI metrics row → Price trend chart → Top Makes table + Market Insights side by side.

### Commit
```
feat: browse and market pages — 12-column layouts, refined cards
```

---

## Phase 6: Polish

- Verify 8pt grid on every element
- 80/15/5 color distribution audit
- Card anatomy consistency check
- Responsive breakpoints
- Final commit

---

## Verification Per Phase

- [ ] All 5 pages load without console errors
- [ ] Sidebar + header persist across navigation
- [ ] Cards follow Header/Body/Footer pattern with 24px padding
- [ ] 12-column grid alignment verified
- [ ] Gold usage ≤ 15% of visible surface area
- [ ] Green ONLY on live indicators / positive metrics
- [ ] All API calls succeed
- [ ] No backend changes

---

*Plan ready. 6 phases, each produces a reviewable commit.*
