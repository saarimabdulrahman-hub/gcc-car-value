"""Listing fingerprint — stable SHA-256 identifier across crawls."""

import hashlib
from schema.listing import CanonicalListing


class ListingFingerprint:
    """Generates a deterministic fingerprint for a listing.

    Stable across crawls — same listing produces the same fingerprint
    even if price/mileage change. Based on identity fields only.
    """

    @staticmethod
    def compute(listing: CanonicalListing) -> str:
        """Generate SHA-256 fingerprint from listing identity fields."""
        raw = "|".join([
            listing.marketplace,
            listing.marketplace_listing_id,
            listing.vehicle.make.strip().lower(),
            listing.vehicle.model.strip().lower(),
            str(listing.vehicle.year),
            listing.vehicle.vin.strip().lower() if listing.vehicle.vin else "",
            listing.listing_url.strip().lower(),
        ])
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def compute_from_fields(marketplace: str, external_id: str,
                            make: str, model: str, year: int,
                            url: str = "") -> str:
        """Compute fingerprint from individual fields."""
        raw = "|".join([
            marketplace, external_id,
            make.strip().lower(), model.strip().lower(),
            str(year), "", url.strip().lower(),
        ])
        return hashlib.sha256(raw.encode()).hexdigest()
