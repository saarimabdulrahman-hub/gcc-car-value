"""Scraper constants — job states, defaults, configuration keys."""

from enum import StrEnum


class JobState(StrEnum):
    CREATED   = "created"
    READY     = "ready"
    RUNNING   = "running"
    WAITING   = "waiting"     # Rate-limited, waiting to proceed
    RETRYING  = "retrying"
    COMPLETED = "completed"
    FAILED    = "failed"
    CANCELLED = "cancelled"


# Terminal states — no further transitions
TERMINAL_STATES = {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}

# Default configuration
DEFAULT_TIMEOUT = 30          # seconds
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_BASE = 1.0    # seconds
DEFAULT_BACKOFF_MAX = 60.0    # seconds
DEFAULT_RATE_LIMIT = 2.0      # requests/second
DEFAULT_USER_AGENT = "GCCCarValue/1.0 (market research; +https://gcccarvalue.com)"
DEFAULT_CONCURRENCY = 1

# Retryable HTTP status codes
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
