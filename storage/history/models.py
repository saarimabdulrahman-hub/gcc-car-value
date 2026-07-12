"""Storage data models."""

from dataclasses import dataclass, field
from pipeline.history.models import ListingSnapshot, ListingHistory, LifecycleState


@dataclass
class CurrentListing:
    """The latest version of a listing — exactly one per fingerprint."""
    fingerprint: str
    listing_id: str
    marketplace: str
    price: float = 0.0
    currency: str = ""
    mileage_km: int = 0
    seller_name: str = ""
    status: str = "active"
    lifecycle_state: LifecycleState = LifecycleState.NEW
    last_updated: float = 0.0
    snapshot_count: int = 0
    data: dict = field(default_factory=dict)


@dataclass
class TimelineEntry:
    """A single point on a listing's timeline."""
    timestamp: float
    snapshot_id: str
    price: float = 0.0
    mileage_km: int = 0
    lifecycle_state: str = ""
    seller_name: str = ""
    image_count: int = 0


@dataclass
class PartitionKey:
    """Composite partition key: marketplace + year_month."""
    marketplace: str
    year_month: str  # "2026-07"

    @classmethod
    def from_timestamp(cls, marketplace: str, ts: float) -> "PartitionKey":
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return cls(marketplace=marketplace, year_month=dt.strftime("%Y-%m"))
