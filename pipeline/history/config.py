from dataclasses import dataclass, field

@dataclass
class HistoryConfig:
    similarity_threshold: float = 0.85       # For deduplication
    max_snapshots_per_listing: int = 100
    freshness_decay_days: int = 14           # Days before freshness reaches 0
    track_fields: list[str] = field(default_factory=lambda: [
        "price", "mileage_km", "description", "seller_name",
        "image_count", "status",
    ])
