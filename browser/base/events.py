"""Browser events — lifecycle event types and event bus integration."""

# Standard browser event types
BROWSER_EVENTS = {
    "browser.started":    "Browser process started",
    "browser.stopped":    "Browser process stopped",
    "browser.crashed":    "Browser process crashed",
    "context.created":    "Browser context created",
    "context.closed":     "Browser context closed",
    "page.created":       "Page/tab opened",
    "page.closed":        "Page/tab closed",
    "navigation.started": "Page navigation started",
    "navigation.finished":"Page navigation completed",
    "navigation.failed":  "Page navigation failed",
    "download.started":   "File download started",
    "download.finished":  "File download completed",
    "download.failed":    "File download failed",
    "error":              "Generic browser error",
}
