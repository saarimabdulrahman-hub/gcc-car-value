"""Driver lifecycle event types."""

DRIVER_EVENTS = {
    "driver.registered":   "A driver was registered",
    "driver.removed":      "A driver was removed",
    "driver.started":      "A driver launched a browser",
    "driver.stopped":      "A driver was shutdown",
    "driver.failed":       "A driver failed to launch or crashed",
    "driver.restarted":    "A driver was recovered and restarted",
    "driver.selected":     "A driver was selected for a request",
    "capability.missing":  "Required capability not found in any driver",
    "driver.unhealthy":    "A driver failed its health check",
}
