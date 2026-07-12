"""Haraj-specific validation."""

from schema.validation import SchemaValidator
from schema.listing import CanonicalListing


class HarajValidator:
    def __init__(self): self._schema = SchemaValidator()
    def validate(self, listing: CanonicalListing) -> list[str]:
        errors = self._schema.validate(listing)
        if listing.pricing.currency and listing.pricing.currency != "SAR":
            errors.append("Haraj SA listings must be in SAR")
        return errors
