# GCC Car Value — Metrics Architecture

**Date:** 2026-07-12  
**Package:** `src.core.metrics`  
**Global singleton:** `from src.core.metrics import Metrics`

---

## 1. Architecture

```
Application Code
    │
    ▼
Metrics (global singleton)
    │
    ├── Registry ─────── stores all Metric objects
    │       ├── Counter     monotonic count
    │       ├── Gauge       up/down value
    │       ├── Histogram   bucketed distribution
    │       ├── Timer       duration (context manager)
    │       └── Info        static metadata
    │
    ├── Collectors ───── gather values from internals
    │       ├── ProcessCollector    (future)
    │       ├── DatabaseCollector   (future)
    │       └── APICollector        (future)
    │
    └── Exporters ────── publish to external systems
            ├── PrometheusExporter  (P0018)
            ├── CloudWatchExporter  (future)
            ├── DatadogExporter     (future)
            └── OTelExporter        (future)
```

## 2. Registry (`MetricsRegistry`)

Thread-safe singleton. All metric registration, lookup, and mutation flows through the registry.

```python
from src.core.metrics import Metrics

# Registration
Metrics.counter("valuation.requests", "Valuation request count")
Metrics.gauge("db.pool.size", "DB connection pool size")
Metrics.histogram("api.latency_ms", "API request latency",
                  buckets=[10, 50, 100, 250, 500, 1000])

# Mutation (looks up metric, then calls the right method)
Metrics.increment("valuation.requests", tags={"confidence": "high"})
Metrics.set_gauge("db.pool.size", 10.0)
Metrics.observe("api.latency_ms", 145.0)

# Timer context manager
with Metrics.timer("valuation.duration_ms"):
    result = await valuate(...)

# Collection (for exporters)
for metric in Metrics.collect_all():
    for value in metric.collect():
        print(metric.full_name, value.value, value.tags)
```

**Key properties:**
- Duplicate registration raises `DuplicateMetricError`
- Missing metric access raises `MetricNotFoundError`
- `get_or_register()` is safe for concurrent use
- `list_names(namespace="api")` filters by namespace prefix

## 3. Metric Types

### Counter
Monotonically increasing. Never decreases. Used for request counts, error counts, ingested records.

```python
c = Counter("scraper.listings_ingested", "Listings ingested by scrapers",
            namespace="scraper")
c.inc()
c.inc(50, tags={"source": "dubizzle"})
total = c.value()
```

### Gauge
Point-in-time value. Goes up and down. Used for pool sizes, queue depths, temperatures.

```python
g = Gauge("db.pool.active", "Active DB connections", namespace="database")
g.set(8.0)
g.inc(1.0)
g.dec(2.0)
```

### Histogram
Distribution across configurable buckets. Used for latencies, payload sizes, price distributions.

```python
h = Histogram("api.latency_ms", "API request latency",
              buckets=[10, 50, 100, 250, 500, 1000],
              namespace="api")
h.observe(145.0, tags={"endpoint": "/valuate"})
count = h.count()      # total observations
total = h.sum()        # sum of all values
```

### Timer
Context manager wrapping a Histogram. Records elapsed milliseconds.

```python
with Metrics.timer("valuation.duration_ms"):
    result = await compute_valuation(...)

# Manual start/stop
t = Metrics.start_timer("valuation.duration_ms")
result = await compute_valuation(...)
elapsed = t.stop()  # returns ms
```

### Info
Static string metadata. Version, environment name, build info.

```python
info = Info("app.version", namespace="app")
info.set_info(version="0.1.0", commit="abc123", python="3.12")
```

## 4. Namespaces

All metrics use dot-separated namespaces:

| Namespace | Purpose | Example |
|-----------|---------|---------|
| `api.*` | HTTP requests, latency, status codes | `api.requests`, `api.latency_ms` |
| `database.*` | Connection pool, query latency | `database.pool.size`, `database.query_ms` |
| `scraper.*` | Scraper runs, listings, errors | `scraper.runs`, `scraper.listings_ingested` |
| `ml.*` | Model predictions, training | `ml.predictions`, `ml.mae` |
| `valuation.*` | Valuation requests, comp counts | `valuation.requests`, `valuation.comps` |
| `cache.*` | Cache hits, misses | `cache.hits`, `cache.misses` |
| `system.*` | CPU, memory, uptime | `system.uptime_seconds` |
| `security.*` | Auth failures, rate limits | `security.denied_requests` |
| `app.*` | Static metadata | `app.version`, `app.environment` |

## 5. Exporters (`MetricExporter`)

Exporters pull metrics from the registry and publish to external systems. The registry is exporter-agnostic.

```python
from src.core.metrics.exporters.base import MetricExporter

class MyExporter(MetricExporter):
    def format_name(self) -> str:
        return "my-exporter"

    async def export(self) -> None:
        for metric in self.registry.collect_all():
            for value in metric.collect():
                # Publish to external system
                publish(metric.full_name, value.value, value.tags)
```

## 6. Collectors (`MetricCollector`)

Collectors gather metric values from application internals. They bridge instrumentation points and exported metrics.

```python
from src.core.metrics.collectors.base import MetricCollector

class DatabaseCollector(MetricCollector):
    def name(self) -> str:
        return "database"

    async def collect(self) -> None:
        pool = get_pool_stats()
        self.registry.set_gauge("database.pool.size", pool.size)
        self.registry.set_gauge("database.pool.active", pool.active)
```

## 7. Thread Safety

- Registry uses `threading.RLock` for registration and lookup
- Counters, Gauges, Histograms use individual `threading.Lock` for value mutation
- `get_or_register()` is safe for concurrent use (double-checked under lock)
- Concurrent counter increments from 4 threads × 1000 iterations = 4000 total (verified in test)

## 8. Lifecycle Integration

```python
# In main.py startup
from src.core.metrics import Metrics

Metrics.info("app.version").set_info(version="0.1.0")
Metrics.info("app.environment").set_info(env=settings.environment)
Metrics.counter("app.startups")
Metrics.increment("app.startups")

# Metrics are available immediately — no async initialization required
# Exporters handle async when they call export()
```

## 9. Future Extensions

### Prometheus Exporter (P0018)
Register a `/metrics` endpoint serving Prometheus text format. The exporter iterates `Metrics.collect_all()` and formats each metric type into the Prometheus exposition format.

### Process Collector
Gather CPU, memory, thread count, and GC stats from the Python runtime.

### Database Collector  
Monitor SQLAlchemy connection pool: size, checked out, overflow.

### API Middleware
FastAPI middleware that auto-records request counts, latency histograms, and status code breakdowns for all endpoints.

### Distributed Tracing
Integration with OpenTelemetry for span/metric correlation via trace IDs.

---

*Metrics architecture documented 2026-07-12.*
