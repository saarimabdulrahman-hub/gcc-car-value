# GCC Car Value — HTML Normalization & Cleaning Engine

**Date:** 2026-07-12  
**Package:** `markup/`

## Pipeline

```
Raw HTML → Parse (lxml) → Detect Hidden → Remove Scripts/Styles/Comments
                                │                      │
                                ▼                      ▼
                          Mark with            Whitespace Normalization
                          data-was-hidden              │
                                                       ▼
                                               Metadata Extraction
                                                       │
                                                       ▼
                                               Clean DOM → CleaningReport
```

## Usage

```python
from markup import HTMLEngine

engine = HTMLEngine()
soup, report = engine.process(html_string)

# report.scripts_removed     → number of <script> tags removed
# report.styles_removed      → style tags + inline styles removed
# report.comments_removed    → HTML comments removed
# report.hidden_nodes_found  → nodes with display:none/visibility:hidden/hidden attr
# report.metadata            → {title, description, og_title, language, charset, ...}

# soup is a clean BeautifulSoup document ready for DOM extraction
```

## What gets cleaned

| Element | Action |
|---------|--------|
| `<script>`, `<noscript>` | Removed |
| `<style>` | Removed |
| `style="..."` attributes | Removed from all elements |
| HTML comments `<!-- -->` | Removed |
| `display:none` nodes | Marked `data-was-hidden="true"` (not deleted) |
| `visibility:hidden` nodes | Marked `data-was-hidden="true"` |
| `hidden` attribute nodes | Marked `data-was-hidden="true"` |
| Multiple spaces | Collapsed to single space |
| Tabs, NBSP | Normalized |

## Metadata Extracted

Title, description, keywords, language, charset, generator, viewport, canonical URL, OpenGraph (og:title, og:description, og:image, og:type), Twitter cards.

## Verified

- 3 scripts, 1 style, 2 comments, 2 hidden nodes all detected and removed/marked
- Metadata correctly extracted from `<title>`, `<meta>`, and OG tags
- Whitespace collapsed correctly
- Arabic text preserved

---

*HTML engine documented 2026-07-12.*
