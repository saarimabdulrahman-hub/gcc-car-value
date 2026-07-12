# GCC Car Value — Historical Dataset Storage Layer

**Date:** 2026-07-12  
**Package:** `storage/history/`

## Architecture

```
HistoryEngine
    │
    ▼
HistoryRepository.save(history)
    │
    ├── CurrentListingStore → latest version per fingerprint
    ├── SnapshotStore → append-only, never overwrite, never delete
    └── TimelineStore → chronological price/mileage/lifecycle queries
    │
    ▼
QueryAPI → latest(), price_history(), active(), recently_updated()
```

## Stores

### CurrentListingStore
- Exactly one entry per fingerprint
- Insert/update/lookup/soft delete
- Filtered queries: active, by marketplace, by lifecycle, recently updated

### SnapshotStore
- Append-only — never overwrite, never delete
- Keyed by (fingerprint, timestamp)
- Sorted chronological retrieval
- Partition-aware: `PartitionKey(marketplace, year_month)`
- `partition_distribution()` for monitoring

### TimelineStore
- `get_timeline(fingerprint)` → full chronological timeline
- `get_price_timeline(fingerprint)` → price-only
- `get_mileage_timeline(fingerprint)` → mileage-only
- `get_lifecycle_timeline(fingerprint)` → lifecycle state transitions

## Usage

```python
from storage.history import HistoryRepository
from pipeline.history import HistoryManager

mgr = HistoryManager()
repo = HistoryRepository()

# Crawl
mgr.start_crawl(1)
for listing in marketplace_results:
    history = mgr.process(listing)
    repo.save(history)  # Persist current + all snapshots

# Query
current = repo.get_current("fp-abc")
prices = repo.get_price_timeline("fp-abc")
active = repo.list_active()
```

## Index Design

| Index | Fields | Unique |
|-------|--------|--------|
| `idx_fingerprint` | `fingerprint` | Yes |
| `idx_marketplace` | `marketplace` | No |
| `idx_timestamp` | `captured_at` | No (partitioned) |
| `idx_lifecycle` | `lifecycle_state` | No |
| `idx_price` | `price` | No |
| `idx_marketplace_ts` | `marketplace`, `captured_at` | No |

## Partitioning

`PartitionKey(marketplace, year_month)` — e.g., `"dubizzle_uae/2026-07"`. Snapshots are grouped by marketplace + month for efficient archival and time-range queries.

## Verified

- Current store: save, get, soft delete, list active/by marketplace
- Snapshot store: append-only, sorted retrieval, partition distribution
- Timeline: price/mileage/lifecycle chronological queries
- Repository: unified save + query across all stores
- Partitions: timestamp-to-PartitionKey mapping

---

*Storage layer documented 2026-07-12.*
