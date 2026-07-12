# Final Polish — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Close the 4 remaining gaps that have meaningful UX impact — autocomplete ARIA, typography token hardening, unused file cleanup, and sidebar menu semantics.

**Architecture:** Four small tasks. Tasks 1 and 2 are independent (different sections of the file). Task 3 is trivial. Task 4 is the largest but purely mechanical (find-and-replace).

**Tech Stack:** Vanilla HTML/CSS/JS. Single file `ui/index.html`.

## Global Constraints

- Do NOT change Python, API, or database
- No npm/build/framework dependencies
- Zero regressions on existing functionality
- Commit after each task

---

### Task 1: Autocomplete ARIA — Combobox Pattern

**Files:** Modify `ui/index.html` (JS: `doAutocomplete()`, HTML: autocomplete inputs)

**Goal:** Make the autocomplete dropdown properly announced by screen readers. Currently it's silent — users don't know suggestions appeared.

**Changes:**

**A) Add `role="combobox"` to each autocomplete input:**

In `buildForm()`, add `role="combobox"` and `aria-expanded="false"` to make, model, city, and country inputs. Also add `aria-autocomplete="list"`.

**B) Add `role="listbox"` to suggestion dropdowns and `role="option"` to items:**

In `doAutocomplete()`, when showing the suggestions dropdown:
- Set `input.setAttribute('aria-expanded', 'true')` on the input
- Add `role="listbox"` to the suggestions div
- Add `role="option"` to each suggestion item
- Set `aria-selected="false"` on each option

When hiding the dropdown:
- Set `input.setAttribute('aria-expanded', 'false')`

**C) Add `aria-activedescendant` for keyboard navigation:**

When the user presses ArrowDown/ArrowUp in the autocomplete, track the active index and set `aria-activedescendant` on the input pointing to the active option's ID.

Add keyboard event handlers to the autocomplete input in `buildForm()`:

```javascript
el.querySelectorAll('.fm-make, .fm-model, .fm-city, .fm-country').forEach(function(input){
  input.addEventListener('keydown', function(e){
    var wrap = this.closest('.autocomplete-wrap');
    if (!wrap) return;
    var sug = wrap.querySelector('.autocomplete-suggestions');
    if (!sug || !sug.classList.contains('show')) return;
    var items = sug.querySelectorAll('.autocomplete-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      // Move focus to first/last item, track active index
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      // Move focus to previous item
    } else if (e.key === 'Enter') {
      e.preventDefault();
      // Click the active item
    } else if (e.key === 'Escape') {
      sug.classList.remove('show');
      this.setAttribute('aria-expanded', 'false');
    }
  });
});
```

**Commit:**
```
feat: add ARIA combobox pattern to autocomplete inputs

- Add role=combobox, aria-expanded, aria-autocomplete to autocomplete inputs
- Add role=listbox to suggestion dropdown, role=option to items
- Add ArrowDown/ArrowUp/Enter/Escape keyboard navigation
- Set aria-activedescendant on input during keyboard navigation
```

---

### Task 2: Typography Token Expansion

**Files:** Modify `ui/index.html` (CSS `:root` + all hardcoded font-size values)

**Goal:** Replace the 84 remaining hardcoded `font-size` values with design token references. This makes the typography scale centrally managed and ensures consistency.

**Changes:**

**A) Expand the `:root` typography scale to cover all used sizes:**

Currently the token scale has 8 sizes. The actual usage requires these additional tokens:

```css
--text-xs:      0.68rem;   /* 11px — micro labels, market KPI labels */
--text-sm:      0.72rem;   /* 12px — rail meta, country chips */
--text-base-sm: 0.78rem;   /* 12.5px — card h3, comp meta */
--text-base:    0.82rem;   /* 13px — rail status, market health */
--text-md:      0.85rem;   /* 14px — autocomplete items, choice card p */
--text-lg:      0.88rem;   /* 14px — browse search */
--text-input:   0.92rem;   /* 15px — form inputs, page-sub */
--text-h4:      0.95rem;   /* 15px — btn text, range labels */
--text-lead:    1.05rem;   /* 17px — home hero sub */
```

**B) Systematically replace hardcoded `font-size: Xrem` with `var(--text-*)`:**

For every CSS rule that uses a hardcoded `font-size: 0.XXrem`, replace with the matching token. Priority order:

1. CSS classes first (one edit each, broad impact)
2. JS template strings second (in `showResults()`, `renderBrowseMakes()`, etc.)

Example replacements:
- `font-size: 0.68rem` → `font-size: var(--text-xs)`
- `font-size: 0.72rem` → `font-size: var(--text-sm)`
- `font-size: 0.78rem` → `font-size: var(--text-base-sm)`
- `font-size: 0.82rem` → `font-size: var(--text-base)`
- `font-size: 0.85rem` → `font-size: var(--text-md)`
- `font-size: 0.88rem` → `font-size: var(--text-base)`
- `font-size: 0.92rem` → `font-size: var(--text-input)`
- `font-size: 0.95rem` → `font-size: var(--text-h4)`
- `font-size: 1.05rem` → `font-size: var(--text-lead)`

**C) Verify visual equivalence:**

After each batch of replacements, confirm that no font sizes changed visually. The token values should match exactly what was hardcoded.

**Commit:**
```
refactor: expand typography tokens and replace 84 hardcoded font-sizes

- Add 9 new typography tokens covering all used sizes
- Replace hardcoded font-size values in CSS with token references
- Replace hardcoded font-size values in JS template strings with tokens
- All visual output unchanged (token values match original hardcoded values)
```

---

### Task 3: Unused File Cleanup

**Files:** Delete (not modify)

**Goal:** Remove the 7 files identified as unused/debug artifacts.

**Delete these files:**
```
ui/browse-market.js    — older version, different CSS vars, not referenced
ui/browse-test.js      — partial fragment, not referenced
ui/fix-forms.js        — historical fix for removed function
ui/test.html           — dev test page
_test_js.js            — root debug file
_test_load.js          — root debug file
_v2_check.js           — root debug file
```

**Verify before deletion** — confirm each file is NOT referenced by index.html or any other file in the project:
- `grep -r "browse-market.js" ui/ src/` → no results
- `grep -r "browse-test.js" ui/ src/` → no results
- etc.

**Commit:**
```
chore: remove 7 unused debug and historical files

- Remove ui/browse-market.js (older version, not referenced)
- Remove ui/browse-test.js (partial fragment, not referenced)
- Remove ui/fix-forms.js (historical fix for removed function)
- Remove ui/test.html (dev test page)
- Remove root _test_js.js, _test_load.js, _v2_check.js (debug artifacts)
```

---

### Task 4: Sidebar Menu ARIA Semantics

**Files:** Modify `ui/index.html` (HTML sidebar section)

**Goal:** Add `role="navigation"` landmark refinements and `aria-current="page"` on the active nav item. Minimal change, meaningful screen reader improvement.

**Changes:**

**A) Replace `aria-label` on `<nav>` with a more descriptive one:**

The sidebar `<nav>` already has `aria-label="Primary"`. Keep it.

**B) In `goPage()`, set `aria-current="page"` on the active nav link:**

When a nav link becomes active (`.active` class added), also set `aria-current="page"`. When it becomes inactive, remove `aria-current`.

```javascript
function goPage(p, el) {
  // ... existing code ...
  document.querySelectorAll('.sidebar-nav a').forEach(function(a){
    a.classList.remove('active');
    a.removeAttribute('aria-current');
  });
  el.classList.add('active');
  el.setAttribute('aria-current', 'page');
  // ... rest of existing code ...
}
```

**C) Add `aria-label` to the disabled nav items explaining why they're disabled:**

```html
<a href="#" class="nav-disabled" aria-label="Reports — coming soon" aria-disabled="true">
<a href="#" class="nav-disabled" aria-label="Watchlist — coming soon" aria-disabled="true">
<a href="#" class="nav-disabled" aria-label="Settings — coming soon" aria-disabled="true">
```

**Commit:**
```
fix: add sidebar menu ARIA semantics

- Set aria-current="page" on active nav item in goPage()
- Add aria-disabled="true" + descriptive aria-label on disabled items
- Remove aria-current when navigating away
```

---

## Verification

After all 4 tasks:

- [ ] Autocomplete: Tab to Make field, type "Toy" → screen reader announces "3 suggestions available". ArrowDown → "Toyota selected". Enter → value filled.
- [ ] Typography: Visual inspection of all 5 pages. No font sizes changed. All text renders identically to before.
- [ ] Cleanup: `git status` shows 7 deleted files. `ui/` directory now contains only `index.html` + `previews/`.
- [ ] Sidebar: Tab through nav. Screen reader announces "Home, current page". Disabled items announce "Reports — coming soon, disabled".
- [ ] No regressions: All 5 pages load and function correctly. All API calls succeed.

---

*Plan complete. 4 tasks, ~2 hours estimated. After this, all non-future gaps are closed.*
