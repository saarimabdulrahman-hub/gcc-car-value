# Implementation Plan: "Browse Models" Page Revamp

## Context
Redesigning the "Browse Models" page to match a high-fidelity enterprise dark-mode UI. The key requirement is a seamless, immersive hero area with an overlay of floating KPIs, removing static headers in favor of floating navigation, and positioning the page background/hero elements (skyline, cars, map) to feel like one continuous, unconstrained canvas.

## Approved Plan (Status: Finalized)
1. **Layout Strategy**:
   - Move all common styles into a shared `styles.css`.
   - Update `browse.html` to use absolute/floating positioning for the header elements.
   - Use a full-page CSS background (`page-hero-container`) to eliminate the "hero card" container effect.
   - Position KPI cards to overlap the hero background (`margin-top: -100px`) to achieve the requested "floating on image" effect.

2. **File Structure**:
   - `ui/browse.html`: The main page structure with absolute positioning for header elements and hero background.
   - `ui/styles.css`: Centralized design system tokens (Graphite/Gold) and layout utility classes.

3. **Key Components**:
   - **Floating Header**: Absolute-positioned navigation overlay.
   - **Background Hero**: Full-width/height background with integrated map overlay and car illustration.
   - **Floating KPI Grid**: Overlapping the bottom of the hero area.
   - **Featured Manufacturers**: Gold-ranked grid list.
   - **Insights/Recently Viewed**: Sidebar-style widgets.

## Location of this Plan
- **Plan File**: `C:\Users\saari\.claude\plans\elegant-enchanting-pie.md`
