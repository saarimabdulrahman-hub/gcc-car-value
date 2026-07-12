"""Log formatter — JSON and console output formatting.

The actual formatting is handled by structlog processors configured in
config.py. This module provides the formatter API for direct use cases.
"""

from src.core.logging.config import _add_standard_fields, _json_serializer

__all__ = ["format_json", "format_console"]


def format_json(event_dict: dict) -> str:
    """Format a log event dict as a JSON string with standard fields."""
    enriched = _add_standard_fields(None, "info", dict(event_dict))
    return _json_serializer(enriched)


def format_console(event_dict: dict) -> str:
    """Format a log event dict for human-readable console output."""
    enriched = _add_standard_fields(None, "info", dict(event_dict))
    parts = [
        f'{enriched.get("timestamp", "")}',
        f'[{enriched.get("level", "info")}]',
        enriched.get("event", ""),
    ]
    for k, v in enriched.items():
        if k not in ("timestamp", "level", "event", "service",
                     "environment", "version", "hostname", "pid"):
            parts.append(f"{k}={v}")
    return " ".join(str(p) for p in parts)
