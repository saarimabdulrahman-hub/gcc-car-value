# GCC Car Value — ML Feature Store & Training Dataset Builder

**Date:** 2026-07-12  
**Package:** `ml/features/`

## Architecture

```
Historical Data → QueryEngine → IntelligenceEngine
                                      │
                                      ▼
                              DatasetBuilder.build()
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            FeatureRegistry    FeatureStore    DatasetVersion
            (28 features)      (vectors)       (metadata)
                    │                 │
                    ▼                 ▼
            FeatureValidator   Export (CSV/JSONL/Parquet)
```

## Feature Catalog (28 pre-defined)

| Group | Features |
|-------|----------|
| Vehicle Identity | make, model, year, trim, body_type, fuel_type, transmission, specification |
| Vehicle Condition | mileage_km, color, vehicle_age_years, seller_type |
| Pricing | price, currency |
| Location | country, city |
| History | days_active, listing_age_days, snapshot_count |
| Market Intelligence | price_index, depreciation_rate, liquidity_score, market_health_score, price_percentile |
| Forecast Inputs | ma_30d, volatility_90d, inventory_delta, momentum_score, freshness_score |

## Usage

```python
from ml.features import DatasetBuilder

builder = DatasetBuilder(repo, query_engine, intelligence)
version = builder.build(
    make="Toyota", marketplace="dubizzle",
    min_year=2018, max_rows=10000,
)
# version.row_count → 5000
# version.checksum → "a1b2c3d4e5f6..."

builder.export_csv("toyota_dubai.csv")
df = builder.to_dataframe()
```

## Dataset Versioning

```python
DatasetVersion(
    dataset_id="dubizzle_toyota_1750000000",
    version=1, row_count=5000, feature_count=28,
    checksum="a1b2c3d4e5f6...",
    feature_schema_version=4241,
)
```

## Validation

- Required features: make, model, year (must not be missing)
- Numeric ranges: year [1990, 2027], mileage [0, 1M], price [0, 10M]
- Categorical: body_type, fuel_type, transmission, specification, currency, country, seller_type
- Schema version changes when features are added/removed

## Verified

- 28 pre-defined features loaded from catalog
- Registry: register, get, duplicate rejection, schema version
- Store: save/load/build vectors, to_rows export
- Validation: range violations, categorical checks, required field missing
- Dataset versioning: ID, checksum, row count, schema version
- 663 tests passing with no regression

---

*Feature store documented 2026-07-12.*
