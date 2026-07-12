"""Browser pool event types for observability."""

POOL_EVENTS = {
    "browser.created":     "A new browser was created and added to the pool",
    "browser.recycled":    "A browser was stopped and removed from the pool",
    "browser.destroyed":   "A browser was destroyed after crash limit reached",
    "context.acquired":    "A context was leased from the pool",
    "context.released":    "A context was returned to the pool",
    "pool.expanded":       "The pool was scaled up (new browser added)",
    "pool.shrunk":         "The pool was scaled down (idle browser removed)",
    "lease.timeout":       "A lease exceeded the maximum lease duration",
    "health.failure":      "A browser failed its health check",
    "pool.exhausted":      "The pool reached maximum capacity with no idle slots",
}
