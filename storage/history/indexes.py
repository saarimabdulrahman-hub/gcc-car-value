"""Index metadata — documents which indexes exist for query optimization."""

INDEXES = {
    "idx_fingerprint":    {"fields": ["fingerprint"], "unique": True},
    "idx_marketplace":    {"fields": ["marketplace"]},
    "idx_timestamp":       {"fields": ["captured_at"], "partitioned": True},
    "idx_lifecycle":       {"fields": ["lifecycle_state"]},
    "idx_price":           {"fields": ["price"]},
    "idx_marketplace_ts":  {"fields": ["marketplace", "captured_at"]},
}
