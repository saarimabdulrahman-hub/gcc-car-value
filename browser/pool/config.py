"""Pool configuration — min/max browsers, contexts per browser, timeouts."""

from dataclasses import dataclass


@dataclass
class PoolConfig:
    """Configuration for the BrowserPool."""
    min_browsers: int = 1           # Minimum warm pool size
    max_browsers: int = 5           # Maximum browsers allowed
    max_contexts_per_browser: int = 20  # Contexts per browser before recycling
    max_idle_seconds: float = 300.0     # Idle before a browser is recycled (5 min)
    max_lifetime_seconds: float = 3600.0 # Max browser lifetime (1 hour)
    lease_timeout: float = 30.0         # Max time to wait for a lease
    max_lease_duration: float = 600.0   # Max time a lease can be held (10 min)
    health_check_interval: float = 30.0  # Seconds between health checks
    warm_pool_size: int = 1             # Browsers kept warm when idle
    memory_limit_mb: int = 512          # Recycle browser if RSS exceeds this
    crash_limit: int = 3                # Remove browser after N crashes
