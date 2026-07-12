# GCC Car Value — Dubizzle UAE Marketplace Connector

**Date:** 2026-07-12  
**Package:** `marketplaces/dubizzle/`

## Architecture

```
DubizzlePipeline.run(fetch_page)
    │
    ├── Discovery — generate search URLs
    ├── Pagination — page-by-page traversal with checkpoint resume
    │
    ▼
fetch_page(url) → HTML
    │
    ├── ListingExtractor — extract listing cards from search results
    ├── ChallengeManager.detect() — check for bot protection
    │
    ▼
fetch_page(detail_url) → HTML
    │
    ├── DetailExtractor — extract make, model, year, price, mileage, spec, etc.
    ├── Mapper — convert extracted dict → CanonicalListing
    │
    ▼
NormalizationEngine.normalize(listing)
    │
    ▼
SchemaValidator.validate(listing)
    │
    ▼
Output: list[CanonicalListing]
```

## Key Design Principle

**This connector orchestrates — it does NOT implement.**

| Component | Delegates To |
|-----------|-------------|
| DOM parsing | `browser.dom.DOMDocument` |
| Typed extraction | `browser.dom.Extractor` |
| Selectors | `browser.selectors.Selector` |
| Canonical schema | `schema.CanonicalListing` |
| Normalization | `normalization.NormalizationEngine` |
| Validation | `schema.SchemaValidator` |
| Challenge detection | `browser.challenge.ChallengeManager` |

No raw CSS, no browser APIs, no normalization logic exists in this package.

## Pipeline Flow

```python
from marketplaces.dubizzle import DubizzlePipeline

pipeline = DubizzlePipeline()
listings = await pipeline.run(
    fetch_page=my_async_fetcher,   # Your page fetch function
    make="Toyota", model="Land Cruiser",
    max_pages=5,
)
# listings is a list of validated, normalized CanonicalListing objects
```

## Verified

- Discovery: search URLs with make/model/year/price filters, seed URLs
- Pagination: first/next page, max pages, checkpoint save/restore
- Listing extraction: 2 cards extracted from mock search results
- Detail extraction: make, model, year, price, mileage, spec, transmission, fuel, body, color, seller
- Mapper: extracted dict → CanonicalListing with all sub-models populated
- Full pipeline: mock fetcher → 2 listings produced, normalized, and validated

---

*Dubizzle connector documented 2026-07-12.*
