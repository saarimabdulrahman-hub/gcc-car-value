"""Auto-instrumentation — HTTP, database, ML, external API spans.

These modules create child spans automatically. Application code can also
use get_tracer() directly for custom spans.
"""

from src.core.tracing.instrumentation.http import HTTPInstrumentation
from src.core.tracing.instrumentation.database import DatabaseInstrumentation
from src.core.tracing.instrumentation.ml import MLInstrumentation

__all__ = ["HTTPInstrumentation", "DatabaseInstrumentation", "MLInstrumentation"]
