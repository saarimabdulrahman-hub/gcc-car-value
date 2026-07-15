# Buy a Car Page — Blueprint Implementation Plan

**Source:** `Buy_A_Car_UI_Reverse_Engineering_Blueprint.zip` (21 documents)
**File:** `ui/index.html` only
**Rule:** No backend changes. No other page changes.

## Global Constraints
- Modify only `#page-buy` HTML, Buy-related CSS, and Buy-related JS
- Preserve all existing form functionality (buildForm, doValuation, doUrlValuation, etc.)
- All existing API calls preserved
- Commit after each task

---

## Task 1: Color System & Design Tokens — Buy Page Specific

Align the Buy page with the blueprint color system. The blueprint specifies distinct surface colors different from the home page.

**Colors to apply to Buy page area:**
- Card backgrounds: `#151B23` (currently `--bg-card: #171A23`)
- Input backgrounds: `#10151B` (currently `--bg-input: rgba(0,0,0,0.25)`)
- Panel backgrounds: `#11161D` (rail panels)
- Accent Gold: `#C89435` (primary CTA, focus rings)
- Success green: `#00D66B` (live indicators)

Approach: Add Buy-page-specific CSS variable overrides within `.buy-layout` scope, or add new tokens.

**Commit:** `feat: apply blueprint color system to Buy page`

---

## Task 2: Grid Layout — 220px + 670px + 250px

Replace the current 9+3 grid with the blueprint's precise three-pane layout.

**Grid spec:**
- Sidebar: 220px (already exists, verify)
- Main workspace: ~670px
- Right panel: 250px
- Gutters: 24px (--space-3)
- Container max-width: ~1140px

Use `.grid-12` with adjusted column proportions or a specific Buy page grid.

**Commit:** `feat: apply blueprint grid layout to Buy page`

---

## Task 3: Card System — 14px Radius, 24px Padding

Apply blueprint card specs to all Buy page cards:
- Border-radius: 14px (--radius-lg is 12px, need 14px)
- Padding: 24px (--space-3)
- Subtle border, soft elevation
- Form card (Deal Analysis), URL card, right panel cards

**Commit:** `feat: apply blueprint card system to Buy page cards`

---

## Task 4: Input System — 48px Height, Icons, Gold Focus

Apply blueprint input specs:
- Height: 48px (currently 54px)
- Border-radius: 10px (--radius-md)
- Gold focus ring
- Muted placeholders
- Input icons where specified

**Commit:** `feat: apply blueprint input system to Buy page form`

---

## Task 5: Form Structure — Sections, CTA, URL Card

Restructure form per blueprint:
1. Deal Analysis card header
2. Asking Price section with currency
3. Vehicle Details (4-column grid: Make, Model, Year, Mileage)
4. Market Details (3-column grid: Country, City, Spec)
5. Primary CTA — full-width gold gradient button, sparkle icon, trailing arrow
6. URL import card below

**Commit:** `feat: restructure Buy form per blueprint section flow`

---

## Task 6: Right Panel — AI Card + Market Coverage Card

Restructure right panel per blueprint:
- Width: 250px, sticky
- AI Capabilities card
- Market Coverage card
- Remove extra panels (Methodology, System Health)

**Commit:** `feat: restructure right panel per blueprint`

---

## Task 7: Typography — Title, Labels, Inputs, Button

Apply blueprint typography:
- Page title: 34px / 700 weight
- Section labels: 12px uppercase
- Input text: 14px / 500 weight
- Button text: 15px / 600 weight

**Commit:** `feat: apply blueprint typography to Buy page`

---

## Task 8: Polish — Spacing, Depth, Final Review

Apply blueprint spacing tokens (4, 8, 12, 16, 20, 24, 32, 40, 48, 64) throughout Buy page elements. Verify depth system: Background → Cards → Inputs → Buttons → Hover.

**Commit:** `feat: Buy page spacing and depth polish per blueprint`

---

## Verification
- [ ] Buy page loads without JS errors
- [ ] Form submission works (doValuation → results)
- [ ] URL import works (doUrlValuation)
- [ ] Rail panels populate on load
- [ ] Grid collapses correctly at 1100px
- [ ] All other pages unaffected
