# Gap Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the 10 highest-priority gaps between the Enterprise Design Bible spec and the actual frontend implementation — keyboard accessibility, ARIA semantics, form validation, and visual polish.

**Architecture:** Four phases ordered by impact-per-effort ratio. Phase 1 bundles all tiny/small fixes (7 gaps in one pass). Phase 2 addresses form validation UX. Phase 3 fixes the largest visual bugs. Phase 4 reduces inline style debt in `showResults()`. All changes are in `ui/index.html` only. No backend, no API, no new dependencies.

**Tech Stack:** Vanilla HTML/CSS/JS. Single file `ui/index.html`. Zero build toolchain.

## Global Constraints

- Do NOT change any Python files, API endpoints, or database schemas
- Do NOT add npm, webpack, Vite, or any build dependencies
- Do NOT introduce React, Vue, or any framework
- All changes are additive-to-existing-functionality (no regressions)
- Test by loading `http://localhost:8000` in browser after each task
- Commit after each task with descriptive message
- `ui/index.html` is the ONLY file modified

---

### Task 1: Accessibility Quick Wins — ARIA, focus, lang, SVG, confidence ring

**Files:**
- Modify: `ui/index.html` (scattered edits across CSS, HTML, JS sections)

**Interfaces:**
- Consumes: Existing DOM structure, existing JS functions
- Produces: Keyboard-accessible clickable elements, screen-reader-friendly markup, correct `html[lang]`, accurate confidence ring

#### Step 1: Add `role="button"` and `tabindex="0"` to all clickable `<div>` elements

The choice cards, browse chips, and year-action buttons are `<div>` or `<span>` elements with `onclick` but no ARIA role. Screen readers don't recognize them as buttons. Keyboard users can't Tab to them.

In the HTML section, find the choice cards. Replace their opening tags:

**Find:** `<div class="choice-card" onclick="goPage('sell',...`
**Replace with:** `<div class="choice-card" role="button" tabindex="0" onclick="goPage('sell',...`
**Also add:** `onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();goPage('sell',document.getElementById('nav-sell'))}"`

Do the same for the Buy choice card.

For the browse chips, they're generated in JS in `initBrowseChips()`. Add `tabindex="0" role="button"` to each chip and add a keydown handler for Enter/Space:

```javascript
function initBrowseChips(){
  document.querySelectorAll('#browse-quick-filters .browse-chip').forEach(function(c){
    c.setAttribute('tabindex', '0');
    c.setAttribute('role', 'button');
    c.onclick = function(){
      document.querySelectorAll('#browse-quick-filters .browse-chip').forEach(function(x){ x.classList.remove('active'); });
      c.classList.add('active');
      BROWSE_ACTIVE_CHIP = c.getAttribute('data-filter');
      renderBrowseMakes();
    };
    c.onkeydown = function(e){
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); c.click(); }
    };
  });
}
```

For year-action buttons generated in `selectModel()`, the `<button>` element is already natively focusable and keyboard accessible — no change needed.

For make cards generated in `renderBrowseMakes()`, they already have `tabindex="0" role="button"` — no change needed.

For row links generated in `selectMake()` and `selectModel()`, they already have `tabindex="0" role="button"` — no change needed.

#### Step 2: Add `aria-hidden="true"` to all decorative SVG icons

Search for every `<svg` tag in the HTML section. For icons that are purely decorative (sidebar nav icons, header notification bell, search icon, card icons), add `aria-hidden="true"`.

List of SVGs to update:
- Sidebar nav icons (5 SVGs) — all decorative
- Header notification bell SVG — decorative
- Search icon SVG in browse toolbar — decorative
- Choice card SVGs (2 SVGs) — decorative
- Result action button SVGs (3 SVGs) — decorative
- Market export button SVGs (2 SVGs) — decorative

For each, add `aria-hidden="true"` to the `<svg>` opening tag.

#### Step 3: Add `aria-label` to KPI values and data elements

In `loadHomeKPIs()`, add `aria-label` attributes to KPI value elements after setting their text content:

```javascript
// After setting home-kpi-listings
el = document.getElementById('home-kpi-listings');
if (el) { el.textContent = active > 0 ? active.toLocaleString() : '--'; el.setAttribute('aria-label', active > 0 ? active.toLocaleString() + ' active listings' : 'Data unavailable'); }
```

In `renderMarketKPIs()`, add `aria-label` to each KPI card's value element. Modify the KPI card template to include an aria-label on the value div:

```javascript
'<div class="market-kpi-value" aria-label="' + esc(k.label) + ': ' + esc(String(k.value)) + '">' + esc(String(k.value)) + '</div>'
```

In `showResults()`, add `aria-label` to the valuation hero amount:

```javascript
h += '<div class="result-amount" aria-label="Estimated value: ' + d.estimate.toLocaleString() + ' AED">AED ' + d.estimate.toLocaleString() + '</div>';
```

Add `aria-label` to the confidence ring SVG with a human-readable description.

#### Step 4: Fix `html[lang]` on language toggle

In `toggleLang()`, add a line to update the `lang` attribute:

```javascript
function toggleLang(){
  var isRtl = document.body.dir === 'rtl';
  document.body.dir = isRtl ? 'ltr' : 'rtl';
  document.documentElement.lang = isRtl ? 'en' : 'ar';
}
```

#### Step 5: Fix confidence ring SVG stroke-dasharray

The circle has `r="28"`, so circumference = `2 * π * 28 ≈ 175.93`. The current dasharray values of 92, 68, 35 are arbitrary. Fix them to represent actual percentages of the circumference.

In `showResults()`, find the line that generates the confidence ring SVG. Replace the dasharray calculation:

```javascript
var confPct = d.confidence === 'high' ? 75 : (d.confidence === 'medium' ? 50 : 25);
// ...
'<circle cx="32" cy="32" r="28" fill="none" stroke="' + confColor + '" stroke-width="4" stroke-dasharray="' + Math.round(confPct / 100 * 175.93) + ' 175.93" stroke-dashoffset="0" stroke-linecap="round" transform="rotate(-90 32 32)" style="transition:stroke-dasharray 1s ease"/>'
```

#### Step 6: Commit

```bash
git add ui/index.html
git commit -m "fix: accessibility quick wins — ARIA roles, aria-hidden, aria-label, html[lang], confidence ring SVG

- Add role=button + tabindex=0 to choice cards (+ keyboard handler)
- Add role=button + tabindex=0 to browse filter chips (+ keyboard handler)
- Add aria-hidden=true to all 13 decorative SVG icons
- Add aria-label to KPI values, market cards, valuation hero
- Update html[lang] attribute on language toggle (en ↔ ar)
- Fix confidence ring stroke-dasharray to use actual circumference (175.93)"
```

---

### Task 2: Home Page Skeleton Loading

**Files:**
- Modify: `ui/index.html` (CSS: new skeleton classes, HTML: skeleton structure, JS: `loadHomeKPIs`)

**Interfaces:**
- Consumes: `#page-home` structure, `loadHomeKPIs()` function
- Produces: Skeleton loader visible during initial data fetch, replaced by real data on load

#### Step 1: Add home skeleton CSS

Add these classes in the CSS section, after the existing `.skeleton` styles (around line 1995):

```css
/* ── Home Page Skeleton ── */
.home-skeleton-badge {
  width: 180px; height: 28px;
  border-radius: var(--radius-full);
  margin: 0 auto var(--space-4);
}
.home-skeleton-hero {
  width: 420px; height: 56px;
  margin: 0 auto var(--space-3);
  border-radius: var(--radius-sm);
}
.home-skeleton-sub {
  width: 480px; height: 20px;
  margin: 0 auto var(--space-4);
  border-radius: var(--radius-sm);
}
.home-skeleton-kpi {
  height: 100px;
  border-radius: var(--radius-xl);
}
```

#### Step 2: Add skeleton HTML

Replace the KPI strip and CTA section with a skeleton wrapper that gets hidden when data loads. Wrap the existing KPI strip in a `<div id="home-data-content">` and add a `<div id="home-skeleton-content">` before it:

In the home page HTML section, before the KPI strip, add:

```html
<div id="home-skeleton-content">
  <div class="home-hero" style="padding-bottom:var(--space-4)">
    <div class="skeleton home-skeleton-badge"></div>
    <div class="skeleton home-skeleton-hero"></div>
    <div class="skeleton home-skeleton-sub"></div>
  </div>
  <div class="home-kpi-strip">
    <div class="skeleton home-skeleton-kpi"></div>
    <div class="skeleton home-skeleton-kpi"></div>
    <div class="skeleton home-skeleton-kpi"></div>
    <div class="skeleton home-skeleton-kpi"></div>
  </div>
</div>
```

Wrap the existing hero, KPI strip, CTA section, and trust strip in:

```html
<div id="home-data-content" class="hidden">
  <!-- existing hero, KPI, CTA, trust strip -->
</div>
```

#### Step 3: Update `loadHomeKPIs()` to toggle skeleton/data visibility

At the start of `loadHomeKPIs()`, keep the skeleton visible. In the `.then()` callback, after populating all KPI values, hide the skeleton and show the data:

```javascript
function loadHomeKPIs(){
  fetch(API+'/admin/stats').then(function(r){return r.json()}).then(function(d){
    // ... existing KPI population code ...

    // Hide skeleton, show real data
    var skel = document.getElementById('home-skeleton-content');
    var data = document.getElementById('home-data-content');
    if (skel) skel.classList.add('hidden');
    if (data) data.classList.remove('hidden');
  }).catch(function(){
    // On error, still show data section (with -- values) and hide skeleton
    var skel = document.getElementById('home-skeleton-content');
    var data = document.getElementById('home-data-content');
    if (skel) skel.classList.add('hidden');
    if (data) data.classList.remove('hidden');
  });
}
```

On `goPage('home', ...)`, reset the skeleton state so navigating back to home shows skeletons again:

```javascript
if (p === 'home') {
  var skel = document.getElementById('home-skeleton-content');
  var data = document.getElementById('home-data-content');
  if (skel) skel.classList.remove('hidden');
  if (data) data.classList.add('hidden');
  loadHomeKPIs();
}
```

#### Step 4: Commit

```bash
git add ui/index.html
git commit -m "feat: add skeleton loading to Home page hero and KPI ribbon"
```

---

### Task 3: Inline Form Validation — Replace Toast Warnings with Field-Level Errors

**Files:**
- Modify: `ui/index.html` (CSS: error state styles, JS: `doValuation` and `readForm`)

**Interfaces:**
- Consumes: `doValuation()`, form field DOM structure
- Produces: Red border + micro error text on invalid fields instead of toast popups

#### Step 1: Add field error CSS

Add these styles after the `.form-group` section:

```css
/* ── Field Error State ── */
.form-group.error input,
.form-group.error select {
  border-color: var(--red);
  box-shadow: 0 0 0 3px var(--red-bg);
}
.form-group.error .field-error {
  display: block;
}
.field-error {
  display: none;
  font-size: 0.68rem;
  color: var(--red);
  font-weight: 500;
  margin-top: 2px;
}
```

#### Step 2: Add error message elements to form fields

In `buildForm()`, add a `<span class="field-error"></span>` after each required input field. The `.fm-make`, `.fm-model`, `.fm-year` fields each need one. In the Buy form, `.fm-asking` also needs one.

For the Make input, change:
```javascript
'<div class="form-group"><label>Make</label><div class="autocomplete-wrap"><input type="text" class="fm-make" ...><div class="autocomplete-suggestions"></div></div></div>'
```
To:
```javascript
'<div class="form-group"><label>Make</label><div class="autocomplete-wrap"><input type="text" class="fm-make" ...><div class="autocomplete-suggestions"></div></div><span class="field-error" data-field="make">Please select a make</span></div>'
```

Do the same for Model ("Please select a model"), Year ("Please enter a valid year"), and the Asking Price field in buy mode ("Please enter the asking price").

#### Step 3: Replace toast validation with inline errors

In `doValuation()`, replace the toast-based validation with inline field errors. Before the existing validation block, add a field-clearing function and then set errors:

```javascript
async function doValuation(mode){
  // Clear all previous field errors
  var el = document.getElementById(mode + '-form');
  el.querySelectorAll('.form-group').forEach(function(g){ g.classList.remove('error'); });
  el.querySelectorAll('.field-error').forEach(function(e){ e.style.display = 'none'; });

  var body = readForm(el);
  var errors = [];

  if (!body.make) {
    errors.push({field: 'make', msg: 'Please select a make'});
    var mkGroup = el.querySelector('.fm-make').closest('.form-group');
    if (mkGroup) mkGroup.classList.add('error');
    var mkErr = mkGroup ? mkGroup.querySelector('.field-error') : null;
    if (mkErr) mkErr.style.display = 'block';
  }
  if (!body.model) {
    errors.push({field: 'model', msg: 'Please select a model'});
    var mdGroup = el.querySelector('.fm-model').closest('.form-group');
    if (mdGroup) mdGroup.classList.add('error');
    var mdErr = mdGroup ? mdGroup.querySelector('.field-error') : null;
    if (mdErr) mdErr.style.display = 'block';
  }
  if (!body.year || isNaN(body.year) || body.year < 1990 || body.year > 2027) {
    errors.push({field: 'year', msg: 'Please enter a valid year (1990-2027)'});
    var yrGroup = el.querySelector('.fm-year').closest('.form-group');
    if (yrGroup) yrGroup.classList.add('error');
    var yrErr = yrGroup ? yrGroup.querySelector('.field-error') : null;
    if (yrErr) { yrErr.textContent = 'Please enter a valid year (1990-2027)'; yrErr.style.display = 'block'; }
  }

  if (mode === 'buy' && !body.asking_price) {
    errors.push({field: 'asking', msg: 'Please enter the asking price'});
    var apGroup = el.querySelector('.fm-asking');
    if (apGroup) {
      var apFormGroup = apGroup.closest('.form-group');
      if (!apFormGroup) { apFormGroup = apGroup.parentElement; }
      if (apFormGroup) apFormGroup.classList.add('error');
    }
  }

  if (errors.length > 0) return; // Stop — inline errors are shown

  // ... rest of existing doValuation logic (loading spinner, fetch, etc.) ...
}
```

#### Step 4: Clear errors on field input

Add an input handler that clears the error state when the user starts typing in a field that had an error:

In `buildForm()`, after constructing the form, add event listeners:

```javascript
el.querySelectorAll('input').forEach(function(input){
  input.addEventListener('input', function(){
    var group = this.closest('.form-group');
    if (group) group.classList.remove('error');
    var err = group ? group.querySelector('.field-error') : null;
    if (err) err.style.display = 'none';
  });
});
```

#### Step 5: Commit

```bash
git add ui/index.html
git commit -m "feat: replace toast validation with inline field-level errors

- Add .field-error CSS (red text, hidden by default, shown on .form-group.error)
- Add error <span> elements after make, model, year, asking-price fields
- Replace showWarning() toasts with inline error display in doValuation()
- Clear field errors on input (user types → error disappears)"
```

---

### Task 4: Visual Polish — Count-up animation, empty states, broken things

**Files:**
- Modify: `ui/index.html` (CSS: animation, JS: `showResults`, `renderMarketKPIs`, `showResults` empty states)

**Interfaces:**
- Consumes: `showResults()`, `renderMarketInsights()`
- Produces: Count-up price animation on valuation results, empty state for 0 comps, empty state for 0 adjustments

#### Step 1: Add count-up animation to valuation hero

In `showResults()`, find the line that writes the result amount. Instead of writing the static value, set a `data-target` attribute and use `requestAnimationFrame` to count up:

Replace:
```javascript
h += '<div class="result-amount" aria-label="...">AED ' + d.estimate.toLocaleString() + '</div>';
```

With a span that gets animated by JS after the HTML is inserted:

```javascript
h += '<div class="result-amount" aria-label="Estimated value: ' + d.estimate.toLocaleString() + ' AED"><span id="result-amount-value">AED 0</span></div>';
```

After `c.innerHTML = h;`, add the count-up animation:

```javascript
c.innerHTML = h;

// Count-up animation for result amount
var amountEl = document.getElementById('result-amount-value');
if (amountEl) {
  var target = d.estimate;
  var duration = 600;
  var start = performance.now();
  function animate(now) {
    var elapsed = now - start;
    var progress = Math.min(elapsed / duration, 1);
    // Ease-out: 1 - (1-t)^3
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(eased * target);
    amountEl.textContent = 'AED ' + current.toLocaleString();
    if (progress < 1) {
      requestAnimationFrame(animate);
    }
  }
  requestAnimationFrame(animate);
}
```

#### Step 2: Add empty state for 0 comparable listings

In `showResults()`, if `d.comps` is empty or missing, show an empty state instead of an empty card:

```javascript
/* ═══ COMPARABLE LISTINGS ═══ */
if (d.comps && d.comps.length) {
  h += '<div class="card"><h3>Comparable Listings</h3>' + (d.comps || []).slice(0, 8).map(function(x){ ... }).join('') + '</div>';
} else {
  h += '<div class="card"><h3>Comparable Listings</h3><div class="empty-state"><div class="empty-state-icon">📋</div><h3>No comparable listings found</h3><p>Try broadening your search criteria or checking a more common make/model combination.</p></div></div>';
}
```

Note: The API currently returns 422 for insufficient comps. This empty state handles the case where comps exist but are empty (future-proofing). The 422 case is already handled by the catch block.

#### Step 3: Add empty state for 0 adjustments

In `showResults()`, if `d.adjustments` is empty, show a message instead of hiding the section:

```javascript
/* ═══ AI EXPLANATION ═══ */
if (d.adjustments && d.adjustments.length) {
  h += '<div class="card"><h3>How We Calculated This</h3>...';
} else {
  h += '<div class="card"><h3>How We Calculated This</h3><p style="font-size:var(--text-caption);color:var(--text-muted);text-align:center;padding:var(--space-3) 0">This valuation is based directly on comparable listings with no adjustments needed.</p></div>';
}
```

#### Step 4: Commit

```bash
git add ui/index.html
git commit -m "feat: add count-up animation, empty states for comps and adjustments

- Count-up animation on valuation hero (600ms ease-out cubic)
- Empty state card for 0 comparable listings
- Empty state message for 0 adjustments (no adjustments needed)"
```

---

### Task 5: Reduce Inline Style Debt in `showResults()` — Extract Key Classes

**Files:**
- Modify: `ui/index.html` (CSS: 4 new utility classes, JS: `showResults()`)

**Interfaces:**
- Consumes: `showResults()` function
- Produces: 4 new CSS classes replacing the worst inline style blocks

#### Step 1: Add CSS classes for result card content

These classes replace the largest inline style blocks in `showResults()`. Add them after the existing Results section:

```css
/* ── Results: Better Deals ── */
.result-alt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.result-alt-price {
  font-size: 1.1rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}
.result-alt-meta {
  font-size: 0.76rem;
  color: var(--text-muted);
  margin-top: 2px;
}
.result-alt-save {
  background: var(--green-bg);
  color: var(--green);
  padding: 5px 12px;
  border-radius: var(--radius-md);
  font-size: 0.68rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}
.result-alt-source {
  font-size: 0.7rem;
  color: var(--text-accent);
  margin-top: 4px;
}

/* ── Results: Adjustment Row ── */
.result-adj-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-subtle);
}
.result-adj-reason {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-primary);
}
.result-adj-detail {
  font-size: 0.75rem;
  color: var(--text-muted);
}
.result-adj-amount {
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  flex-shrink: 0;
  margin-left: var(--space-2);
}

/* ── Results: Better Deals Card ── */
.result-better-deals {
  border-left: 3px solid var(--green);
}

/* ── Results: Verdict Detail ── */
.result-verdict-detail {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 4px;
}
```

#### Step 2: Refactor alt-card rendering in `showResults()`

Replace the inline-styled alt-card block (the "Better Deals Available" section) to use the new CSS classes. Find the `alts.map(...)` section and replace it with:

```javascript
if (alts.length) {
  h += '<div class="card result-better-deals"><h3>Better Deals Available</h3>' + alts.map(function(x){
    var save = ap - x.price_aed;
    return '<div class="alt-card">' +
      '<div class="result-alt-header">' +
        '<div>' +
          '<div class="result-alt-price">AED ' + x.price_aed.toLocaleString() + '</div>' +
          '<div class="result-alt-meta">' + x.year + ' · ' + x.mileage_km + ' km · ' + x.spec + ' · ' + x.city + '</div>' +
        '</div>' +
        '<div class="result-alt-save">SAVE AED ' + save.toLocaleString() + '</div>' +
      '</div>' +
      '<div class="result-alt-source">' + esc(x.found_on) + '</div>' +
    '</div>';
  }).join('') + '</div>';
}
```

#### Step 3: Refactor adjustment row rendering

Replace the inline-styled adjustment rows:

```javascript
h += '<div class="card"><h3>How We Calculated This</h3><div style="display:flex;flex-direction:column;gap:10px">';
d.adjustments.forEach(function(a){
  h += '<div class="result-adj-row">' +
    '<div>' +
      '<div class="result-adj-reason">' + esc(a.reason) + '</div>' +
      '<div class="result-adj-detail">' + esc(a.detail) + '</div>' +
    '</div>' +
    '<div class="result-adj-amount" style="color:' + (a.amount >= 0 ? 'var(--green)' : 'var(--red)') + '">' + (a.amount >= 0 ? '+' : '') + 'AED ' + Math.abs(a.amount).toLocaleString() + '</div>' +
  '</div>';
});
h += '</div></div>';
```

#### Step 4: Refactor verdict detail

Replace the inline-styled verdict detail line:

```javascript
h += '<div class="result-verdict-detail">Asking: AED ' + ap.toLocaleString() + ' vs Market: AED ' + d.estimate.toLocaleString() + '</div>';
```

#### Step 5: Commit

```bash
git add ui/index.html
git commit -m "refactor: extract inline styles from showResults() into CSS classes

- Add 8 new CSS classes for result components (alt-header, alt-price, alt-meta,
  alt-save, alt-source, adj-row, adj-reason, adj-detail, adj-amount)
- Replace inline styles in Better Deals section
- Replace inline styles in AI Explanation adjustments section
- Replace inline styles in Deal Verdict detail
- Reduces inline style blocks from 12+ to 1 (the dynamic color on adj-amount)"
```

---

### Verification Plan

After all 5 tasks, verify in browser at `http://localhost:8000`:

- [ ] **Home page:** Skelton loader appears on load, replaced by KPIs. Tab through choice cards — they focus and activate with Enter/Space.
- [ ] **Sell form:** Submit empty form → red borders + error text on make/model/year. Start typing → errors clear.
- [ ] **Buy form:** Same as Sell. Asking price required validation works. URL import still works.
- [ ] **Results:** Price counts up from 0. Confidence ring arc is proportional. Tab through action buttons.
- [ ] **Browse:** Filter chips are Tab-accessible, activate with Enter/Space. Search works. "Value This" works.
- [ ] **Market:** KPI cards have aria-labels. All sections populate.
- [ ] **Language toggle:** `html[lang]` changes between "en" and "ar". Body dir toggles.
- [ ] **Screen reader:** Run through with NVDA/VoiceOver. Sidebar nav announced. KPI values read. SVG icons silent.
- [ ] **Reduced motion:** Enable in OS settings. Animations stop. Shimmer freezes.
- [ ] **No regressions:** All 5 pages load. All existing API calls succeed. No console errors.

---

*Plan complete 2026-07-12. 5 tasks, ~2 hours total estimated effort.*
