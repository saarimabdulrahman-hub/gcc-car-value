# GCC Car Value — Vehicle Canonicalization Engine

**Date:** 2026-07-12  
**Package:** `normalization/`

## Architecture

```
CanonicalListing (raw marketplace values)
    │
    ▼
NormalizationEngine.normalize(listing)
    │
    ├── Make:     "toyota motors"    → "Toyota"      (68 aliases)
    ├── Model:    "landcruiser"      → "Land Cruiser" (per-make aliases)
    ├── Trim:     "V X R"           → "VXR"          (space/hyphen cleanup)
    ├── Trans:    "auto"            → "automatic"    (13 aliases)
    ├── Fuel:     "gasoline"        → "petrol"       (15 aliases, Arabic support)
    ├── Body:     "4x4"             → "suv"          (17 aliases)
    ├── Color:    "pearl white"     → "White"        (50+ aliases, Arabic)
    ├── Spec:     "gulf spec"       → "GCC"          (18 aliases, Arabic)
    ├── Mileage:  50000 miles       → 80467 km       (auto-convert)
    ├── City:     "rak"             → "Ras Al Khaimah" (25 GCC cities)
    └── Originals → listing.metadata["original_values"]
    │
    ▼
NormalizationReport (changed fields, confidence, rules applied)
```

## Usage

```python
from normalization import NormalizationEngine
from schema.listing import CanonicalListing

engine = NormalizationEngine()
report = engine.normalize(listing)

# listing.vehicle.make was "toyota motors" → now "Toyota"
# report.changed_fields → 3 (make, model, color were normalized)
# listing.metadata["original_values"] → {"make": "toyota motors", ...}
```

## Alias Coverage

| Field | Aliases | Languages |
|-------|---------|-----------|
| Make | 68 | en |
| Model | 50+ (per-make) | en |
| Transmission | 13 | en |
| Fuel | 15 | en, ar |
| Body | 17 | en |
| Color | 50+ | en, ar |
| Spec | 18 | en, ar |
| City | 25 | en, ar |

## Confidence Scoring

| Rule | Confidence |
|------|-----------|
| Exact alias match | 1.0 |
| Trim normalization | 0.9 |
| Title case fallback | 0.5–0.7 |
| Empty value | 1.0 |

## Verified

- 49 parametrized tests covering all normalizers
- "toyota motors" → Toyota, "landcruiser" → Land Cruiser, "lc" → Land Cruiser
- "auto"/"at"/"a/t" → automatic, "gasoline" → petrol
- "pearl white" → White, "gulf spec" → GCC
- 50000 miles → 80467 km
- "rak" → Ras Al Khaimah, "makkah" → Mecca
- Original values preserved in metadata

---

*Canonicalization engine documented 2026-07-12.*
