# GCC Car Value — Analytics Query Engine

**Date:** 2026-07-12  
**Package:** `analytics/query/`

## Architecture

```
HistoryRepository (storage layer)
    │
    ▼
QueryEngine (read-only analytics)
    │
    ├── PriceHistoryAnalyzer  → vehicle price timelines
    ├── Aggregator             → average, median, volatility, group-by
    ├── TrendEngine            → price trends, inventory trends, direction
    ├── InventoryAnalytics     → active, new, removed, duration
    ├── TimeSeriesEngine       → daily, weekly, monthly, quarterly, yearly
    ├── Filters                → marketplace, make/model, price/mileage range, date range
    └── QueryCache             → TTL-based, thread-safe
```

## Queries

```python
from analytics.query import QueryEngine

engine = QueryEngine(repository)

# Price
engine.price_history("fp-abc")                    # [{price, currency, at}, ...]
engine.average_price(make="Toyota", model="Camry") # float
engine.median_price(marketplace="dubizzle")         # float
engine.price_volatility(make="Land Cruiser")        # float

# Inventory
engine.active_count()                               # int
engine.new_listings(days=7)                        # int
engine.removed_listings(days=30)                   # int
engine.average_duration(marketplace="dubizzle")     # days

# Trends
engine.price_trend(make="Corolla", periods=8)       # TrendResult {direction: "up", change_pct: 3.2}
engine.inventory_trend(marketplace="dubizzle")      # TrendResult

# Time-Series
engine.time_series("price", "monthly", limit=12)    # [TimeSeriesPoint, ...]
engine.monthly_average(make="Camry", months=6)      # [TimeSeriesPoint, ...]

# Aggregations
engine.aggregate("price", group_by="marketplace")   # AggregationResult {groups: [...]}
```

## Filters

```python
FilterCriteria(
    marketplace="dubizzle", make="Toyota", model="Camry",
    price_min=50000, price_max=150000,
    mileage_min=0, mileage_max=200000,
    year_min=2018, year_max=2023,
)
```

## Time-Series Periods

| Period | Key Format | Example |
|--------|-----------|---------|
| `daily` | `YYYY-MM-DD` | `2026-07-12` |
| `weekly` | `YYYY-Www` | `2026-W28` |
| `monthly` | `YYYY-MM` | `2026-07` |
| `quarterly` | `YYYY-Qn` | `2026-Q3` |
| `yearly` | `YYYY` | `2026` |

## Cache

TTL-based, thread-safe. `hit_rate` available for monitoring.

## Verified

- Average/median/volatility on seeded data
- Marketplace and make filtering
- Cache set/get, TTL expiry, invalidation, hit rate
- 644 tests passing with no regression

---

*Query engine documented 2026-07-12.*
