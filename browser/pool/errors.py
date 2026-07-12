"""Browser pool errors."""


class PoolError(Exception):
    """Base pool error."""


class PoolExhaustedError(PoolError):
    """No browsers available and pool is at maximum."""


class PoolShuttingDownError(PoolError):
    """Pool is shutting down — no new leases."""


class LeaseTimeoutError(PoolError):
    """Lease was held longer than max_lease_duration."""


class BrowserSlotError(PoolError):
    """A browser slot is in an invalid state."""
