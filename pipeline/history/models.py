"""History data models — snapshots, lifecycle states, change records."""

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class LifecycleState(StrEnum):
    NEW = "new"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    REMOVED = "removed"
    DUPLICATE = "duplicate"
    ARCHIVED = "archived"


@dataclass
class FieldChange:
    """A single field change between two snapshots."""
    field: str
    old_value: str = ""
    new_value: str = ""

    @property
    def changed(self) -> bool: return self.old_value != self.new_value

    def summary(self) -> str:
        if not self.changed: return f"{self.field}: unchanged"
        return f"{self.field}: {self.old_value} → {self.new_value}"


@dataclass
class ListingSnapshot:
    """A point-in-time snapshot of a listing."""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str = ""                # Canonical listing ID
    marketplace: str = ""
    fingerprint: str = ""               # SHA-256
    price: float = 0.0
    currency: str = ""
    mileage_km: int = 0
    description: str = ""
    seller_name: str = ""
    image_count: int = 0
    status: str = "active"
    raw_data: dict = field(default_factory=dict)
    captured_at: float = field(default_factory=time.time)
    crawl_number: int = 0
    lifecycle_state: LifecycleState = LifecycleState.NEW
    changes: list[FieldChange] = field(default_factory=list)


@dataclass
class ListingHistory:
    """Complete history of a listing across crawls."""
    listing_id: str = ""
    marketplace: str = ""
    fingerprint: str = ""
    first_seen: float = 0.0
    last_seen: float = 0.0
    snapshots: list[ListingSnapshot] = field(default_factory=list)
    lifecycle_state: LifecycleState = LifecycleState.NEW
    crawl_count: int = 0
    update_count: int = 0

    @property
    def price_history(self) -> list[dict]:
        return [{"price": s.price, "currency": s.currency, "at": s.captured_at}
                for s in self.snapshots if s.price > 0]

    @property
    def mileage_history(self) -> list[dict]:
        return [{"mileage_km": s.mileage_km, "at": s.captured_at}
                for s in self.snapshots if s.mileage_km > 0]

    @property
    def days_active(self) -> float:
        if self.last_seen <= 0: return 0
        return (self.last_seen - self.first_seen) / 86400.0

    @property
    def snapshot_count(self) -> int: return len(self.snapshots)
