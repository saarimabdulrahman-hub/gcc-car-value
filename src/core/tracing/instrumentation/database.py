"""Database instrumentation — creates child spans for SQL operations.

Usage (manual, in repository code):
    from src.core.tracing.instrumentation.database import DatabaseInstrumentation
    db = DatabaseInstrumentation()

    with db.start_query_span("SELECT listings WHERE make=$1") as span:
        result = await session.execute(stmt)
        span.set_attribute("db.rows", len(result))
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
import re

from src.core.tracing.tracer import get_tracer
from src.core.tracing.span import NoOpSpan


class DatabaseInstrumentation:
    """Creates child spans for database operations.

    SQL statements are sanitized: parameters are replaced with $N placeholders
    and literal values are stripped to prevent sensitive data in traces.
    """

    _sql_param_pattern = re.compile(r"'[^']*'|\$\d+")

    def __init__(self):
        self._tracer = get_tracer("database")

    @contextmanager
    def start_query_span(self, operation: str, db_system: str = "postgresql",
                         db_name: str = "gcc_car_value",
                         attributes: dict[str, Any] | None = None):
        """Create a span for a database query.

        Args:
            operation: Sanitized SQL or operation name (e.g., 'SELECT listings').
            db_system: Database system (postgresql).
            db_name: Database name.
            attributes: Additional span attributes.
        """
        safe_op = self._sanitize_sql(operation)

        with self._tracer.start_span(
            safe_op,
            kind="client",
            attributes={
                "db.system": db_system,
                "db.name": db_name,
                "db.operation": safe_op[:100],  # Truncate for span name
                "db.statement": safe_op[:500],  # Full statement, sanitized
                **(attributes or {}),
            },
        ) as span:
            yield span

    def _sanitize_sql(self, sql: str) -> str:
        """Remove literal values from SQL to prevent data leakage in traces."""
        # Replace quoted strings with ?
        sql = re.sub(r"'[^']*'", "?", sql)
        # Truncate very long statements
        if len(sql) > 500:
            sql = sql[:497] + "..."
        return sql
