"""OpenSooq Pipeline — multi-country acquisition orchestrator."""

from datetime import datetime, timezone
from typing import Callable, Awaitable
import structlog

from schema.listing import CanonicalListing
from schema.validation import SchemaValidator
from normalization.engine import NormalizationEngine
from marketplaces.opensooq.config import OpenSooqConfig
from marketplaces.opensooq.discovery import OpenSooqDiscovery
from marketplaces.opensooq.pagination import OpenSooqPagination
from marketplaces.opensooq.listing import OpenSooqListingExtractor
from marketplaces.opensooq.details import OpenSooqDetailExtractor
from marketplaces.opensooq.mapper import OpenSooqMapper
from marketplaces.opensooq.checkpoint import OpenSooqCheckpoint
from marketplaces.opensooq.statistics import OpenSooqStatistics
from marketplaces.opensooq.capabilities import OpenSooqCapabilities

logger = structlog.get_logger()


class OpenSooqPipeline:
    def __init__(self, config: OpenSooqConfig | None = None):
        self.config = config or OpenSooqConfig()
        self.capabilities = OpenSooqCapabilities()
        self._discovery = OpenSooqDiscovery(self.config)
        self._pagination = OpenSooqPagination(self.config)
        self._listing_extractor = OpenSooqListingExtractor()
        self._detail_extractor = OpenSooqDetailExtractor()
        self._mapper = OpenSooqMapper(self.config)
        self._normalizer = NormalizationEngine()
        self._validator = SchemaValidator()
        self._checkpoint = OpenSooqCheckpoint(self.config)
        self._stats = OpenSooqStatistics()

    async def run(self, fetch_page: Callable[[str], Awaitable[str]],
                  resume: bool = False, make: str = "",
                  max_pages: int | None = None) -> list[CanonicalListing]:
        self._stats.start()
        if resume:
            state = self._checkpoint.load()
            if state: self._pagination.restore_state(state.get("pagination", {}))

        self._pagination.start()
        all_listings: list[CanonicalListing] = []
        max_p = max_pages or self.config.max_pages

        for _ in range(1, max_p + 1):
            try: self._pagination.next_page()
            except Exception: break

            url = self._discovery.search_url(page=self._pagination.current_page, make=make)
            html = await fetch_page(url); self._stats.record_page()

            from browser.dom.document import DOMDocument
            doc = DOMDocument.from_html(html, url=url)
            cards = self._listing_extractor.extract_cards(doc)
            self._stats.record_found(len(cards))
            if not cards: self._pagination.mark_last_page(); break

            for card in cards:
                try:
                    listing = await self._process(card, fetch_page)
                    if listing: all_listings.append(listing); self._stats.record_processed()
                except Exception as e:
                    self._stats.record_failure()
                    logger.warning("opensooq_failed", url=card.get("url", "")[:120], error=str(e)[:200])

            self._checkpoint.save({"pagination": self._pagination.checkpoint_state(), "total": len(all_listings)})

        self._stats.finish(); return all_listings

    async def _process(self, card: dict, fetch_page) -> CanonicalListing | None:
        url = card.get("url", "");
        if not url: return None
        if url.startswith("/"): url = f"{self.config.base_url}{url}"

        html = await fetch_page(url)
        from browser.challenge.manager import ChallengeManager
        if ChallengeManager().detect(html=html, url=url): return None

        from browser.dom.document import DOMDocument
        doc = DOMDocument.from_html(html, url=url)
        details = self._detail_extractor.extract(doc)
        details["url"] = url; details["listing_id"] = self._extract_id(url)
        for k in ("title", "price", "year", "mileage_km", "location"):
            if not details.get(k) and card.get(k): details[k] = card.get(k)

        listing = self._mapper.map_to_canonical(details, url=url, listing_id=details.get("listing_id", ""))
        listing.scraped_at = datetime.now(timezone.utc).isoformat()
        self._normalizer.normalize(listing)
        if self._validator.validate(listing) and self.config.skip_incomplete: return None
        return listing

    @staticmethod
    def _extract_id(url: str) -> str:
        import re; m = re.search(r'/(\d{5,})(?:[/?#]|$)', url); return m.group(1) if m else ""

    @property
    def stats(self) -> dict: return self._stats.snapshot()
