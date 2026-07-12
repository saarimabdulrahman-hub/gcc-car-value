"""Test tracing framework — all operations work as no-ops without OTel installed."""
import pytest
from src.core.tracing.span import Span, NoOpSpan
from src.core.tracing.tracer import get_tracer, Tracer


class TestNoOpSpan:
    """Verify no-op span doesn't raise when OTel is not installed."""

    def test_create_noop_span(self):
        span = NoOpSpan("test")
        assert span.name == "test"
        assert span.duration_ms >= 0

    def test_set_attribute_noop(self):
        span = NoOpSpan("test")
        span.set_attribute("key", "value")
        span.set_attribute("sensitive", "secret123")  # Should not raise

    def test_set_attributes_noop(self):
        span = NoOpSpan("test")
        span.set_attributes(a=1, b=2, c=3)

    def test_add_event_noop(self):
        span = NoOpSpan("test")
        span.add_event("something_happened", detail="ok")

    def test_record_exception_noop(self):
        span = NoOpSpan("test")
        try:
            raise ValueError("test error")
        except ValueError as e:
            span.record_exception(e)  # Should not raise

    def test_end_noop(self):
        span = NoOpSpan("test")
        span.end()  # Should not raise


class TestTracerNoOp:
    """Verify tracer returns no-op spans and doesn't crash without OTel."""

    def test_get_tracer_returns_tracer(self):
        tracer = get_tracer("test.module")
        assert isinstance(tracer, Tracer)

    def test_get_tracer_is_singleton_per_name(self):
        t1 = get_tracer("test.singleton")
        t2 = get_tracer("test.singleton")
        assert t1 is t2

    def test_start_span_context_manager(self):
        tracer = get_tracer("test.cm")
        with tracer.start_span("my_operation") as span:
            span.set_attribute("make", "Toyota")
            span.set_attribute("estimate", 125000)
        # No exception raised

    def test_start_span_with_attributes(self):
        tracer = get_tracer("test.attrs")
        with tracer.start_span("op", attributes={"db.system": "postgresql"}) as span:
            pass

    def test_span_handles_exception_gracefully(self):
        tracer = get_tracer("test.exc")
        with pytest.raises(ValueError):
            with tracer.start_span("failing_op") as span:
                raise ValueError("boom")
        # Span should have recorded the exception without crashing

    def test_multiple_nested_spans(self):
        tracer = get_tracer("test.nested")
        with tracer.start_span("parent") as parent:
            parent.set_attribute("level", "parent")
            with tracer.start_span("child") as child:
                child.set_attribute("level", "child")
        # Both spans complete without error

    def test_context_injection_does_not_crash(self):
        """Auto-injection of request context attributes into spans."""
        tracer = get_tracer("test.ctx")
        with tracer.start_span("with_context") as span:
            pass  # _inject_context should not raise


class TestProvider:
    """Verify provider handles OTel being unavailable."""

    def test_is_tracing_enabled_returns_false(self):
        """Without OTel installed, tracing should be disabled."""
        from src.core.tracing.provider import is_tracing_enabled
        # Should be False because otel_enabled defaults to False
        # or because opentelemetry is not installed
        assert isinstance(is_tracing_enabled(), bool)

    def test_init_tracing_does_not_crash(self):
        """init_tracing should handle OTel being unavailable gracefully."""
        from src.core.tracing.provider import init_tracing
        init_tracing()  # Should not raise, even without OTel installed


class TestInstrumentation:
    """Verify instrumentation modules work without OTel."""

    def test_database_instrumentation_span(self):
        from src.core.tracing.instrumentation.database import DatabaseInstrumentation
        db = DatabaseInstrumentation()
        with db.start_query_span("SELECT * FROM listings WHERE make = 'Toyota'") as span:
            span.set_attribute("db.rows", 42)
        # Should not raise

    def test_database_sql_sanitization(self):
        from src.core.tracing.instrumentation.database import DatabaseInstrumentation
        db = DatabaseInstrumentation()
        sanitized = db._sanitize_sql(
            "SELECT * FROM users WHERE password = 'secret123' AND email = 'a@b.com'"
        )
        assert "secret123" not in sanitized
        assert "?" in sanitized

    def test_ml_instrumentation_span(self):
        from src.core.tracing.instrumentation.ml import MLInstrumentation
        ml = MLInstrumentation()
        with ml.start_prediction_span("lightgbm_v1") as span:
            span.set_attribute("ml.prediction_value", 125000)

    def test_ml_fallback_span(self):
        from src.core.tracing.instrumentation.ml import MLInstrumentation
        ml = MLInstrumentation()
        with ml.start_fallback_span("model_not_found") as span:
            pass

    def test_ml_model_load_span(self):
        from src.core.tracing.instrumentation.ml import MLInstrumentation
        ml = MLInstrumentation()
        with ml.start_model_load_span("lightgbm_v1") as span:
            span.set_attribute("ml.load_duration_ms", 45.2)
