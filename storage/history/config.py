from dataclasses import dataclass

@dataclass
class StorageConfig:
    partition_by_month: bool = True
    partition_by_marketplace: bool = True
    max_snapshots_per_listing: int = 500
    soft_delete: bool = True
    index_fingerprint: bool = True
    index_timestamp: bool = True
    index_lifecycle: bool = True
    index_price: bool = True
