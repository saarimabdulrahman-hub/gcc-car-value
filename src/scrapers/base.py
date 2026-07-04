import uuid
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
    pages_crawled: int = 0
    errors: list[dict] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BaseScraper(ABC):
    source: str
    base_url: str

    def __init__(self):
        self.rate_limiter = RateLimiter(settings.scraper_rate_limit_rps)
        self.raw_storage = RawStorage()
        self._session = None

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
                        result.records_ingested += 1
                        result.pages_crawled += 1
                    except Exception as e:
                        result.errors.append({"url": url, "error": str(e)})
                page += 1
        finally:
            result.completed_at = datetime.now(timezone.utc)
            if self._session:
                await self._session.aclose()
        return result

    async def close(self):
        if self._session:
            await self._session.aclose()
