# Remaining Gaps — Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Close the 10 remaining MEDIUM/LOW gaps — inline style extraction in `buildForm()`, form label associations, dead CSS cleanup, and RTL foundation.

**Architecture:** Three small tasks. Task 1 extracts the last large inline-style blocks. Task 2 fixes structural a11y gaps (labels, skip link, ARIA regions). Task 3 removes dead code and adds RTL hooks. All in `ui/index.html`.

**Tech Stack:** Vanilla HTML/CSS/JS. Single file.

## Global Constraints

- Do NOT change Python, API, or database
- No npm/build/framework dependencies
- Zero regressions on existing functionality
- Commit after each task

---

### Task 1: Extract Inline Styles from `buildForm()` + URL Import

**Files:** Modify `ui/index.html`

**Goal:** Apply the same pattern as Task 5 (which cleaned `showResults()`) to the two remaining areas with large inline style blocks.

**Changes:**

**A) Add CSS classes for the asking price section:**

```css
/* ── Buy Form: Asking Price Hero ── */
.buy-asking-section {
  background: linear-gradient(135deg, var(--gold-glow), rgba(200,169,81,0.03));
  border-radius: 14px;
  padding: var(--space-4);
  margin-bottom: 0;
  border: 1px solid var(--gold-glow);
}
.buy-asking-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.buy-asking-input {
  flex: 1;
  height: 56px;
  padding: 0 18px;
  border: 1.5px solid rgba(255,255,255,0.06);
  border-radius: var(--radius-lg);
  font-size: 1.2rem;
  font-weight: 700;
  background: rgba(0,0,0,0.25);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  transition: border-color var(--duration-base), box-shadow var(--duration-base);
}
.buy-asking-input:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px var(--gold-glow);
}
.buy-asking-currency {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-accent);
}

/* ── Buy Form: URL Import ── */
.url-import-card {
  background: linear-gradient(135deg, var(--gold-glow), rgba(200,169,81,0.03));
  border-radius: 14px;
  padding: var(--space-5) var(--space-6);
  border: 1px dashed var(--border-hover);
  text-align: center;
}
.url-import-icon {
  font-size: 1.4rem;
  margin-bottom: var(--space-1);
}
.url-import-title {
  font-weight: 700;
  margin-bottom: 4px;
  font-size: 0.95rem;
  color: var(--text-primary);
}
.url-import-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-bottom: var(--space-4);
}
.url-import-input {
  width: 100%;
  max-width: 560px;
  height: 54px;
  padding: 0 18px;
  border: 1.5px solid var(--border-hover);
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  font-family: 'Inter', sans-serif;
  text-align: center;
  margin-bottom: var(--space-3);
  background: var(--bg-input);
  color: var(--text-primary);
  transition: border-color var(--duration-base);
}
.url-import-input:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 3px var(--gold-glow);
  outline: none;
}
```

**B) In `buildForm()`, replace the inline-styled asking price section with these classes.**

**C) In the Buy page HTML, replace the inline-styled URL import section with these classes.**

**D) Remove inline `onfocus`/`onblur` handlers from the asking price input and URL input — the CSS `:focus` selectors above handle this now.**

**Commit:**
```
refactor: extract inline styles from buildForm() and URL import into CSS

- Add 12 CSS classes for asking price section and URL import card
- Replace inline styles in buy form section A with CSS classes
- Replace inline styles in URL import section with CSS classes
- Remove JS onfocus/onblur handlers (CSS :focus now handles this)
```

---

### Task 2: Structural Accessibility — Labels, Skip Link, ARIA Regions

**Files:** Modify `ui/index.html`

**Goal:** Close the remaining a11y gaps: properly associated form labels, a skip-to-content link, and `aria-live` regions for dynamic content.

**Changes:**

**A) Add explicit `<label for="">` associations:**

In `buildForm()`, each input currently has `<label>Make</label>` wrapping but no `for`/`id` association. Add unique IDs to each input and `for` attributes to each label:

```javascript
// Make field:
'<div class="form-group"><label for="' + id + '-make">Make</label>...<input id="' + id + '-make" class="fm-make" ...>'

// Model field:
'<div class="form-group"><label for="' + id + '-model">Model</label>...<input id="' + id + '-model" class="fm-model" ...>'

// etc.
```

Where `id` is either `'sell'` or `'buy'` — use the parameter passed to `buildForm()`.

**B) Add skip-to-content link:**

Add as the first child of `<body>`:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

With CSS:
```css
.skip-link {
  position: absolute;
  top: -100px;
  left: var(--space-2);
  background: var(--gold);
  color: var(--text-inverse);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.85rem;
  z-index: var(--z-toast);
  transition: top var(--duration-fast);
}
.skip-link:focus {
  top: var(--space-2);
}
```

**C) Add `aria-live` regions for dynamic content:**

- Add `aria-live="polite"` to `#sell-results` and `#buy-results` containers
- Add `aria-live="polite"` to `#market-kpi-grid`
- Add `aria-live="polite"` to `#browse-makes-grid`

**Commit:**
```
fix: structural accessibility — labels, skip link, aria-live regions

- Add for/id associations on all form labels in buildForm()
- Add skip-to-content link as first body child
- Add aria-live="polite" to results, market KPI, and browse grid containers
```

---

### Task 3: Dead Code Removal + RTL Foundation

**Files:** Modify `ui/index.html`

**Goal:** Remove unused CSS classes, add RTL CSS hooks so the language toggle actually works visually.

**Changes:**

**A) Remove dead CSS:**

- Delete `.table-enterprise` block (never used in HTML)
- Delete `.btn-icon` block (never used in HTML)
- Delete the `--duration-instant` token if never referenced (check first)

**B) Add RTL CSS foundation:**

Add `[dir="rtl"]` selectors for the key layout elements that need mirroring:

```css
/* ── RTL Support ── */
[dir="rtl"] .sidebar { border-right: none; border-left: 1px solid var(--border-subtle); }
[dir="rtl"] .sidebar-nav a::before { left: auto; right: -8px; border-radius: 3px 0 0 3px; }
[dir="rtl"] .sidebar-nav a { text-align: right; }
[dir="rtl"] .header { direction: rtl; }
[dir="rtl"] .buy-layout { direction: rtl; }
[dir="rtl"] .buy-rail { direction: ltr; } /* Numbers stay LTR */
[dir="rtl"] .page-header { direction: rtl; }
[dir="rtl"] .browse-toolbar { direction: rtl; }
[dir="rtl"] .toast-container { right: auto; left: 20px; }
[dir="rtl"] @keyframes slideIn { from { transform: translateX(-400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
[dir="rtl"] @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(-400px); opacity: 0; } }
```

**Commit:**
```
chore: remove dead CSS, add RTL foundation

- Remove .table-enterprise and .btn-icon (never used)
- Add [dir="rtl"] selectors for sidebar, header, layout, toasts
- RTL mirror slide animations for toast notifications
```

---

## Verification

After all 3 tasks:

- [ ] Buy form asking price section renders without inline styles
- [ ] URL import card renders without inline styles
- [ ] Form labels are clickable (click "Make" → input focuses)
- [ ] Tab from address bar → skip link appears → Enter → jumps to main content
- [ ] Screen reader announces "12 results loaded" when valuation completes
- [ ] Language toggle → page mirrors to RTL (sidebar on right, text aligned right)
- [ ] No console errors from removed CSS classes
- [ ] All 5 pages still load and function correctly

---

*Plan complete. 3 tasks, ~1.5 hours estimated.*
