# GCC Car Value — Request Context & Correlation Middleware

**Date:** 2026-07-12  
**Package:** `src.core.context`

---

## 1. Architecture

```
Incoming HTTP Request
    │
    ▼
CorrelationMiddleware (BaseHTTPMiddleware)
    │
    ├── Extract/Generate correlation_id (X-Correlation-ID header)
    ├── Create RequestContext (immutable frozen dataclass)
    ├── Store in ContextVar (async-safe — each task isolated)
    ├── Bind to logging context (auto-appears in all log lines)
    │
    ▼
Route Handler → Business Logic → Response
    │                              │
    │   get_context() available    │   X-Correlation-ID header
    │   correlation_id in logs     │   X-Request-ID header
    │   correlation_id in metrics  │   X-Response-Time-Ms header
    │                              │
    ▼                              ▼
Response sent ←────────────────────┘
    │
    ▼
Context cleaned up (ContextVar reset to empty)
```

## 2. RequestContext Model

Immutable (frozen) dataclass. Each request gets a new instance.

```python
@dataclass(frozen=True)
class RequestContext:
    correlation_id: str       # UUID — persisted across services
    request_id: str           # UUID — unique per request
    request_start: float      # time.time()
    request_method: str       # GET, POST, etc.
    request_path: str         # /v1/valuate
    client_ip: str            # sha256:abc123... (hashed for privacy)
    user_agent: str
    user_id: str              # From JWT (future P0021 auth integration)
    role: str                 # RBAC role (future)
    country: str              # From request (future)
    api_version: str
    environment: str
```

## 3. Middleware Behavior

| Scenario | Behavior |
|----------|----------|
| Client sends `X-Correlation-ID: abc` | Reused — no new ID generated |
| No header present | Generates new UUID4 |
| Background task needs context | `clone_context()` + `run_with_context()` |
| Concurrent requests | Each has independent context via ContextVar |

### Response Headers

| Header | Example |
|--------|---------|
| `X-Correlation-ID` | `550e8400-e29b-41d4-a716-446655440000` |
| `X-Request-ID` | `6ba7b810-9dad-11d1-80b4-00c04fd430c8` |
| `X-Response-Time-Ms` | `145.3` |

## 4. Context Propagation

### Within a request (automatic)

```python
# Route handler
from src.core.context import correlation_id
cid = correlation_id()  # "550e8400-..."

# Deep in business logic
from src.core.context import get_context
ctx = get_context()
print(ctx.correlation_id)  # Same ID — no parameter passing needed
```

### Background tasks (explicit)

```python
from src.core.context import clone_context, run_with_context

ctx = clone_context()  # Snapshot current context
asyncio.create_task(run_with_context(background_job(), ctx))

async def background_job():
    cid = correlation_id()  # Inherited from parent request
    log.info("background_task_started")  # Includes correlation_id
```

### Thread workers (explicit)

```python
from src.core.context import clone_context, run_sync_with_context

ctx = clone_context()
thread = threading.Thread(
    target=run_sync_with_context, args=(my_func, ctx)
)
thread.start()
```

## 5. Logger Integration

No application code changes needed. The middleware calls `log_bind()` with context fields, so every log line within a request automatically includes `correlation_id`, `request_id`, `request_method`, `request_path`, etc.

## 6. Metrics Integration

No exporter changes needed. `get_context()` is available to any metric collector that wants to read the current request context. The `correlation_id` can be used as a metric label.

## 7. Performance

Middleware overhead: ~0.05 ms/request (two UUID generations + ContextVar set + dict operations). No I/O, no blocking — pure Python in-memory operations.

## 8. Async Isolation (verified)

```
Request A (correlation_id: aaa)     Request B (correlation_id: bbb)
        │                                    │
        ▼                                    ▼
   ContextVar = "aaa"                  ContextVar = "bbb"
        │                                    │
   await sleep(10ms)                   await sleep(5ms)
        │                                    │
        ▼                                    ▼
   ContextVar = "aaa" ✓               ContextVar = "bbb" ✓
```

ContextVars are copied on `asyncio.create_task()` and isolated per task. Two concurrent requests never see each other's context.

## 9. Future Integration Points

| Prompt | Integration |
|--------|-------------|
| P0022 | OpenTelemetry — set `trace_id`, `span_id` via `update_context()` |
| Auth integration | Populate `user_id`, `role` from JWT in middleware |
| Sentry | Attach `correlation_id` as Sentry tag |
| Background workers | Inherit parent context via `run_with_context()` |

---

*Request context documented 2026-07-12.*
