import time
import pytest
from src.scrapers.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_enforces_rate():
    limiter = RateLimiter(requests_per_second=5.0)
    start = time.monotonic()
    for _ in range(10):
        await limiter.acquire()
    elapsed = time.monotonic() - start
    assert 0.8 <= elapsed <= 2.0


@pytest.mark.asyncio
async def test_rate_limiter_first_token_immediate():
    limiter = RateLimiter(requests_per_second=10.0)
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed < 0.1


def test_scraper_result_dataclass():
    from src.scrapers.base import ScraperResult
    result = ScraperResult(source="test")
    assert result.source == "test"
    assert result.run_id is not None
    assert result.records_ingested == 0


def test_base_scraper_abstract():
    from src.scrapers.base import BaseScraper
    with pytest.raises(TypeError):
        BaseScraper()  # cannot instantiate abstract class
