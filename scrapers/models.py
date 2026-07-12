"""Scraper data models — job configuration, results, events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from scrapers.constants import JobState
import uuid


@dataclass
class ScraperConfig:
    """Configuration for a scraper instance."""
    marketplace: str
    country: str = "AE"
    timeout: float = 30.0
    max_retries: int = 3
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    rate_limit: float = 2.0
    user_agent: str = ""
    proxy: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    locale: str = "en"
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScraperJob:
    """A single scraping job — created by the scheduler, executed by a worker."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    marketplace: str = ""
    state: JobState = JobState.CREATED
    config: ScraperConfig | None = None
    created_at: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    started_at: float | None = None
    completed_at: float | None = None
    retry_count: int = 0
    error: str | None = None
    result: "ScraperResult | None" = None


@dataclass
class ScraperResult:
    """Result of a completed scraping job."""
    pages_crawled: int = 0
    listings_found: int = 0
    listings_new: int = 0
    listings_updated: int = 0
    errors: list[dict[str, str]] = field(default_factory=list)
    raw_storage_keys: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


@dataclass
class ScraperEvent:
    """An event emitted during scraping — for metrics and observability."""
    event_type: str
    job_id: str
    marketplace: str
    timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    data: dict[str, Any] = field(default_factory=dict)
