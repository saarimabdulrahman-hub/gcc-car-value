"""Scraper metrics — auto-collects job duration, pages, errors, retries."""

from scrapers.models import ScraperEvent, ScraperResult
from scrapers.base.base_events import EventHandler


class ScraperMetrics:
    """Collects and publishes scraper metrics via the global Metrics registry.

    Automatically subscribes to lifecycle events. No manual metric calls
    needed in scraper implementations.
    """

    def __init__(self, event_bus: "EventBus"):  # noqa: F821
        self._event_bus = event_bus
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        self._event_bus.on("job.started", self._on_job_started)
        self._event_bus.on("job.completed", self._on_job_completed)
        self._event_bus.on("job.failed", self._on_job_failed)
        self._event_bus.on("job.retrying", self._on_job_retrying)
        self._event_bus.on("page.downloaded", self._on_page_downloaded)
        self._event_bus.on("rate.limited", self._on_rate_limited)

    # --- Handlers ---

    async def _on_job_started(self, event: ScraperEvent) -> None:
        self._inc("scraper.jobs.started", event.marketplace)

    async def _on_job_completed(self, event: ScraperEvent) -> None:
        self._inc("scraper.jobs.completed", event.marketplace)
        result = event.data.get("result")
        if isinstance(result, ScraperResult):
            self._inc("scraper.pages.crawled", event.marketplace,
                      amount=result.pages_crawled)
            self._inc("scraper.listings.found", event.marketplace,
                      amount=result.listings_found)
            if result.errors:
                self._inc("scraper.errors", event.marketplace,
                          amount=len(result.errors))

    async def _on_job_failed(self, event: ScraperEvent) -> None:
        self._inc("scraper.jobs.failed", event.marketplace)

    async def _on_job_retrying(self, event: ScraperEvent) -> None:
        self._inc("scraper.retries", event.marketplace)

    async def _on_page_downloaded(self, event: ScraperEvent) -> None:
        self._inc("scraper.pages.downloaded", event.marketplace)

    async def _on_rate_limited(self, event: ScraperEvent) -> None:
        self._inc("scraper.rate_limits", event.marketplace)

    # --- Internal ---

    @staticmethod
    def _inc(name: str, marketplace: str, amount: float = 1.0) -> None:
        try:
            from src.core.metrics import Metrics
            Metrics.increment(name, amount,
                            tags={"marketplace": marketplace})
        except Exception:
            pass
