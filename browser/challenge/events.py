"""Challenge lifecycle event types."""

CHALLENGE_EVENTS = {
    "challenge.detected":      "A challenge was detected on a page",
    "challenge.classified":    "A challenge was classified",
    "recovery.started":        "Recovery actions started",
    "recovery.succeeded":      "Recovery succeeded",
    "recovery.failed":         "Recovery failed",
    "recovery.escalated":      "Challenge escalated for manual review",
    "recovery.aborted":        "Job aborted due to unrecoverable challenge",
    "browser.restarted":       "Browser was restarted as recovery action",
    "session.restarted":       "Session was restarted as recovery action",
}
