"""Logging configuration — structlog processors, dev/prod mode, log levels."""

import logging
import structlog

from src.config import get_settings


def configure_logging() -> None:
    """Configure structlog for the application.

    Called once at startup (in main.py). Sets up processors for both
    development (colored console) and production (JSON lines) modes.
    """
    settings = get_settings()

    # Default processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _add_standard_fields,
    ]

    # Environment-specific renderer
    if settings.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer(serializer=_json_serializer))

    # Level filter
    processors.insert(1, structlog.stdlib.filter_by_level)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set root logger level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)

    # Quiet noisy third-party loggers
    for noisy in ("uvicorn.access", "botocore", "boto3", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _add_standard_fields(logger, method_name, event_dict):
    """Inject standard metadata into every log entry."""
    settings = get_settings()
    event_dict.setdefault("service", "gcc-car-value")
    event_dict.setdefault("environment", settings.environment)
    event_dict.setdefault("version", settings.api_version)
    import os
    event_dict.setdefault("hostname", os.uname().nodename if hasattr(os, 'uname') else "unknown")
    event_dict.setdefault("pid", os.getpid())
    return event_dict


def _json_serializer(obj, **kwargs):
    """JSON serializer that handles non-serializable objects gracefully."""
    import json
    return json.dumps(obj, default=str, **kwargs)
