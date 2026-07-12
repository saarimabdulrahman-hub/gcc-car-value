# GCC Car Value — Production Scraper Framework

**Date:** 2026-07-12  
**Package:** `scrapers/`

---

## 1. Architecture

```
Scheduler → Job Queue → ScraperFactory → BaseScraper → Marketplace Scraper
                                                              │
                                    ┌─────────────────────────┼─────────────────────────┐
                                    ▼                         ▼                         ▼
                              SessionManager             RateLimiter              RetryEngine
                              (UA rotation,              (token bucket,           (exponential
                               headers, cookies,          burst-aware,             backoff, jitter,
                               proxy, timeout)            async)                   circuit breaker)
                                    │                         │                         │
                                    └─────────────────────────┼─────────────────────────┘
                                                              ▼
                                                        EventBus → ScraperMetrics
                                                              │
                                                              ▼
                                                        Metrics Registry
```

## 2. Lifecycle

```
CREATED → READY → RUNNING → COMPLETED
                    │
                    ├── WAITING (rate limited)
                    ├── RETRYING → RUNNING
                    ├── FAILED
                    └── CANCELLED
```

| State | Meaning |
|-------|---------|
| `CREATED` | Job exists, not yet started |
| `READY` | Configured, waiting to execute |
| `RUNNING` | Actively fetching/parsing |
| `WAITING` | Paused by rate limiter |
| `RETRYING` | Failed, backing off before retry |
| `COMPLETED` | Successfully finished |
| `FAILED` | Permanently failed after max retries |
| `CANCELLED` | Manually cancelled |

## 3. Building a Marketplace Scraper

Only three methods required:

```python
from scrapers.base.base_scraper import BaseScraper
from scrapers.models import ScraperConfig

class DubizzleUAEScraper(BaseScraper):
    async def fetch_index(self, page: int) -> list[str]:
        """Return listing URLs from search results page."""
        ...

    async def fetch_listing(self, url: str) -> str:
        """Return raw HTML for a single listing."""
        ...

    def parse(self, html: str, url: str) -> dict:
        """Extract make, model, year, price, etc. from HTML."""
        return {"make": "Toyota", "model": "Camry", ...}
```

Everything else (lifecycle, retry, rate limiting, sessions, events, metrics) is inherited.

## 4. Registration

```python
from scrapers.registry import scraper_registry
scraper_registry.register("dubizzle_uae", DubizzleUAEScraper)
```

Then instantiate via the factory:

```python
from scrapers.factory import ScraperFactory
from scrapers.models import ScraperConfig

factory = ScraperFactory()
config = ScraperConfig(marketplace="dubizzle_uae", country="AE", rate_limit=2.0)
scraper = factory.create("dubizzle_uae", config)
result = await scraper.run()
```

## 5. Components

| Component | Responsibility |
|-----------|---------------|
| `BaseScraper` | Lifecycle, orchestration, event emission |
| `RetryEngine` | Exponential backoff with full jitter, max attempts |
| `RateLimiter` | Async token bucket, burst-aware |
| `SessionManager` | UA rotation, GCC-optimized headers, cookies, proxy |
| `EventBus` | Pub/sub for lifecycle events |
| `ScraperMetrics` | Auto-collects job duration, pages, errors, retries |
| `BaseListingParser` | Shared extraction helpers (year, mileage, price, spec) |

## 6. Concurrency

Framework supports `asyncio.gather` for concurrent scraper execution. 10 DummyScrapers tested concurrently — no race conditions, no deadlocks, no resource leaks.

---

*Scraper framework documented 2026-07-12.*
