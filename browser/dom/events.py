"""DOM extraction lifecycle events."""

DOM_EVENTS = {
    "document.loaded":        "A document was loaded and parsed",
    "query.executed":         "A CSS selector query was executed",
    "node.extracted":         "A value was extracted from a node",
    "validation.failed":      "Extraction validation failed",
    "extraction.completed":   "Extraction of a document completed",
}
