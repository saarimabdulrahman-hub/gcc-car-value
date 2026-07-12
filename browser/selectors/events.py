"""Selector lifecycle event types."""

SELECTOR_EVENTS = {
    "selector.registered":    "A selector was registered",
    "selector.updated":       "A selector was updated",
    "selector.removed":       "A selector was removed",
    "selector.executed":      "A selector was executed against a document",
    "fallback.triggered":     "A fallback selector was used",
    "selector.validation_failed": "Selector validation failed",
    "selector.deprecated":    "A selector was marked deprecated",
}
