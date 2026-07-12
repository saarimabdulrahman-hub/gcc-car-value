"""Binary lifecycle event types."""

BINARY_EVENTS = {
    "binary.registered":  "A binary was registered",
    "binary.removed":     "A binary was removed",
    "binary.validated":   "A binary passed validation",
    "binary.invalid":     "A binary failed validation",
    "binary.selected":    "A binary was selected for use",
    "cache.hit":          "Validation cache hit",
    "cache.miss":         "Validation cache miss",
    "cache.refreshed":    "Cache was cleared and rebuilt",
}
