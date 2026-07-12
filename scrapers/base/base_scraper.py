"""BaseScraper — inheritable scraper with full lifecycle, retry, rate limiting, events, metrics.

Marketplace scrapers only implement:
    - fetch_index(page)   → list of listing URLs
    - fetch_listing(url)  → raw HTML for a listing page
    - parse(html, url)    → dict of extracted fields

Everything else (lifecycle, retry, rate limiting, sessions, events, metrics)
is inherited from this class.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any

import structlog

from scrapers.constants import JobState, TERMINAL_STATES
from scrapers.models import ScraperConfig, ScraperJob, ScraperResult, ScraperEvent
from scrapers.errors import ScraperError
from scrapers.base.base_retry import RetryEngine
from scrapers.base.base_rate_limiter import RateLimiter
from scrapers.base.base_session import SessionManager
from scrapers.base.base_events import EventBus
from scrapers.base.base_metrics import ScraperMetrics

logger = structlog.get_logger()


class BaseScraper(ABC):
    """Production scraper base class.

    Subclasses override marketplace-specific methods:
        fetch_index(), fetch_listing(), parse()

    The base class handles:
        - Lifecycle management (states, transitions)
        - Retry with exponential backoff
        - Rate limiting (token bucket)
        - Session management (UA rotation, headers)
        - Event emission (job.started, page.downloaded, etc.)
        - Metrics collection
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self._state = JobState.CREATED
        self._event_bus = EventBus()
        self._metrics = ScraperMetrics(self._event_bus)
        self._retry = RetryEngine(
            max_attempts=config.max_retries,
            base_seconds=config.backoff_base,
            max_seconds=config.backoff_max,
        )
        self._rate_limiter = RateLimiter(config.rate_limit)
        self._session_mgr = SessionManager(
            user_agent=config.user_agent,
            timeout=config.timeout,
            headers=config.headers,
            cookies=config.cookies,
            proxy=config.proxy,
        )
        self._job: ScraperJob | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, job: ScraperJob | None = None) -> ScraperResult:
        """Execute the full scraping lifecycle.

        Args:
            job: Optional ScraperJob. If None, creates a new job.

        Returns:
            ScraperResult with pages_crawled, listings_found, etc.
        """
        self._job = job or ScraperJob(
            marketplace=self.config.marketplace,
            config=self.config,
        )
        self._transition(JobState.RUNNING)
        self._job.started_at = time.time()
        await self._emit("job.started", job_id=self._job.job_id)

        result = ScraperResult()

        try:
            page = 1
            while True:
                urls = await self._fetch_index_with_retry(page)
                if not urls:
                    break

                for url in urls:
                    if self._job.state in TERMINAL_STATES:
                        break

                    parsed = await self._fetch_and_parse(url)
                    if parsed:
                        result.listings_found += 1
                    result.pages_crawled += 1
                    await self._emit("page.downloaded",
                                    url=url[:120],
                                    success=parsed is not None)

                page += 1

            self._transition(JobState.COMPLETED)
            self._job.completed_at = time.time()
            result.duration_ms = (self._job.completed_at - self._job.started_at) * 1000
            await self._emit("job.completed", result=result)

        except Exception as e:
            self._transition(JobState.FAILED)
            self._job.error = str(e)[:500]
            result.errors.append({"error": str(e)[:200]})
            await self._emit("job.failed", error=str(e)[:200])

        finally:
            await self._session_mgr.close()

        self._job.result = result
        return result

    async def cancel(self) -> None:
        """Cancel a running job."""
        if self._job:
            self._transition(JobState.CANCELLED)
            await self._emit("job.cancelled")

    @property
    def state(self) -> JobState:
        return self._state

    @property
    def events(self) -> EventBus:
        return self._event_bus

    # ------------------------------------------------------------------
    # Marketplace-specific methods (subclasses MUST implement)
    # ------------------------------------------------------------------

    @abstractmethod
    async def fetch_index(self, page: int) -> list[str]:
        """Fetch a page of the search index. Returns listing URLs."""
        ...

    @abstractmethod
    async def fetch_listing(self, url: str) -> str:
        """Fetch a single listing page. Returns raw HTML."""
        ...

    @abstractmethod
    def parse(self, html: str, url: str) -> dict[str, Any]:
        """Parse raw HTML into structured listing fields."""
        ...

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _fetch_index_with_retry(self, page: int) -> list[str]:
        """Fetch index page with retry logic."""
        async def _fetch():
            await self._rate_limiter.acquire()
            return await self.fetch_index(page)

        success, result, errors = await self._retry.execute(
            _fetch,
            is_retryable=lambda e: isinstance(e, ScraperError) and e.retryable,
            on_retry=self._on_retry,
        )
        if success:
            return result or []
        return []

    async def _fetch_and_parse(self, url: str) -> dict | None:
        """Fetch a listing page and parse it."""
        async def _fetch():
            await self._rate_limiter.acquire()
            return await self.fetch_listing(url)

        success, html, _ = await self._retry.execute(_fetch)
        if not success or html is None:
            return None

        try:
            return self.parse(html, url)
        except Exception:
            return None

    async def _on_retry(self, attempt: int, error: Exception) -> None:
        """Called before each retry attempt."""
        self._transition(JobState.RETRYING)
        if self._job:
            self._job.retry_count += 1
        await self._emit("job.retrying",
                        attempt=attempt,
                        error=str(error)[:200])

    def _transition(self, new_state: JobState) -> None:
        self._state = new_state
        if self._job:
            self._job.state = new_state

    async def _emit(self, event_type: str, **data: Any) -> None:
        if self._job:
            await self._event_bus.emit(ScraperEvent(
                event_type=event_type,
                job_id=self._job.job_id,
                marketplace=self.config.marketplace,
                data=data,
            ))
