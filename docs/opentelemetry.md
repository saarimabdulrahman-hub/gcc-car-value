# GCC Car Value — OpenTelemetry Distributed Tracing

**Date:** 2026-07-12  
**Package:** `src.core.tracing`  
**Status:** Optional — disabled by default. No dependency required when disabled.

---

## 1. Architecture

```
HTTP Request
    │
    ▼
CorrelationMiddleware  →  correlation_id injected
    │
    ▼
HTTPInstrumentation    →  Root span (http.method, http.path, http.status_code)
    │
    ├── DatabaseInstrumentation  →  Child span (db.system, db.operation, sanitized SQL)
    ├── MLInstrumentation        →  Child span (ml.model_version, ml.prediction_value)
    └── Custom spans via get_tracer()
    │
    ▼
BatchSpanProcessor → Exporter (Console | OTLP → Jaeger/Tempo)
```

## 2. Enabling Tracing

```bash
# Install OTel SDK + exporter
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# Enable in .env
OTEL_ENABLED=true
OTEL_EXPORTER=console    # or otlp
OTEL_SAMPLE_RATE=1.0     # 1.0 = trace everything, 0.1 = 10%
```

## 3. When Disabled (Default)

All operations are zero-overhead no-ops:
- `get_tracer()` returns a no-op tracer
- `tracer.start_span()` yields a `NoOpSpan`
- All `span.set_attribute()` calls do nothing
- No OpenTelemetry SDK is loaded
- No performance impact

Application code never needs `if is_tracing_enabled()` checks.

## 4. Span Hierarchy

```
HTTP GET /v1/valuate              (root, kind=server)
├── db.SELECT listings WHERE...   (child, kind=client)
├── db.SELECT comps WHERE...      (child, kind=client)
├── ml.predict (lightgbm)         (child, kind=internal)
│   └── ml.load_model             (child, kind=internal)
└── ml.fallback (if needed)       (child, kind=internal)
```

## 5. Automatic Context Injection

Every span automatically receives:

| Attribute | Source |
|-----------|--------|
| `correlation_id` | Request context |
| `request_id` | Request context |
| `user_id` | Request context (when available) |
| `http.method` | Request context |
| `http.path` | Request context |
| `service.name` | OTel resource |
| `service.version` | App config |
| `deployment.environment` | App config |

No application code changes needed.

## 6. Sampling

| Strategy | Config | Use Case |
|----------|--------|----------|
| Always On | `OTEL_SAMPLE_RATE=1.0` | Development, debugging |
| Ratio | `OTEL_SAMPLE_RATE=0.1` | Production (10%) |
| Always Off | `OTEL_ENABLED=false` | Disabled completely |

## 7. Exporters

| Exporter | Config | Endpoint |
|----------|--------|----------|
| Console | `OTEL_EXPORTER=console` | stdout |
| OTLP | `OTEL_EXPORTER=otlp` | `http://localhost:4317` |

OTLP works with Jaeger, Grafana Tempo, and any OTLP-compatible backend.

## 8. Usage in Application Code

```python
from src.core.tracing import get_tracer

tracer = get_tracer(__name__)

# Custom span
with tracer.start_span("custom_operation") as span:
    span.set_attribute("custom.key", "value")
    result = await do_work()
    span.set_attribute("custom.result", result)

# Database span
from src.core.tracing.instrumentation.database import DatabaseInstrumentation
db = DatabaseInstrumentation()
with db.start_query_span("SELECT listings WHERE make=$1") as span:
    result = await session.execute(stmt)

# ML span
from src.core.tracing.instrumentation.ml import MLInstrumentation
ml = MLInstrumentation()
with ml.start_prediction_span("lightgbm_v20260712") as span:
    result = model.predict(features)
    span.set_attribute("ml.prediction_value", result)
```

## 9. Sensitive Data Protection

SQL statements are automatically sanitized — literal values replaced with `?` — before being recorded in span attributes. Span attributes are passed through the same `mask_field()` filter used by the logging framework.

---

*OpenTelemetry documentation completed 2026-07-12.*
