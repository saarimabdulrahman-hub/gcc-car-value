# GCC Car Value — OpenSooq Marketplace Connector

**Date:** 2026-07-12  
**Package:** `marketplaces/opensooq/`

## Multi-Country Architecture

```
OpenSooqPipeline(config=OpenSooqConfig(country="KW"))
    │
    ├── Discovery    → kw.opensooq.com/vehicles?make=toyota
    ├── Pagination   → page 1..N
    ├── Extraction   → cards + details via DOM Engine
    ├── Mapper       → CanonicalListing (country=KW, currency=KWD)
    ├── Normalization → GCC canonicalization with Kuwait aliases
    └── Validation   → Schema + KWD currency check
```

## Country Configuration

```python
# 6 countries, one codebase
COUNTRY_CONFIGS = {
    "AE": {"base_url": "https://ae.opensooq.com", "currency": "AED", "timezone": "Asia/Dubai"},
    "SA": {"base_url": "https://sa.opensooq.com", "currency": "SAR", "timezone": "Asia/Riyadh"},
    "KW": {"base_url": "https://kw.opensooq.com", "currency": "KWD", "timezone": "Asia/Kuwait"},
    "QA": {"base_url": "https://qa.opensooq.com", "currency": "QAR", "timezone": "Asia/Qatar"},
    "BH": {"base_url": "https://bh.opensooq.com", "currency": "BHD", "timezone": "Asia/Bahrain"},
    "OM": {"base_url": "https://om.opensooq.com", "currency": "OMR", "timezone": "Asia/Muscat"},
}
```

## Usage

```python
from marketplaces.opensooq import OpenSooqPipeline
from marketplaces.opensooq.config import OpenSooqConfig

# UAE
pipeline = OpenSooqPipeline(OpenSooqConfig(country="AE"))
listings = await pipeline.run(fetch_page)

# Kuwait — same code, different config
pipeline_kw = OpenSooqPipeline(OpenSooqConfig(country="KW"))
listings_kw = await pipeline_kw.run(fetch_page)
```

## Capability Manifest

```python
OpenSooqCapabilities(
    supports_multi_country=True,  # Key differentiator
    supports_rtl=True,            # Arabic interface
    supported_countries=["AE","SA","KW","QA","BH","OM"],
)
```

## Verified

- All 6 countries have valid base URLs, currencies, timezones
- Config auto-fills URLs and checkpoint paths from country code
- AE mapper produces AED/opensooq_ae; KW mapper produces KWD/opensooq_kw
- Same pipeline code works for all 6 countries — zero code duplication

---

*OpenSooq connector documented 2026-07-12.*
