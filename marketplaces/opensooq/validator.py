from schema.validation import SchemaValidator
from schema.listing import CanonicalListing
from marketplaces.opensooq.constants import COUNTRY_CONFIGS

class OpenSooqValidator:
    def __init__(self, country="AE"): self._sv=SchemaValidator(); self._country=country
    def validate(self, listing: CanonicalListing) -> list[str]:
        errors=self._sv.validate(listing)
        cc=COUNTRY_CONFIGS.get(self._country,{})
        expected_currency=cc.get("currency","AED")
        if listing.pricing.currency and listing.pricing.currency != expected_currency:
            errors.append(f"OpenSooq {self._country} listings must be in {expected_currency}")
        return errors
