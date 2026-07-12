# Structured Logging Framework

**Package:** `src.core.logging`

## Quick Start

```python
from src.core.logging import get_logger, configure_logging

# Startup (once, in main.py)
configure_logging()

# In any module
log = get_logger(__name__)

# Standard levels
log.info("event_name", key="value", count=42)
log.warning("degraded_service", reason="cache_miss")
log.error("db_connection_failed", db_host="localhost")

# Categories
log.audit("admin_action", user_id="abc", action="model_promoted")
log.security("auth_failed", ip="1.2.3.4", reason="invalid_token")
log.performance("api_latency", endpoint="/valuate", execution_time_ms=145.2)
```

## Output Format

### Development (console, colored)
```
2026-07-12T10:30:00Z [info] valuation_computed make=Toyota estimate=125000 module=src.api.routes.valuation
```

### Production (JSON)
```json
{
  "timestamp": "2026-07-12T10:30:00Z",
  "level": "info",
  "event": "valuation_computed",
  "service": "gcc-car-value",
  "environment": "production",
  "version": "0.1.0",
  "hostname": "api-7f3a",
  "pid": 42,
  "module": "src.api.routes.valuation",
  "make": "Toyota",
  "estimate": 125000
}
```

## Sensitive Data Masking

The logger automatically masks sensitive data:

```python
# These are automatically masked in output:
log.info("config", jwt_secret="abc123")       # → jwt_secret="***MASKED***"
log.info("auth", authorization="Bearer xyz")  # → authorization="***MASKED***"
log.info("db", database_url="postgresql://user:pass@host/db")
# → database_url="postgresql://user:***MASKED***@host/db"
```

## Context

```python
from src.core.logging.context import bind_context, clear_context

bind_context(request_id="abc123", user_id="user-1")
log.info("request_started")  # includes request_id, user_id
clear_context()
```

## Log Levels

| Level | Usage |
|-------|-------|
| `TRACE` | Extremely detailed (not exposed — use debug) |
| `DEBUG` | Development debugging |
| `INFO` | Normal operational events |
| `WARNING` | Degraded service, recoverable errors |
| `ERROR` | Operation failures, exceptions |
| `CRITICAL` | Application cannot continue |

Set via `LOG_LEVEL` env var (default: `INFO`, dev: `DEBUG`).
