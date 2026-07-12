"""Inference request model."""
from dataclasses import dataclass, field

@dataclass
class InferenceRequest:
    model_name: str = "valuation"
    features: dict = field(default_factory=dict)
    request_key: str = ""       # For deterministic routing
    cache_key: str = ""         # For prediction caching
