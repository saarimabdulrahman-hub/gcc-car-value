"""Browser pool — manages browser lifecycle, leasing, scaling, and recycling."""
from browser.pool.browser_pool import BrowserPool
from browser.pool.config import PoolConfig
from browser.pool.errors import PoolExhaustedError, PoolShuttingDownError

__all__ = ["BrowserPool", "PoolConfig", "PoolExhaustedError", "PoolShuttingDownError"]
