"""TracingProvider — initializes OpenTelemetry with exporters and sampling.

OpenTelemetry is optional and disabled by default. When enabled, the provider
configures the SDK with the specified exporter and sampler. When disabled,
all tracing operations are no-ops with zero overhead.

Configuration via Settings:
    otel_enabled: bool = False
    otel_exporter: str = "console"   # "console" | "otlp" | "none"
    otel_sample_rate: float = 1.0    # 1.0 = all, 0.1 = 10%
"""

from __future__ import annotations

import structlog
from src.config import get_settings

logger = structlog.get_logger()

_provider_initialized = False


def is_tracing_enabled() -> bool:
    """Check if OpenTelemetry tracing is enabled and available."""
    settings = get_settings()
    if not getattr(settings, 'otel_enabled', False):
        return False
    try:
        import opentelemetry  # noqa: F401
        return True
    except ImportError:
        logger.warning("tracing_disabled", reason="opentelemetry_not_installed")
        return False


def init_tracing() -> None:
    """Initialize OpenTelemetry SDK if enabled.

    Called once at application startup. Safe to call multiple times —
    subsequent calls are no-ops.
    """
    global _provider_initialized
    if _provider_initialized:
        return

    if not is_tracing_enabled():
        logger.info("tracing_disabled", reason="otel_enabled=False")
        _provider_initialized = True
        return

    try:
        _do_init()
        _provider_initialized = True
        logger.info("tracing_initialized",
                    exporter=getattr(get_settings(), 'otel_exporter', 'console'))
    except Exception as e:
        logger.error("tracing_init_failed", error=str(e)[:200])
        _provider_initialized = True  # Don't retry


def _do_init() -> None:
    """Internal OpenTelemetry SDK initialization."""
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME

    settings = get_settings()

    # Resource — identifies this service
    resource = Resource.create({
        SERVICE_NAME: "gcc-car-value",
        "service.version": settings.api_version,
        "deployment.environment": settings.environment,
    })

    # Sampler
    sample_rate = getattr(settings, 'otel_sample_rate', 1.0)
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ALWAYS_ON, ALWAYS_OFF
    if sample_rate >= 1.0:
        sampler = ALWAYS_ON
    elif sample_rate <= 0.0:
        sampler = ALWAYS_OFF
    else:
        sampler = TraceIdRatioBased(sample_rate)

    # Provider
    provider = TracerProvider(resource=resource, sampler=sampler)

    # Exporter
    exporter = _create_exporter()
    if exporter is not None:
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)


def _create_exporter():
    """Create the configured exporter."""
    settings = get_settings()
    exporter_type = getattr(settings, 'otel_exporter', 'console')

    if exporter_type == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            return OTLPSpanExporter(
                endpoint=getattr(settings, 'otel_otlp_endpoint',
                                "http://localhost:4317"),
            )
        except ImportError:
            logger.warning("otlp_exporter_unavailable", reason="grpc not installed")
            return _console_exporter()

    if exporter_type == "console":
        return _console_exporter()

    return None


def _console_exporter():
    """Console exporter for development."""
    try:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        return ConsoleSpanExporter()
    except ImportError:
        return None
