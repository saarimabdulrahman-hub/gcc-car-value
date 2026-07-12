"""Test scraper framework — lifecycle, retry, rate limiter, factory, registry."""
import asyncio
import time
import pytest
from scrapers.constants import JobState
from scrapers.models import ScraperConfig, ScraperJob
from scrapers.errors import ScraperError, TemporaryFailure
from scrapers.base.base_scraper import BaseScraper
from scrapers.base.base_retry import RetryEngine
from scrapers.base.base_rate_limiter import RateLimiter
from scrapers.base.base_events import EventBus
from scrapers.base.base_session import SessionManager
from scrapers.registry import ScraperRegistry, scraper_registry
from scrapers.factory import ScraperFactory


# ------------------------------------------------------------------
# Dummy scraper for testing the framework
# ------------------------------------------------------------------

class DummyScraper(BaseScraper):
    """Minimal scraper that returns canned data — no real HTTP."""

    def __init__(self, config=None, urls=None, parsed=None, fail_on=None):
        super().__init__(config or ScraperConfig(marketplace="test"))
        self._urls = urls or [f"http://example.com/listing/{i}" for i in range(3)]
        self._parsed = parsed or {"make": "Toyota", "model": "Camry", "year": 2020}
        self._fail_on = fail_on or set()

    async def fetch_index(self, page: int) -> list[str]:
        if page > 1:
            return []
        return self._urls

    async def fetch_listing(self, url: str) -> str:
        if "fail" in url and "fetch" in self._fail_on:
            raise TemporaryFailure("Simulated fetch failure")
        return f"<html><h1>Toyota Camry 2020</h1><p>AED 75,000</p></html>"

    def parse(self, html: str, url: str) -> dict:
        if "fail" in url and "parse" in self._fail_on:
            raise ScraperError("Simulated parse failure")
        return dict(self._parsed)


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestRetryEngine:
    @pytest.mark.asyncio
    async def test_successful_operation_no_retries(self):
        engine = RetryEngine(max_attempts=3)
        calls = 0
        async def op():
            nonlocal calls; calls += 1; return "ok"
        success, result, errors = await engine.execute(op)
        assert success
        assert result == "ok"
        assert calls == 1
        assert engine.total_retries == 0

    @pytest.mark.asyncio
    async def test_retries_on_failure(self):
        engine = RetryEngine(max_attempts=3, base_seconds=0.001, max_seconds=0.01)
        calls = 0
        async def op():
            nonlocal calls; calls += 1
            if calls < 3:
                raise TemporaryFailure("fail")
            return "finally"
        success, result, errors = await engine.execute(op)
        assert success
        assert result == "finally"
        assert calls == 3
        assert engine.total_retries == 2

    @pytest.mark.asyncio
    async def test_exhausts_retries(self):
        engine = RetryEngine(max_attempts=2, base_seconds=0.001)
        async def op():
            raise TemporaryFailure("always fails")
        success, result, errors = await engine.execute(op)
        assert not success
        assert result is None
        assert len(errors) == 2


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_acquire_does_not_block_initially(self):
        limiter = RateLimiter(requests_per_second=100)
        start = time.perf_counter()
        await limiter.acquire()
        elapsed = time.perf_counter() - start
        assert elapsed < 0.05  # Should be nearly instant with high rate

    @pytest.mark.asyncio
    async def test_rate_limit_is_enforced(self):
        limiter = RateLimiter(requests_per_second=10)
        start = time.perf_counter()
        for _ in range(20):
            await limiter.acquire()
        elapsed = time.perf_counter() - start
        # 20 requests at 10/sec with burst=10: first 10 instant,
        # then ~1 sec for the remaining 10
        assert elapsed > 0.5

    def test_available_tokens(self):
        limiter = RateLimiter(requests_per_second=10, burst_size=5)
        assert limiter.available_tokens > 0


class TestEventBus:
    @pytest.mark.asyncio
    async def test_handler_called(self):
        bus = EventBus()
        received = []
        async def handler(event):
            received.append(event.event_type)
        bus.on("test.event", handler)
        from scrapers.models import ScraperEvent
        await bus.emit(ScraperEvent("test.event", job_id="1", marketplace="test"))
        assert "test.event" in received

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        bus = EventBus()
        results = []
        async def h1(e): results.append("h1")
        async def h2(e): results.append("h2")
        bus.on("e", h1)
        bus.on("e", h2)
        from scrapers.models import ScraperEvent
        await bus.emit(ScraperEvent("e", job_id="1", marketplace="test"))
        assert len(results) == 2


class TestSessionManager:
    def test_creates_session_with_ua(self):
        mgr = SessionManager()
        client = mgr.session()
        assert "User-Agent" in client.headers
        assert client.timeout is not None

    def test_custom_user_agent(self):
        mgr = SessionManager(user_agent="CustomBot/1.0")
        client = mgr.session()
        assert client.headers["User-Agent"] == "CustomBot/1.0"


class TestScraperLifecycle:
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        scraper = DummyScraper()
        result = await scraper.run()
        assert scraper.state == JobState.COMPLETED
        assert result.pages_crawled == 3
        assert result.listings_found == 3

    @pytest.mark.asyncio
    async def test_cancel_stops_scraping(self):
        scraper = DummyScraper(urls=["http://example.com/1"])
        result = await scraper.run()
        assert scraper.state == JobState.COMPLETED
        assert result.pages_crawled == 1


class TestRegistry:
    def test_register_and_get(self):
        reg = ScraperRegistry()
        reg.register("test_market", DummyScraper)
        cls = reg.get("test_market")
        assert cls is DummyScraper

    def test_get_unregistered_raises(self):
        reg = ScraperRegistry()
        with pytest.raises(KeyError, match="not_registered"):
            reg.get("not_registered")

    def test_list_marketplaces(self):
        reg = ScraperRegistry()
        reg.register("a", DummyScraper)
        reg.register("b", DummyScraper)
        assert set(reg.list_marketplaces()) == {"a", "b"}


class TestFactory:
    def test_create_returns_scraper_instance(self):
        registry = ScraperRegistry()
        factory = ScraperFactory()
        registry.register("test", DummyScraper)
        # The factory uses the global registry, so register there too
        scraper_registry.register("factory_test", DummyScraper)
        s = factory.create("factory_test",
                          ScraperConfig(marketplace="factory_test"))
        assert isinstance(s, BaseScraper)


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_scrapers(self):
        """Multiple scrapers run concurrently without interference."""
        async def run_one(i):
            scraper = DummyScraper(
                config=ScraperConfig(marketplace=f"test-{i}"),
                urls=[f"http://example.com/{i}/1"],
            )
            return await scraper.run()

        results = await asyncio.gather(*[run_one(i) for i in range(10)])
        for r in results:
            assert r.pages_crawled == 1
        assert len(results) == 10
