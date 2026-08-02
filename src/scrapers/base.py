import uuid
import structlog
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from src.scrapers.rate_limiter import RateLimiter
from src.scrapers.session import create_scraper_session
from src.scrapers.raw_storage import RawStorage
from src.config import get_settings

settings = get_settings()


@dataclass
class ScraperResult:
    source: str
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    records_ingested: int = 0
    records_new: int = 0
    records_updated: int = 0
    records_rejected: int = 0
    pages_crawled: int = 0
    errors: list[dict] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BaseScraper(ABC):
    source: str
    base_url: str

    def __init__(self, session_factory=None):
        self.rate_limiter = RateLimiter(settings.scraper_rate_limit_rps)
        self.raw_storage = RawStorage()
        self._session = None
        self._session_factory = session_factory

    async def get_session(self):
        if self._session is None:
            self._session = create_scraper_session()
        return self._session

    @abstractmethod
    async def fetch_index(self, page: int) -> list[str]:
        ...

    @abstractmethod
    async def fetch_listing(self, url: str) -> str:
        ...

    @abstractmethod
    def parse(self, html: str, url: str) -> dict:
        ...

    async def run(self) -> ScraperResult:
        result = ScraperResult(source=self.source)
        result.started_at = datetime.now(timezone.utc)
        _consecutive_failures = 0
        _MAX_CONSECUTIVE_FAILURES = 10
        try:
            page = 1
            while True:
                urls = await self.fetch_index(page)
                if not urls:
                    break
                for url in urls:
                    try:
                        await self.rate_limiter.acquire()
                        html = await self.fetch_listing(url)
                        s3_key = f"raw/{self.source}/{result.run_id}/{uuid.uuid4()}.html"
                        self.raw_storage.upload_text(s3_key, html)
                        parsed = self.parse(html, url)
                        parsed["raw_data_s3_key"] = s3_key
                        parsed["source"] = self.source
                        parsed["pipeline_run_id"] = result.run_id

                        saved = await self._persist(parsed)
                        if saved == "new":
                            result.records_new += 1
                            result.records_ingested += 1
                        elif saved == "updated":
                            result.records_updated += 1
                            result.records_ingested += 1
                        else:
                            result.records_rejected += 1

                        result.pages_crawled += 1
                        _consecutive_failures = 0
                    except Exception as e:
                        _consecutive_failures += 1
                        structlog.get_logger().error(
                            "listing_fetch_failed", source=self.source, url=url,
                            error=str(e)[:200],
                            consecutive_failures=_consecutive_failures)
                        result.errors.append({"url": url, "error": str(e)})
                        if _consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                            structlog.get_logger().critical(
                                "scraper_circuit_breaker_open",
                                source=self.source,
                                consecutive_failures=_consecutive_failures)
                            break
                if _consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                    break
                page += 1
        finally:
            result.completed_at = datetime.now(timezone.utc)
            if self._session:
                await self._session.aclose()
        return result

    async def close(self):
        if self._session:
            await self._session.aclose()

    async def _persist(self, parsed: dict) -> str:
        """Run parsed data through validate -> normalize -> score -> promote.

        Returns "new", "updated", or "rejected".
        """
        if self._session_factory is None:
            return "rejected"

        from src.pipeline.validator import validate_listing
        from src.pipeline.normalizer import normalize_listing
        from src.pipeline.quality import score_quality
        from src.pipeline.promoter import promote_listing

        validation = validate_listing(parsed)
        if not validation.is_valid:
            structlog.get_logger().info(
                "listing_rejected_validation", source=self.source,
                errors=validation.errors[:3])
            return "rejected"

        data = normalize_listing(validation.data)
        score, flags = score_quality(data)

        async with self._session_factory() as session:
            listing = await promote_listing(data, score, flags, session)
            is_new = listing is not None and listing.first_seen_at == listing.last_seen_at
            await session.commit()

        if listing is None:
            return "rejected"
        return "new" if is_new else "updated"
