# Metrics Framework

**Package:** `src.core.metrics`  
**Global singleton:** `from src.core.metrics import Metrics`

## Quick Start

```python
from src.core.metrics import Metrics

# 1. Register metrics (at module level or startup)
Metrics.counter("valuation.requests", "Total valuation requests")
Metrics.gauge("db.pool.size", "Connection pool size")
Metrics.histogram("api.latency_ms", "API request latency",
                  buckets=[10, 50, 100, 250, 500, 1000])

# 2. Use metrics in application code
Metrics.increment("valuation.requests", tags={"confidence": "high"})
Metrics.set_gauge("db.pool.size", 10.0)
Metrics.observe("api.latency_ms", 145.0)

# 3. Timer context manager
with Metrics.timer("valuation.duration_ms"):
    result = await compute_valuation(...)
```

## Metric Types

| Type | Purpose | Key Methods |
|------|---------|-------------|
| `Counter` | Monotonically increasing count | `inc(amount)`, `value()` |
| `Gauge` | Point-in-time value (up/down) | `set(v)`, `inc(amount)`, `dec(amount)`, `value()` |
| `Histogram` | Distribution with buckets | `observe(value)`, `count()`, `sum()` |
| `Timer` | Context manager for duration | `with Metrics.timer(...)` |
| `Info` | Static string metadata | `set_info(**kwargs)` |

## Namespaces

All metrics use dot-separated namespaces for organization:

```
api.*         — HTTP requests, latency, status codes
database.*    — Connection pool, query latency
scraper.*     — Runs, listings ingested, errors
ml.*          — Model predictions, training, drift
valuation.*   — Valuation requests, comp counts, confidence
cache.*       — Cache hits, misses, TTL
system.*      — CPU, memory, uptime, threads
security.*    — Auth failures, rate limit hits, denied requests
```

## Thread Safety

The registry uses `threading.RLock` for all registration and mutation.
Counters, Gauges, and Histograms use internal locks for value access.
The `get_or_register()` pattern is safe for concurrent metric registration.

## Adding a New Exporter

```python
from src.core.metrics.exporters.base import MetricExporter

class MyExporter(MetricExporter):
    def format_name(self) -> str:
        return "my-exporter"

    async def export(self) -> None:
        for metric in self.registry.collect_all():
            for value in metric.collect():
                print(metric.full_name, value.value, value.tags)
```

## Adding a New Collector

```python
from src.core.metrics.collectors.base import MetricCollector

class MyCollector(MetricCollector):
    def name(self) -> str:
        return "my-collector"

    async def collect(self) -> None:
        # Gather data from application internals
        self.registry.set_gauge("system.cpu_pct", get_cpu_usage())
```
