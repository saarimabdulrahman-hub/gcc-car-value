# GCC Car Value — Prometheus Integration

**Date:** 2026-07-12  
**Endpoint:** `GET /metrics`  
**Content-Type:** `text/plain; version=0.0.4; charset=utf-8`

---

## 1. Architecture

```
Prometheus (scrape every 15-60s)
    │
    ▼
GET /metrics → Routes → PrometheusExporter.export_sync()
                              │
                              ▼
                    MetricsRegistry.collect_all()
                              │
                              ▼
                    PrometheusFormatter → text/plain
```

The `/metrics` endpoint never accesses the registry directly. It delegates to the `PrometheusExporter`, which calls `registry.collect_all()` and passes the results to the `PrometheusFormatter` for serialization. This preserves the abstraction — the registry and application code remain exporter-agnostic.

## 2. Endpoint

```
GET /metrics
```

Returns all registered metrics in Prometheus exposition format. Uptime is recalculated before each scrape so Prometheus always gets the current value.

## 3. Prometheus Format

### Counter → `_total`

```
# HELP api_requests_total API request count
# TYPE api_requests_total counter
api_requests_total{source="api"} 150
```

### Gauge

```
# HELP db_pool_size DB pool size
# TYPE db_pool_size gauge
db_pool_size 8
```

### Histogram → `_bucket`, `_sum`, `_count`

```
# HELP api_latency_ms API latency
# TYPE api_latency_ms histogram
api_latency_ms_bucket{le="10"} 5
api_latency_ms_bucket{le="50"} 23
api_latency_ms_bucket{le="100"} 45
api_latency_ms_bucket{le="250"} 50
api_latency_ms_bucket{le="500"} 55
api_latency_ms_bucket{le="+Inf"} 60
api_latency_ms_sum 4520.5
api_latency_ms_count 60
```

### Info → `_info`

```
# HELP app_version_info Application version
# TYPE app_version_info gauge
app_version_info{version="0.1.0"} 1
```

## 4. Auto-Registered Application Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `app_version_info` | Info | API version (`version=0.1.0`) |
| `app_environment_info` | Info | Deployment environment (`environment=dev/staging/production`) |
| `app_runtime_info` | Info | Python version |
| `app_uptime_seconds` | Gauge | Process uptime (updated on each scrape) |

## 5. Naming Convention

Application namespaces (dots) become Prometheus metric prefixes (underscores):

| Registry Name | Prometheus Name |
|---------------|-----------------|
| `api.requests` | `api_requests_total` (counter) |
| `api.latency_ms` | `api_latency_ms` (histogram) |
| `db.pool.size` | `db_pool_size` (gauge) |
| `valuation.requests` | `valuation_requests_total` |
| `scraper.listings_ingested` | `scraper_listings_ingested_total` |
| `app.version` | `app_version_info` |

## 6. Label Convention

Tags on metrics become Prometheus labels. Labels are sorted alphabetically in output.

```python
# Registration with base tags
Metrics.counter("valuation.requests", "Valuation requests",
                tags={"source": "api", "version": "v1"})

# Output:
# valuation_requests_total{source="api",version="v1"} 42
```

Label values are always double-quoted. Special characters in values are preserved as-is.

## 7. Prometheus Scrape Configuration

```yaml
scrape_configs:
  - job_name: 'gcc-car-value'
    scrape_interval: 30s
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

## 8. Grafana Compatibility

All metric types are Grafana-compatible:

- Counters: use `rate()` for per-second rates
- Gauges: use directly, or `avg_over_time()` for trends
- Histograms: use `histogram_quantile()` for percentiles
- Info: use for dashboard variables (version, environment)

### Example PromQL Queries

```promql
# API request rate (per second, 5-minute window)
rate(api_requests_total[5m])

# API latency p95
histogram_quantile(0.95, rate(api_latency_ms_bucket[5m]))

# DB pool utilization
db_pool_size / db_pool_max_size

# Valuation request rate by confidence
sum by (confidence) (rate(valuation_requests_total[5m]))
```

## 9. Optimization

The Prometheus exporter is pull-based and synchronous — it formats all metrics on each scrape. Since `format_metrics()` is pure CPU work (no I/O), it completes in <1ms for typical registry sizes (under 1000 metrics).

No caching is implemented because Prometheus expects fresh values on each scrape. If the registry grows very large (>10K metrics), consider:
- Namespace filtering in scrape config
- Incremental formatting (only changed metrics since last scrape)
- Pre-computed metric strings with placeholder values

## 10. Adding a New Metric for Prometheus Export

```python
from src.core.metrics import Metrics

# 1. Register the metric (at module level or startup)
Metrics.counter("my.feature.requests", "My feature request count",
                namespace="my.feature",
                tags={"source": "my-service"})

# 2. Increment in application code
Metrics.increment("my.feature.requests")

# 3. It automatically appears in GET /metrics as:
# my_feature_requests_total{source="my-service"} 1
```

---

*Prometheus integration documented 2026-07-12.*
