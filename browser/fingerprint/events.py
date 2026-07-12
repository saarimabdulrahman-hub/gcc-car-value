"""Fingerprint lifecycle event types."""

FINGERPRINT_EVENTS = {
    "profile.assigned":          "A profile was assigned to a session",
    "profile.released":          "A profile was released from a session",
    "profile.validation_failed": "A profile failed validation",
    "profile.rotated":           "A session's profile was rotated",
    "profile.applied":           "A profile's headers were applied to a context",
}
