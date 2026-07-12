# GCC Car Value — Canonical Vehicle Listing Schema

**Date:** 2026-07-12  
**Package:** `schema/`

## Architecture

```
Marketplace HTML → Scraper → CanonicalListing → Normalization → DB → ML → API
                              ↑
                    Single source of truth
```

## CanonicalListing Structure

```
CanonicalListing
├── listing_id, marketplace, marketplace_listing_id, listing_url
├── schema_version, status, timestamps
├── Vehicle (make, model, year, mileage, body_type, fuel_type, transmission, drivetrain, engine_size, spec, etc.)
├── Pricing    (amount, currency, negotiable, tax_included, finance_available)
├── Location   (country, state, city, district, lat, lon)
├── Seller     (type, name, dealer_id, verified, rating, phone, chat)
├── Images     (cover_image, gallery, image_count, video_available)
└── History    (accident, service, owners, warranty, export/import)
```

## Marketplace Mapping

```
Dubizzle:  "Price"            → pricing.amount = 125000.0
Haraj:     "Selling Price"    → pricing.amount = 125000.0
OpenSooq:  "Price AED"        → pricing.amount = 125000.0

Dubizzle:  "Kilometers"       → vehicle.mileage_km = 120000
Haraj:     "Distance Travelled" → vehicle.mileage_km = 120000
```

All become the same canonical fields. Downstream systems never see marketplace-specific names.

## Validation Rules

| Rule | Error |
|------|-------|
| marketplace required | "marketplace is required" |
| make required | "make is required" |
| price > 0 | "price must be positive" |
| year 1990..current+1 | "year is below minimum" / "year is in the future" |
| mileage >= 0 | "mileage cannot be negative" |
| currency in AED/SAR/KWD/QAR/BHD/OMR/USD | "invalid currency" |
| country in AE/SA/KW/QA/BH/OM | "invalid country" |
| seller rating 0.0-5.0 | "seller rating must be 0-5" |

## Verification

- 5 sub-models with 60+ fields total
- 10 enums covering marketplace, fuel, transmission, body type, drivetrain, currency, country, spec
- Validation: required fields, range checks, enum membership
- `to_dict()` serialization for flat JSON/DB storage
- 20 tests including negative price, future year, invalid currency, missing make

---

*Canonical schema documented 2026-07-12.*
