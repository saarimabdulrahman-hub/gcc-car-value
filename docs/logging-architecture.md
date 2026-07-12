# GCC Car Value — Structured Logging Architecture

**Date:** 2026-07-12  
**Package:** `src.core.logging`  
**Underlying Library:** structlog (stdlib logging)

---

## 1. Architecture

```
Application Code
    │
    ▼
get_logger(__name__) → Logger
    │
    ├── info(), warning(), error()       Standard levels
    ├── audit()                          Security-relevant events
    ├── security()                       Auth failures, rate limits
    └── performance()                    Timing measurements
    │
    ▼
Sensitive Data Masking (filters.py)
    │
    ▼
structlog Processors
    ├── merge_contextvars
    ├── filter_by_level
    ├── add_logger_name
    ├── add_log_level
    ├── TimeStamper (ISO 8601)
    ├── StackInfoRenderer
    ├── format_exc_info
    ├── add_standard_fields (service, env, version, hostname, pid)
    └── Renderer
        ├── ConsoleRenderer (dev, colored)
        └── JSONRenderer (prod, JSON lines)
    │
    ▼
stdout / stderr → Log Aggregator (CloudWatch, Loki, ELK, etc.)
```

## 2. Logger API

```python
from src.core.logging import get_logger

log = get_logger(__name__)
```

### Standard Levels

| Method | Level | Usage |
|--------|-------|-------|
| `log.trace("event", ...)` | DEBUG | Development tracing |
| `log.debug("event", ...)` | DEBUG | Debugging details |
| `log.info("event", ...)` | INFO | Normal operations |
| `log.warning("event", ...)` | WARNING | Degraded, recoverable |
| `log.error("event", ...)` | ERROR | Operation failures |
| `log.critical("event", ...)` | CRITICAL | Fatal, can't continue |
| `log.exception("event", ...)` | ERROR | Exception with traceback |

### Categories

| Method | Level | Use Case |
|--------|-------|----------|
| `log.audit("event", ...)` | INFO | Admin actions, data changes, model deployments |
| `log.security("event", ...)` | WARNING | Auth failures, permission denials, rate limits |
| `log.performance("event", ...)` | INFO | Query times, API latency, scraper duration |

Categories inject a `category` field into the log entry for filtering in log aggregators.

## 3. Standard Fields

Every log entry includes:

| Field | Source | Example |
|-------|--------|---------|
| `timestamp` | structlog | `2026-07-12T10:30:00.123Z` |
| `level` | structlog | `info`, `warning`, `error` |
| `event` | Caller | `valuation_computed` |
| `service` | config | `gcc-car-value` |
| `environment` | config | `production` |
| `version` | config | `0.1.0` |
| `hostname` | `os.uname().nodename` | `api-7f3a` |
| `pid` | `os.getpid()` | `42` |
| `module` | `__name__` | `src.api.routes.valuation` |
| `logger` | structlog | `src.api.routes.valuation` |
| `category` | Logger method | `audit`, `security`, `performance` |

## 4. Sensitive Data Masking

Applied automatically to every log call. No application code changes needed.

| Pattern | Example | Result |
|---------|---------|--------|
| Field name contains `password` | `db_password=...` | `***MASKED***` |
| Field name contains `secret` | `jwt_secret=...` | `***MASKED***` |
| Field name contains `token` | `refresh_token=...` | `***MASKED***` |
| Value starts with `eyJ` | JWT token | `***MASKED***` |
| Value starts with `sk-` | API key | `***MASKED***` |
| Value starts with `gccv_` | Our API key | `***MASKED***` |
| Database URL | `postgresql://u:p@h/db` | `postgresql://u:***MASKED***@h/db` |

## 5. Context Binding

Request-scoped fields that appear in every log message within a request lifecycle.

```python
from src.core.logging.context import bind_context, clear_context

# At request start (P0021 middleware)
bind_context(request_id="abc-123", user_id="user-1", client_ip="1.2.3.4")

# All subsequent log calls include these fields
log.info("valuation_started")  # includes request_id, user_id, client_ip

# At request end
clear_context()
```

Context uses `structlog.contextvars` which is safe for async — each task has its own context.

## 6. Environment Behavior

| Setting | Dev | Prod |
|---------|-----|------|
| Output format | Colored console | JSON lines |
| Log level (default) | DEBUG | INFO |
| Timestamp | ISO 8601 | ISO 8601 |
| Stack traces | Inline | Inline |

No code changes required — `configure_logging()` reads `ENVIRONMENT` from settings.

## 7. Thread Safety

- structlog uses `contextvars` for context — safe for async/await
- Logger instances are stateless (no mutable state except context)
- `get_logger()` returns a cached singleton per module name
- Background workers and scheduled jobs use the same Logger API

## 8. Migration from Existing Code

The existing `structlog.get_logger()` pattern still works, but new code should use:

```python
# Old (still works)
import structlog
logger = structlog.get_logger()

# New (preferred)
from src.core.logging import get_logger
log = get_logger(__name__)
```

## 9. Future Integrations

| Prompt | Integration |
|--------|-------------|
| P0021 | Correlation ID middleware — auto-bind request_id |
| P0022 | OpenTelemetry — trace_id/span_id in context |
| Future | Sentry — exception forwarding |
| Future | CloudWatch — log group/stream routing |
| Future | Loki — structured log shipping |

---

*Logging architecture documented 2026-07-12.*
