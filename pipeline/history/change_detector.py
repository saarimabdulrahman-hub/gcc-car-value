"""Change detector — field-level diff between listing snapshots."""

from pipeline.history.models import ListingSnapshot, FieldChange


class ChangeDetector:
    """Detects field-level changes between two snapshots.

    Compares tracked fields and returns list of FieldChange objects.
    """

    def __init__(self, tracked_fields: list[str] | None = None):
        self._fields = tracked_fields or [
            "price", "mileage_km", "description", "seller_name",
            "image_count", "status",
        ]

    def detect(self, previous: ListingSnapshot,
               current: ListingSnapshot) -> list[FieldChange]:
        """Compare two snapshots and return all field changes."""
        changes = []
        for field in self._fields:
            old_val = str(getattr(previous, field, ""))
            new_val = str(getattr(current, field, ""))
            changes.append(FieldChange(field=field, old_value=old_val, new_value=new_val))
        return changes

    def has_changes(self, previous: ListingSnapshot,
                    current: ListingSnapshot) -> bool:
        """Check if any tracked field changed."""
        for field in self._fields:
            if str(getattr(previous, field, "")) != str(getattr(current, field, "")):
                return True
        return False
