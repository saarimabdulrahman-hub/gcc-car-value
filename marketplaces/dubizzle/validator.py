"""Dubizzle-specific validation — wraps SchemaValidator with marketplace-specific rules."""
from schema.validation import SchemaValidator
from schema.listing import CanonicalListing


class DubizzleValidator:
    """Validates Dubizzle listings against canonical schema + marketplace rules."""

    def __init__(self):
        self._schema_validator = SchemaValidator()

    def validate(self, listing: CanonicalListing) -> list[str]:
        errors = self._schema_validator.validate(listing)
        # Dubizzle-specific: AED currency required
        if listing.pricing.currency and listing.pricing.currency != "AED":
            errors.append("Dubizzle UAE listings must be in AED")
        return errors
