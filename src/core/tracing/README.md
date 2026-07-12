# Distributed Tracing

**Package:** `src.core.tracing`  
**Status:** Optional — disabled by default (no OpenTelemetry dependency required)

## Quick Start

```python
from src.core.tracing import get_tracer

tracer = get_tracer(__name__)

# Create a span
with tracer.start_span("my_operation") as span:
    span.set_attribute("key", "value")
    result = do_work()
    span.set_attribute("result", result)

# Auto-instrumentation
# HTTP spans are created automatically by middleware
# Database spans: use DatabaseInstrumentation
# ML spans: use MLInstrumentation
```

## Enabling Tracing

1. Install OpenTelemetry:
   ```bash
   pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
   ```

2. Set environment variables:
   ```bash
   OTEL_ENABLED=true
   OTEL_EXPORTER=console   # or otlp
   OTEL_SAMPLE_RATE=1.0    # 1.0 = all traces
   ```

## When Disabled

All tracing operations become zero-overhead no-ops. No errors, no warnings, no
performance impact. Application code never checks `is_tracing_enabled()`.
