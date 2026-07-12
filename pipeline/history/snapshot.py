"""Snapshot engine — creates point-in-time snapshots from listings."""

from schema.listing import CanonicalListing
from pipeline.history.models import ListingSnapshot
from pipeline.history.fingerprint import ListingFingerprint


class SnapshotEngine:
    """Creates ListingSnapshots from CanonicalListings."""

    def __init__(self):
        self._fingerprint = ListingFingerprint()

    def create(self, listing: CanonicalListing,
               crawl_number: int = 1,
               lifecycle_state=None) -> ListingSnapshot:
        """Create a snapshot from a canonical listing."""
        fp = self._fingerprint.compute(listing)
        return ListingSnapshot(
            listing_id=listing.listing_id,
            marketplace=listing.marketplace,
            fingerprint=fp,
            price=listing.pricing.amount,
            currency=listing.pricing.currency,
            mileage_km=listing.vehicle.mileage_km,
            description=listing.metadata.get("extracted_description", ""),
            seller_name=listing.seller.seller_name,
            image_count=listing.images.image_count,
            status=listing.status,
            raw_data=listing.to_dict(),
            crawl_number=crawl_number,
            lifecycle_state=lifecycle_state or "new",
        )
