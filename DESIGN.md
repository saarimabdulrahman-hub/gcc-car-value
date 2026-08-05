---
name: GCC Car Valuator
description: Premium car valuation platform for the Gulf market — dark graphite surfaces, gold accent, bilingual
colors:
  canvas: "#050a0f"
  sidebar: "#091017"
  surface: "#0b131c"
  surface-raised: "#0e1721"
  surface-hover: "#14232f"
  accent: "#e9a50a"
  accent-light: "#f2b52a"
  accent-dark: "#bf7707"
  accent-soft: "rgba(233, 165, 10, 0.12)"
  accent-glow: "rgba(233, 165, 10, 0.28)"
  text-primary: "#f7f8fa"
  text-secondary: "#929cab"
  text-muted: "#657180"
  text-inverse: "#050a0f"
  success: "#14df75"
  success-soft: "rgba(20, 223, 117, 0.10)"
  danger: "#f04444"
  danger-soft: "rgba(240, 68, 68, 0.10)"
  warning: "#f59e0b"
  warning-soft: "rgba(245, 158, 11, 0.10)"
  info: "#3b82f6"
  info-soft: "rgba(59, 130, 246, 0.10)"
  line: "#1c2732"
  line-hover: "#35424f"
  line-soft: "rgba(148, 163, 184, 0.11)"
  line-active: "rgba(230, 158, 15, 0.32)"
typography:
  display:
    fontFamily: "Archivo, Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontWeight: 600
  body:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  mono:
    fontFamily: "JetBrains Mono, monospace"
    fontWeight: 500
  label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    letterSpacing: "0.06em"
    textTransform: "uppercase"
rounded:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "12px"
  xl: "16px"
  2xl: "20px"
  full: "9999px"
spacing:
  1: "8px"
  2: "16px"
  3: "24px"
  4: "32px"
  5: "40px"
  6: "48px"
  8: "64px"
components:
  button-primary:
    backgroundColor: "linear-gradient(90deg, #8B6914 0%, #5C4410 55%, #332008 100%)"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "12px 24px"
  button-primary-hover:
    backgroundColor: "linear-gradient(90deg, #8B6914 0%, #5C4410 55%, #332008 100%)"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
  card:
    backgroundColor: "linear-gradient(180deg, rgba(255,255,255,0.015) 0%, transparent 30%), {colors.surface-raised}"
    rounded: "14px"
    padding: "{spacing.3}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
  chip:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.full}"
  chip-active:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-light}"
    rounded: "{rounded.full}"
---

# Design System: GCC Car Valuator

## Overview

**Creative North Star: "The Gulf Archive"**

The aesthetic of a high-end Gulf hotel lobby at dusk — dark marble, gold fixtures, curated lighting, bilingual signage. Premium but welcoming, local but worldly. The interface treats data the way an archive treats documents: organized, searchable, serious, but never cold. Every surface is graphite; every accent is gold. Green means go. Red means stop. There is no purple.

The system is dark-by-design with no light mode. Depth is conveyed through layered surfaces (canvas → sidebar → card → elevated) and subtle gradient overlays rather than heavy drop shadows. Cards use a glass-morphism effect with pseudo-element gradient borders that catch light at the top edge. The gold accent appears sparingly — on primary CTAs, active states, brand marks, and data highlights — and its rarity is the point.

Typography pairs Archivo's distinctive geometric display voice with Inter's neutral workhorse body. JetBrains Mono handles numbers and data. Arabic is a first-class citizen with RTL layout support, translated chrome, and persisted language preference — not a translated afterthought.

**Key Characteristics:**
- Dark graphite surfaces with gold accent (no light mode)
- Glass-morphism cards with pseudo-element gradient borders
- Layered depth through surface tones, not heavy shadows
- Bilingual: English primary, Arabic with full RTL support
- 8px spatial grid, 4-level radius scale, 5-level elevation
- Inter body, Archivo display, JetBrains Mono for data
- Purposeful gold: accent appears on ≤10% of any screen

## Colors

The palette is a dark graphite monolith punctuated by a single gold accent and four semantic colors. Gold is the only warm color; green/red/amber/blue are strictly semantic.

### Primary
- **Gold Accent** (`#e9a50a`): Primary CTAs, active nav states, brand marks, data highlights, focus rings. Used sparingly — its impact comes from contrast against the graphite background, not from frequency.
- **Gold Light** (`#f2b52a`): Hover states, badge text, KPI accent icons. Brighter variant for interactive feedback.
- **Gold Dark** (`#bf7707`): Button gradient endpoint, pressed states. Darker variant for depth in gold elements.

### Neutral
- **Canvas** (`#050a0f`): Page background. The deepest surface. Behind everything.
- **Sidebar** (`#091017`): Navigation chrome. Slightly lighter than canvas to distinguish the persistent frame from the content area.
- **Surface** (`#0b131c`): Card backgrounds, form inputs, dropdowns. The primary content surface.
- **Surface Raised** (`#0e1721`): Card hover state, elevated panels. One step above surface.
- **Surface Hover** (`#14232f`): Interactive hover on cards and rows. The lightest neutral surface.
- **Text Primary** (`#f7f8fa`): Headlines, body text, active nav items. Near-white for readability on dark backgrounds.
- **Text Secondary** (`#929cab`): Supporting copy, metadata, helper text. Muted but legible (7.3:1 contrast ratio).
- **Text Muted** (`#657180`): Section labels, placeholder text, disabled states. Lowest contrast still meeting WCAG AA.
- **Text Inverse** (`#050a0f`): Text on gold backgrounds (badges, tooltips). Same as canvas — reads as dark on light.

### Semantic
- **Success** (`#14df75`): Positive indicators, live status dots, upward trends, healthy scrapers. Used with `success-soft` background (`rgba(20, 223, 117, 0.10)`).
- **Danger** (`#f04444`): Error states, destructive actions, downward trends, unhealthy checks. Used with `danger-soft` background.
- **Warning** (`#f59e0b`): Attention states, stale data indicators, medium confidence. Used with `warning-soft` background.
- **Info** (`#3b82f6`): Neutral indicators, information highlights. Used with `info-soft` background.

### Borders
- **Line** (`#1c2732`): Default borders, dividers, input strokes at rest.
- **Line Hover** (`#35424f`): Border on hover, active form field strokes.
- **Line Soft** (`rgba(148, 163, 184, 0.11)`): Subtle card borders, sidebar dividers.
- **Line Active** (`rgba(230, 158, 15, 0.32)`): Gold border on active chips, selected cards, focused elements.

### Named Rules
**The Gold Restraint Rule.** Gold appears on primary CTAs, active states, and brand moments only. It never appears as body text, card backgrounds, or decorative gradients on non-interactive surfaces. If gold is everywhere, gold is nowhere.

**The Semantic Triad Rule.** Green, red, and amber are used exclusively for system state communication (success/error/warning). They never appear as decorative colors, chart colors, or brand accents. Blue is reserved for informational highlights.

## Typography

**Display Font:** Archivo (with Inter, system sans-serif fallback)
**Body Font:** Inter (with system sans-serif fallback)
**Mono Font:** JetBrains Mono (with monospace fallback)

**Character:** Archivo brings a distinctive geometric voice to hero headlines and page titles — it's the brand's typographic signature. Inter handles everything else with neutral clarity. JetBrains Mono anchors numbers, stats, and data in a precision-coded aesthetic. The pairing is "one distinctive voice, one workhorse, one calculator."

### Hierarchy
- **Display** (600, 48px / `--text-display`, 0.95 line-height): Homepage hero headline only. "What would you like to do today?"
- **Page Title** (700, 34px / `--page-title`, 1.15 line-height, -0.03em tracking): Page headers. Uses gold gradient text effect (background-clip: text).
- **Section Heading** (600, 13px / `--text-caption`, uppercase, 0.06em tracking): Card headers, form section titles. Smaller than body but structurally dominant through weight + case + spacing.
- **Body** (400, 16px / `--text-body`, 1.6 line-height): Primary reading text, form labels, rail descriptions.
- **Data** (700-800, variable, JetBrains Mono, -0.02em tracking): KPI values, prices, listing counts, stats. Tabular figures via `font-feature-settings: "tnum"`.
- **Label** (600, 12px / `--text-xs`, uppercase, 0.06-0.09em tracking): Section labels, filter labels, metadata. The smallest text in the system.

### Named Rules
**The Uppercase Constraint Rule.** Uppercase is reserved for labels under 14px. Body text, headlines, and navigation items are never uppercase. The distinction between "LABEL" and "sentence" creates hierarchy without size changes.

**The Mono Rule.** Numbers in KPIs, prices, and data tables use JetBrains Mono with tabular figures. Body copy and prose never use the mono font. The typeface shift signals "this is data, not opinion."

## Layout

The spatial system uses an 8px grid with named steps from `--space-1` (8px) through `--space-12` (96px). Content lives in a centered container (max-width 1340px with sidebar, 1060px without). The sidebar is a persistent 250px column; the main content area fills the remaining space.

**Responsive behavior:** At 1100px, the Sell/Buy two-column grid collapses to single column. At 900px, the home hero switches from two-column to stacked. At 768px, the browse insight grid collapses from 3 columns to 2 to 1. At 640px, the sidebar becomes a fixed overlay triggered by a hamburger button.

**Density:** The system is medium-density. Cards have 24px internal padding. Form rows use 8px gaps. Content sections are separated by 40-48px vertical spacing. The Reports page is the densest surface and is treated as an analytics dashboard.

## Elevation & Depth

The system conveys depth through layered surface tones rather than shadows. The hierarchy: canvas (page bg) → sidebar (chrome) → surface (cards/inputs) → surface-raised (hover states) → surface-hover (active interactions). Cards at rest have a subtle `0 2px 8px rgba(0,0,0,0.25)` shadow for edge definition, not depth illusion. On hover, cards lift with `0 20px 60px rgba(0,0,0,0.45)` — the only dramatic shadow in the system.

**Glass-morphism:** Cards use a `::before` pseudo-element for a gradient border (top edge catch-light) and a `::after` pseudo-element for a gradient hairline. This creates the illusion of a glass pane without heavy blur or transparency.

### Shadow Vocabulary
- **Card Rest** (`0 2px 8px rgba(0,0,0,0.25)`): Default card state. Edge definition only.
- **Card Hover** (`0 20px 60px rgba(0,0,0,0.45)`): Elevated card. Dramatic depth on interaction.
- **Gold Glow** (`0 0 24px var(--gold-glow)`): Behind primary buttons, active chips, focused inputs. The only colored shadow.

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest. The card rest shadow provides edge definition, not depth. Dramatic shadows appear only on hover as interactive feedback. The sidebar, toolbar, and page background have no shadows at all.

## Shapes

Corners are rounded throughout with a 4-step scale: `xs` (4px, scrollbar thumb), `sm` (6px, small chips), `md` (10px, inputs, buttons, sidebar links), `lg` (12px, dropdowns, search bar), `xl` (16px, KPI strips), `2xl` (20px, choice cards, browse hero). `--radius-full` (9999px) creates pill shapes for chips, badges, and the language toggle.

Cards use 14px radius — slightly larger than the md token. The form card uses a gold radial gradient at the top-left corner, creating an asymmetric accent that distinguishes it from standard content cards.

**Border strategy:** Borders are 1px solid, using the Line scale. Cards use `border-subtle` (near-invisible at rest), transitioning to `border-hover` on interaction. Active elements use `border-active` (gold-tinted). The gold border is the system's way of saying "this is selected" or "this is special."

## Components

### Buttons
- **Shape:** Rounded (10px / `--radius-md`). Full-width by default.
- **Primary:** Gold gradient background (`#8B6914 → #5C4410 → #332008`). White text. 12px 24px padding. Min height 48px. Contains a `::after` pseudo-element shimmer on hover. Hover lifts 2px with gold glow shadow. Active scales to 98%. Loading state pulses opacity. Disabled is 40% opacity with grayscale filter. Supports `.btn-sub` child for descriptive sub-label text.
- **Secondary (Ghost):** Transparent background. Dashed border (`border-hover`). Muted text. Transitions to gold border + white text on hover. Used for export, share, and secondary form actions.
- **Dropdown selects:** Custom styled with SVG chevron. Dark surface bg. Gold focus ring. Appearance reset for consistency.

### Cards
- **Shape:** 14px radius. 24px internal padding. 1px `border-subtle` at rest.
- **Glass effect:** `::before` gradient border (white 4% → transparent) with mask-composite. `::after` top-edge hairline (white 6% gradient). Both pointer-events: none.
- **Hover:** Border transitions to `border-hover`. Shadow deepens to `0 20px 60px`. Subtle scale to 99.5% on active click.
- **Card Header:** Uppercase 13px muted label with bottom border. Optional.
- **Form Card variant:** Gold radial gradient at top-left corner, gold-tinted border. Visually distinguishes the primary action surface from display cards.

### Form Inputs
- **Style:** Dark surface background. 1.5px `border-subtle` stroke. 42px height. 14px border radius. Inter font, 14px.
- **Hover:** Border lightens, background darkens slightly.
- **Focus:** Gold border (`--color-accent`). Gold glow box-shadow (`0 0 0 3px var(--gold-glow)`). No outline.
- **Error:** Red border + red glow. Inline error text in red below the field. Role="alert" for screen readers.
- **Placeholder:** 20% opacity white. Muted and unobtrusive.
- **Readonly:** Reduced opacity background, not-allowed cursor. Used for spec field (GCC default).

### Sidebar Navigation
- **Style:** 250px fixed column. Dark sidebar surface. Sticky top-0, full viewport height.
- **Nav items:** 10px vertical padding, 18px horizontal. 10px border radius. Muted text at rest. Hover: light bg, secondary text color. Active: gold gradient left-border (30% → 12% opacity), white text, gold-tinted border, 600 weight.
- **Section labels:** 12px uppercase, muted, 0.09em tracking. Visual grouping without interactive behavior.
- **Brand area:** "CV" monogram on gold gradient square with glow. Two-line title (brand name + subtitle).
- **Footer:** Profile avatar (gold gradient initials), system health dot (green pulse).
- **Mobile:** Fixed overlay with translateX(-100%). Slide-in on hamburger toggle. Dark backdrop.

### Chips
- **Quick-filter chips:** Pill shape (`--radius-full`). 6px 14px padding. Subtle border at rest. Muted text.
- **Active state:** Gold-tinted background (`--gold-glow`). Gold border. Gold text. 600 weight.
- **Hover:** Border lightens, text brightens.
- **Marketplace chips:** Brand-colored dot + name. Muted border. Used in trust strip to show data sources.

### Choice Cards (Homepage CTAs)
- **Shape:** 20px radius. 32px internal padding. 360px max-width, 380px min-height. Flex column.
- **Structure:** Gold gradient logo square (52px, with inner highlight) + heading + description + arrow circle.
- **Hover:** Lifts 3px. Gold border. Gold glow shadow. Arrow slides right 4px and changes to gold.
- **Active:** Scales to 98%.
- **Focus-visible:** Gold ring shadow. Accessible via role="button" + tabindex="0" + keyboard handlers.

### Make Cards (Browse Grid)
- **Shape:** 16px radius. 24px internal padding. Auto-fill grid (min 200px). Top-edge hairline.
- **Structure:** Logo circle (40px, white bg with brand SVG or letter avatar) + brand name + 2-stat grid (listings/price) + trend badge + volume bar.
- **Hover:** Lifts 3px. Gold border + glow. Logo image scales 110%.
- **Volume bar:** Gold gradient fill with transform:scaleX animation. 3px height.

## Do's and Don'ts

### Do:
- **Do** use the 8px spatial grid. Every gap, padding, and margin is a multiple of 8px via `--space-N` tokens.
- **Do** use gold only on primary CTAs, active states, and brand moments. A card with a gold border is special; a page with six of them is noise.
- **Do** pair every green/red semantic indicator with an icon or text label. Color alone must never be the sole differentiator.
- **Do** use the card component for all content containers. The glass-morphism effect with `::before`/`::after` is the system's signature.
- **Do** show skeleton loading states for any async data. A blank card is broken; a pulsing skeleton is loading.
- **Do** use `aria-busy` on loading regions, `role="alert"` on error messages, and `aria-hidden` on decorative dividers.
- **Do** support Arabic RTL via the `lang.js` module. All user-facing text should have `data-i18n` attributes.

### Don't:
- **Don't** use gold as body text or card backgrounds. Gold is an accent; overuse destroys its impact.
- **Don't** add new colors outside the defined palette without design system review. The 12-chart color array is fixed; pick from it for data visualization.
- **Don't** use `background-attachment: fixed`. It causes scroll jank and is disabled on iOS Safari.
- **Don't** animate `width`, `height`, `padding`, or `margin`. Use `transform` and `opacity` to avoid layout thrash.
- **Don't** ship inline styles. Use CSS classes that reference design tokens. Inline styles bypass the token system and create specificity wars.
- **Don't** duplicate UI blocks between Sell and Buy pages. One rail panel definition, cloned at runtime.
- **Don't** present hardcoded numbers as live data. If a KPI isn't backed by an API call, mark it as "Industry data" or remove it.
- **Don't** use "Enterprise," "cutting-edge," "world-class," or "next-generation" in copy. Say what the product literally does.
