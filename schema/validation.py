"""Schema validation — required fields, ranges, enum values."""

from datetime import datetime
from schema.listing import CanonicalListing
from schema.enums import Currency, Country
from schema.errors import MissingRequiredFieldError, InvalidFieldError


class SchemaValidator:
    """Validates a CanonicalListing against the schema rules."""

    def __init__(self, strict: bool = True,
                 min_year: int = 1990):
        self.strict = strict
        self.min_year = min_year

    def validate(self, listing: CanonicalListing) -> list[str]:
        """Return list of validation errors. Empty list = valid."""
        errors = []

        # --- Required fields ---
        self._required(errors, listing.marketplace, "marketplace")
        self._required(errors, listing.marketplace_listing_id, "marketplace_listing_id")
        self._required(errors, listing.listing_url, "listing_url")
        self._required(errors, listing.vehicle.make, "make")
        self._required(errors, listing.vehicle.model, "model")

        # --- Year ---
        if listing.vehicle.year > 0:
            current = datetime.utcnow().year
            if listing.vehicle.year < self.min_year:
                errors.append(f"year {listing.vehicle.year} is below minimum {self.min_year}")
            if listing.vehicle.year > current + 1:
                errors.append(f"year {listing.vehicle.year} is in the future")
        else:
            if self.strict:
                errors.append("year is required")

        # --- Price ---
        if listing.pricing.amount <= 0:
            errors.append("price must be positive")
        if listing.pricing.currency and listing.pricing.currency not in Currency.__members__.values():
            errors.append(f"invalid currency: {listing.pricing.currency}")

        # --- Mileage ---
        if listing.vehicle.mileage_km < 0:
            errors.append("mileage cannot be negative")

        # --- Location ---
        if listing.location.country and listing.location.country not in Country.__members__.values():
            errors.append(f"invalid country: {listing.location.country}")

        # --- URL ---
        if listing.listing_url and not listing.listing_url.startswith("http"):
            errors.append("listing_url must start with http")

        # --- Images ---
        if len(listing.images.gallery) > 50:
            errors.append(f"gallery has {len(listing.images.gallery)} images, max 50")

        # --- Seller rating ---
        if listing.seller.rating < 0 or listing.seller.rating > 5:
            errors.append(f"seller rating {listing.seller.rating} must be 0-5")

        return errors

    def validate_or_raise(self, listing: CanonicalListing) -> None:
        errors = self.validate(listing)
        if errors:
            raise InvalidFieldError("; ".join(errors))

    def _required(self, errors: list[str], value, name: str) -> None:
        if not value:
            errors.append(f"{name} is required")

    def is_valid(self, listing: CanonicalListing) -> bool:
        return len(self.validate(listing)) == 0
