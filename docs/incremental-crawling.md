# GCC Car Value — Incremental Crawling & Historical Listing Tracking

**Date:** 2026-07-12  
**Package:** `pipeline/history/`

## Architecture

```
CanonicalListing (from marketplace connector)
    │
    ▼
HistoryManager.process(listing)
    │
    ├── 1. Fingerprint (SHA-256 of identity fields)
    ├── 2. Dedup check (within-crawl only)
    ├── 3. Snapshot creation
    ├── 4. Compare with previous snapshot (change detection)
    ├── 5. Lifecycle determination (NEW/UPDATED/UNCHANGED/REMOVED/DUPLICATE)
    ├── 6. Update ListingHistory (append snapshot, update stats)
    └── 7. Freshness scoring
    │
    ▼
ListingHistory (complete timeline)
    ├── price_history
    ├── mileage_history
    ├── snapshots[]
    └── lifecycle_state
```

## Lifecycle States

```
Crawl 1: Listing seen         → NEW
Crawl 2: Price changed         → UPDATED
Crawl 2: Nothing changed       → UNCHANGED
Crawl 3: Listing not found     → REMOVED
Same crawl: Same listing again → DUPLICATE
Not seen for 30+ days          → ARCHIVED
```

## Usage

```python
from pipeline.history import HistoryManager

mgr = HistoryManager()

# Crawl 1
mgr.start_crawl(1)
for listing in marketplace_results:
    history = mgr.process(listing)
    print(history.lifecycle_state)  # "new"

# Crawl 2 (next week)
mgr.start_crawl(2)
for listing in marketplace_results:
    history = mgr.process(listing)
    if history.lifecycle_state == "updated":
        print(history.price_history)  # [{"price": 125000, "at": ...}, {"price": 122000, "at": ...}]
```

## Components

| Component | Purpose |
|-----------|---------|
| `ListingFingerprint` | SHA-256 from marketplace + external_id + make + model + year + url |
| `SnapshotEngine` | Creates ListingSnapshot from CanonicalListing |
| `ChangeDetector` | Field-level diff (price, mileage, description, seller, images, status) |
| `LifecycleDetector` | Determines state transition (new/updated/unchanged/removed) |
| `DeduplicationEngine` | Within-crawl fingerprint dedup — resets between crawls |
| `FreshnessEngine` | 0-1 score decaying over 14 days since last seen |

## Verified

- Same listing across 3 crawls: NEW → UPDATED → UNCHANGED lifecycle
- Price history tracked: [75000, 72500]
- Fingerprint stable across price/mileage changes
- Within-crawl duplicates detected; cross-crawl treated as updates
- Freshness score: 1.0 for just-seen, decays to 0 over 14 days
- 621 tests passing with no regression

---

*Incremental crawling documented 2026-07-12.*
