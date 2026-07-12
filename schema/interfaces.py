"""Schema interfaces for future extension."""

from abc import ABC, abstractmethod
from schema.listing import CanonicalListing


class ListingMapper(ABC):
    """Maps marketplace-specific data to the CanonicalListing schema."""
    @abstractmethod
    def map_to_canonical(self, raw: dict) -> CanonicalListing: ...
