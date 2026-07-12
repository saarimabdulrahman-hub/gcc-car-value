"""Dubizzle Pipeline — orchestrates the full acquisition flow.

This is the ONLY file that coordinates the pipeline. It does NOT contain
browser logic, DOM traversal, raw CSS, normalization, or validation.
It wires together all existing platform frameworks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Awaitable
import structlog

from schema.listing import CanonicalListing
from schema.validation import SchemaValidator
from normalization.engine import NormalizationEngine
from marketplaces.dubizzle.config import DubizzleConfig
from marketplaces.dubizzle.discovery import DubizzleDiscovery
from marketplaces.dubizzle.pagination import DubizzlePagination
from marketplaces.dubizzle.listing import DubizzleListingExtractor
from marketplaces.dubizzle.details import DubizzleDetailExtractor
from marketplaces.dubizzle.mapper import DubizzleMapper
from marketplaces.dubizzle.checkpoint import CheckpointManager
from marketplaces.dubizzle.statistics import PipelineStatistics
from marketplaces.dubizzle.errors import ExtractionError

logger = structlog.get_logger()


class DubizzlePipeline:
    """Full Dubizzle UAE acquisition pipeline.

    Orchestrates: discovery → pagination → listing extraction → detail
    extraction → mapping → canonicalization → validation → output.

    Usage (with mocked page fetcher for testing):
        pipeline = DubizzlePipeline()
        listings = await pipeline.run(
            fetch_page=lambda url: "<html>...</html>",
        )
    """

    def __init__(self, config: DubizzleConfig | None = None):
        self.config = config or DubizzleConfig()
        self._discovery = DubizzleDiscovery(self.config)
        self._pagination = DubizzlePagination(self.config)
        self._listing_extractor = DubizzleListingExtractor()
        self._detail_extractor = DubizzleDetailExtractor()
        self._mapper = DubizzleMapper()
        self._normalizer = NormalizationEngine()
        self._validator = SchemaValidator()
        self._checkpoint = CheckpointManager(self.config)
        self._stats = PipelineStatistics()

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    async def run(self,
                  fetch_page: Callable[[str], Awaitable[str]],
                  resume: bool = False,
                  make: str = "", model: str = "",
                  max_pages: int | None = None) -> list[CanonicalListing]:
        """Execute the full pipeline.

        Args:
            fetch_page: Async function(url) → HTML string. In production,
                        this is a browser page fetch. In tests, a mock.
            resume: Resume from last checkpoint.
            make, model: Optional filters.
            max_pages: Override config max_pages.

        Returns:
            List of validated, normalized CanonicalListing objects.
        """
        self._stats.start()

        if resume:
            state = self._checkpoint.load()
            if state:
                self._pagination.restore_state(state.get("pagination", {}))
                logger.info("checkpoint_resumed",
                           page=self._pagination.current_page)

        self._pagination.start()

        all_listings: list[CanonicalListing] = []
        max_p = max_pages or self.config.max_pages

        # Discovery phase
        search_url = self._discovery.search_url(make=make, model=model)

        # Pagination loop
        for page_num in range(1, max_p + 1):
            try:
                self._pagination.next_page()
            except Exception:
                break  # Pagination exhausted

            url = self._discovery.search_url(page=page_num, make=make, model=model)
            html = await fetch_page(url)
            self._stats.record_page()

            # Phase 1: Extract listing cards from search results
            from browser.dom.document import DOMDocument
            doc = DOMDocument.from_html(html, url=url)
            cards = self._listing_extractor.extract_cards(doc)
            self._stats.record_listings_found(len(cards))

            if not cards:
                self._pagination.mark_last_page()
                break

            # Phase 2: Extract details from each listing
            for card in cards:
                try:
                    listing = await self._process_listing(card, fetch_page)
                    if listing:
                        all_listings.append(listing)
                        self._stats.record_listing_processed()
                except Exception as e:
                    self._stats.record_failure()
                    logger.warning("listing_failed",
                                 url=card.get("url", "")[:120],
                                 error=str(e)[:200])

            # Checkpoint after each page
            self._checkpoint.save({
                "pagination": self._pagination.checkpoint_state(),
                "total_listings": len(all_listings),
                "last_page_url": url,
            })

        self._stats.finish()
        return all_listings

    async def _process_listing(self, card: dict, fetch_page) -> CanonicalListing | None:
        """Process a single listing card: fetch detail → map → normalize → validate."""
        url = card.get("url", "")
        if not url:
            return None

        # Ensure absolute URL
        if url.startswith("/"):
            url = f"{self.config.base_url}{url}"

        # Fetch detail page
        html = await fetch_page(url)

        # Check for challenges
        from browser.challenge.manager import ChallengeManager
        challenge_mgr = ChallengeManager()
        challenge = challenge_mgr.detect(html=html, url=url)
        if challenge:
            logger.info("challenge_detected", url=url[:120],
                       challenge_type=challenge.challenge_type.value)
            return None

        # Extract details
        from browser.dom.document import DOMDocument
        doc = DOMDocument.from_html(html, url=url)
        details = self._detail_extractor.extract(doc)
        details["url"] = url
        details["listing_id"] = self._extract_listing_id(url)

        # Merge card-level data
        for key in ("title", "price", "year", "mileage_km", "location", "image"):
            if not details.get(key) and card.get(key):
                details[key] = card.get(key)

        # Map to canonical schema
        listing = self._mapper.map_to_canonical(details, url=url,
                                                 listing_id=details.get("listing_id", ""))
        listing.scraped_at = datetime.now(timezone.utc).isoformat()

        # Normalize
        self._normalizer.normalize(listing)

        # Validate
        errors = self._validator.validate(listing)
        if errors and self.config.skip_incomplete:
            logger.debug("listing_validation_failed",
                        url=url[:120], errors=errors)
            return None

        return listing

    @staticmethod
    def _extract_listing_id(url: str) -> str:
        """Extract Dubizzle listing ID from URL."""
        import re
        match = re.search(r'/(\d{5,})(?:[/?]|$)', url)
        return match.group(1) if match else ""

    @property
    def stats(self) -> dict:
        return self._stats.snapshot()
