"""Filter engine — applies FilterCriteria to listings."""

from analytics.query.models import FilterCriteria


def apply_filters(store, filters: FilterCriteria) -> list:
    """Apply FilterCriteria to a CurrentListingStore. Returns matching entries."""
    entries = list(store._store.values())
    f = filters

    if f.marketplace: entries = [e for e in entries if e.marketplace == f.marketplace]
    if f.make: entries = [e for e in entries if e.data.get("make", "").lower() == f.make.lower()]
    if f.model: entries = [e for e in entries if e.data.get("model", "").lower() == f.model.lower()]
    if f.city: entries = [e for e in entries if e.data.get("city", "").lower() == f.city.lower()]
    if f.year_min: entries = [e for e in entries if e.data.get("year", 0) >= f.year_min]
    if f.year_max: entries = [e for e in entries if e.data.get("year", 0) <= f.year_max]
    if f.price_min: entries = [e for e in entries if e.price >= f.price_min]
    if f.price_max: entries = [e for e in entries if e.price <= f.price_max]
    if f.mileage_min: entries = [e for e in entries if e.mileage_km >= f.mileage_min]
    if f.mileage_max: entries = [e for e in entries if e.mileage_km <= f.mileage_max]
    if f.lifecycle: entries = [e for e in entries if e.lifecycle_state == f.lifecycle]
    if f.seller_type: entries = [e for e in entries if e.data.get("seller_type", "") == f.seller_type]
    if f.body_type: entries = [e for e in entries if e.data.get("body_type", "") == f.body_type]

    if f.offset: entries = entries[f.offset:]
    if f.limit: entries = entries[:f.limit]

    return entries
