"""Session lifecycle event types."""

SESSION_EVENTS = {
    "session.created":     "A new session was created",
    "session.restored":    "A session was restored from storage",
    "session.released":    "A session was released after use",
    "session.expired":     "A session expired (timeout or lifetime)",
    "session.destroyed":   "A session was destroyed and cleaned up",
    "cookies.imported":    "Cookies were imported from a browser context",
    "cookies.exported":    "Cookies were exported to a browser context",
    "storage.saved":       "Storage state was saved",
    "storage.restored":    "Storage state was restored",
}
