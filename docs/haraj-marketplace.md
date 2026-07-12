# GCC Car Value — Haraj Saudi Arabia Marketplace Connector

**Date:** 2026-07-12  
**Package:** `marketplaces/haraj/`

## Architecture (same as Dubizzle)

```
HarajPipeline.run(fetch_page)
    │
    ├── Discovery — search URLs with make/city filters
    ├── Pagination — page traversal with checkpoint resume
    │
    ▼
fetch_page(url) → HTML (Arabic, RTL)
    │
    ├── ListingExtractor — Arabic/English selectors
    ├── ChallengeManager — bot detection
    │
    ▼
fetch_page(detail_url) → HTML
    │
    ├── DetailExtractor — 15+ fields with Arabic class names
    ├── Mapper → CanonicalListing
    │
    ▼
NormalizationEngine → SchemaValidator
    │
    ▼
Output: list[CanonicalListing]
```

## Key Differences from Dubizzle

| Aspect | Dubizzle | Haraj |
|--------|----------|-------|
| Country | AE | SA |
| Currency | AED | SAR |
| Locale | en-AE | ar-SA |
| Timezone | Asia/Dubai | Asia/Riyadh |
| Layout | LTR | RTL |
| Language | English | Arabic-first |
| Selectors | `.title`, `.price` | `.title`, `.عنوان`, `.price`, `.سعر` |
| Seller type | dealer | private |

## Capability Manifest

```python
HarajCapabilities(
    is_arabic_first=True,
    supports_chat=True,
    supports_phone=True,
    default_currency="SAR",
    default_country="SA",
)
```

## Arabic Support

Arabic text is preserved without translation throughout the pipeline. Selectors match both Arabic (`[class*='سعر']`) and English (`[class*='price']`) class names. The normalization engine handles Arabic make/model/spec/city aliases.

## Verified

- Discovery: search URLs with make/city, seed URLs
- Pagination: page traversal, checkpoint round-trip
- Mapper: extracted dict → CanonicalListing with SAR currency, SA country
- Capability manifest: all fields populated correctly
- Arabic content preserved end-to-end

---

*Haraj connector documented 2026-07-12.*
