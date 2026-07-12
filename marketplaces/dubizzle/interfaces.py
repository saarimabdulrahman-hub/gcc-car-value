from abc import ABC, abstractmethod
from schema.listing import CanonicalListing


class MarketplaceConnector(ABC):
    """Abstract marketplace connector. All marketplace scrapers implement this."""
    @abstractmethod
    async def run(self, fetch_page) -> list[CanonicalListing]: ...
