# GCC Car Value — DOM Extraction Engine

**Date:** 2026-07-12  
**Package:** `browser/dom/`

## Architecture

```
Marketplace Scraper
    │
    ▼
DOMEngine.parse(html) → DOMDocument
    │
    ├── select(css)       → list[DOMNode]
    ├── select_one(css)   → DOMNode | None
    ├── exists(css)       → bool
    ├── count(css)        → int
    │
    ▼
Extractor.text(node)      → ExtractionResult
Extractor.currency(node)  → ExtractionResult
Extractor.integer(node)   → ExtractionResult
Extractor.year(node)      → ExtractionResult
Extractor.url(node)       → ExtractionResult
Extractor.float_val(node) → ExtractionResult
│
▼
ExtractionValidator — require_node, require_text, require_attr, validate_selectors
```

## Usage

```python
from browser.dom import DOMEngine

engine = DOMEngine()
doc = engine.parse(html_string, url="https://...")

# Query
title_node = doc.select_one("h1")
price_node = doc.select_one(".price")

# Typed extraction
title = engine.extract(doc).text(title_node).value       # "Toyota Land Cruiser 2018"
price = engine.extract(doc).currency(price_node).value   # 125000.0
year  = engine.extract(doc).year(doc.select_one(".year")).value  # 2018

# Validation
engine.validate().require_node(price_node, "price")
```

## Browser Independence

The engine works with raw HTML strings — no browser dependency. HTML can come from any source:
- `await page.content()` (Playwright)
- `driver.page_source` (Selenium)
- `httpx.get(url).text` (raw HTTP)
- Static files

## Typed Extractors

| Method | Input | Output | Example |
|--------|-------|--------|---------|
| `text(node)` | DOMNode | string | "Toyota Land Cruiser" |
| `integer(node)` | DOMNode | int | 2018 |
| `float_val(node)` | DOMNode | float | 3.5 |
| `currency(node)` | DOMNode | float | 125000.0 (cleans AED/SAR) |
| `year(node)` | DOMNode | int | 2018 (validates 1990–current+1) |
| `url(node)` | DOMNode | string | "/listing/123" |

## Verified

- HTML parsing (lxml backend via BeautifulSoup4)
- CSS selectors: single, multiple, existence, count
- Typed extraction: text, int, float, currency, year, URL
- Validation: required nodes, text, attributes, selector validation
- All extractors handle None nodes gracefully

---

*DOM engine documented 2026-07-12.*
