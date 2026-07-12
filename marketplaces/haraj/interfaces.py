from abc import ABC, abstractmethod
from schema.listing import CanonicalListing

class MarketplaceConnector(ABC):
    @abstractmethod
    async def run(self, fetch_page) -> list[CanonicalListing]: ...
