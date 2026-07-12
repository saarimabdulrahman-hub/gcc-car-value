"""Haraj Pipeline — orchestrates the full Haraj SA acquisition flow."""

from datetime import datetime, timezone
from typing import Callable, Awaitable
import structlog

from schema.listing import CanonicalListing
from schema.validation import SchemaValidator
from normalization.engine import NormalizationEngine
from marketplaces.haraj.config import HarajConfig
from marketplaces.haraj.discovery import HarajDiscovery
from marketplaces.haraj.pagination import HarajPagination
from marketplaces.haraj.listing import HarajListingExtractor
from marketplaces.haraj.details import HarajDetailExtractor
from marketplaces.haraj.mapper import HarajMapper
from marketplaces.haraj.checkpoint import HarajCheckpoint
from marketplaces.haraj.statistics import HarajStatistics
from marketplaces.haraj.capabilities import HarajCapabilities

logger = structlog.get_logger()


class HarajPipeline:
    """Full Haraj SA acquisition pipeline. Orchestrates platform frameworks only."""

    def __init__(self, config: HarajConfig | None = None):
        self.config = config or HarajConfig()
        self.capabilities = HarajCapabilities()
        self._discovery = HarajDiscovery(self.config)
        self._pagination = HarajPagination(self.config)
        self._listing_extractor = HarajListingExtractor()
        self._detail_extractor = HarajDetailExtractor()
        self._mapper = HarajMapper()
        self._normalizer = NormalizationEngine()
        self._validator = SchemaValidator()
        self._checkpoint = HarajCheckpoint(self.config)
        self._stats = HarajStatistics()

    async def run(self,
                  fetch_page: Callable[[str], Awaitable[str]],
                  resume: bool = False,
                  make: str = "", city: str = "",
                  max_pages: int | None = None) -> list[CanonicalListing]:
        self._stats.start()
        if resume:
            state = self._checkpoint.load()
            if state:
                self._pagination.restore_state(state.get("pagination", {}))

        self._pagination.start()
        all_listings: list[CanonicalListing] = []
        max_p = max_pages or self.config.max_pages

        for page_num in range(1, max_p + 1):
            try:
                self._pagination.next_page()
            except Exception:
                break

            url = self._discovery.search_url(page=page_num, make=make, city=city)
            html = await fetch_page(url)
            self._stats.record_page()

            from browser.dom.document import DOMDocument
            doc = DOMDocument.from_html(html, url=url)
            cards = self._listing_extractor.extract_cards(doc)
            self._stats.record_found(len(cards))

            if not cards:
                self._pagination.mark_last_page()
                break

            for card in cards:
                try:
                    listing = await self._process(card, fetch_page)
                    if listing:
                        all_listings.append(listing)
                        self._stats.record_processed()
                except Exception as e:
                    self._stats.record_failure()
                    logger.warning("haraj_listing_failed", url=card.get("url", "")[:120],
                                 error=str(e)[:200])

            self._checkpoint.save({
                "pagination": self._pagination.checkpoint_state(),
                "total_listings": len(all_listings),
            })

        self._stats.finish()
        return all_listings

    async def _process(self, card: dict, fetch_page) -> CanonicalListing | None:
        url = card.get("url", "")
        if not url: return None
        if url.startswith("/"): url = f"{self.config.base_url}{url}"

        html = await fetch_page(url)

        from browser.challenge.manager import ChallengeManager
        if ChallengeManager().detect(html=html, url=url): return None

        from browser.dom.document import DOMDocument
        doc = DOMDocument.from_html(html, url=url)
        details = self._detail_extractor.extract(doc)
        details["url"] = url
        details["listing_id"] = self._extract_id(url)

        for key in ("title", "price", "year", "mileage_km", "location", "image"):
            if not details.get(key) and card.get(key):
                details[key] = card.get(key)

        listing = self._mapper.map_to_canonical(details, url=url,
                                                  listing_id=details.get("listing_id", ""))
        listing.scraped_at = datetime.now(timezone.utc).isoformat()
        self._normalizer.normalize(listing)

        errors = self._validator.validate(listing)
        if errors and self.config.skip_incomplete:
            return None
        return listing

    @staticmethod
    def _extract_id(url: str) -> str:
        import re; m = re.search(r'/(\d{5,})(?:[/?#]|$)', url)
        return m.group(1) if m else ""

    @property
    def stats(self) -> dict: return self._stats.snapshot()
