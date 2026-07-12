# GCC Car Value — Browser Pool Manager

**Date:** 2026-07-12  
**Package:** `browser/pool/`

## Architecture

```
Scraper Job
    │
    ▼
BrowserPool.acquire()  →  BrowserContext (leased)
    │                          │
    ├── find idle slot         ├── ctx.new_page()
    ├── scale up if needed     ├── page.goto(url)
    ├── health check           └── page.content()
    │
    ▼
BrowserPool.release(ctx) →  context closed, slot freed
    │
    ├── recycle if over lifetime/crash limit
    └── scale down if idle > warm_pool_size
```

## Usage

```python
from browser.pool import BrowserPool, PoolConfig

def make_browser():
    return factory.create("dummy")

pool = BrowserPool(make_browser, PoolConfig(
    min_browsers=1, max_browsers=5,
    max_contexts_per_browser=20,
))
await pool.start()

ctx = await pool.acquire()          # Lease a context
try:
    page = await ctx.new_page()
    await page.goto("https://...")
    html = await page.content()
finally:
    await pool.release(ctx)          # Return to pool

await pool.shutdown()
```

## Configuration

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `min_browsers` | 1 | Minimum warm pool |
| `max_browsers` | 5 | Hard cap |
| `max_contexts_per_browser` | 20 | Contexts before recycling |
| `max_idle_seconds` | 300 | Idle before recycling |
| `max_lifetime_seconds` | 3600 | Max browser lifetime |
| `lease_timeout` | 30 | Max wait for acquire |
| `crash_limit` | 3 | Crashes before removal |

## Verified

- 100 concurrent leases — no deadlocks, no double-leasing, no context leakage
- Auto-scaling: pool grows under load, shrinks when idle
- Health monitoring: unhealthy browsers are recycled
- Recycling: browsers recycled after crash limit or max lifetime

---

*Browser pool documented 2026-07-12.*
