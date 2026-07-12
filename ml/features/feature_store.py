"""Feature Store — load, save, list, build feature vectors."""

import threading
from ml.features.registry import FeatureRegistry
from ml.features.models import FeatureDefinition, FeatureVector
from ml.features.errors import FeatureNotFoundError


class FeatureStore:
    """Thread-safe store for feature vectors keyed by listing fingerprint."""

    def __init__(self, registry: FeatureRegistry | None = None):
        self._registry = registry or FeatureRegistry()
        self._vectors: dict[str, FeatureVector] = {}
        self._lock = threading.Lock()

    def save(self, vector: FeatureVector) -> None:
        with self._lock:
            self._vectors[vector.fingerprint or vector.listing_id] = vector

    def load(self, fingerprint: str) -> FeatureVector | None:
        with self._lock:
            return self._vectors.get(fingerprint)

    def build_vector(self, fingerprint: str, listing_id: str,
                     **values) -> FeatureVector:
        """Build a feature vector from raw values."""
        fv = FeatureVector(listing_id=listing_id, fingerprint=fingerprint)
        for name in self._registry.list_names():
            val = values.get(name)
            # Type coercion
            feat = self._registry.get(name)
            if feat.dtype == "int64" and val is not None:
                val = int(val)
            elif feat.dtype == "float64" and val is not None:
                val = float(val)
            fv.values[name] = val
        return fv

    def list_fingerprints(self) -> list[str]:
        with self._lock:
            return list(self._vectors.keys())

    def count(self) -> int:
        with self._lock:
            return len(self._vectors)

    def to_rows(self) -> list[dict]:
        """Convert all stored vectors to list-of-dicts (ready for DataFrame)."""
        with self._lock:
            return [
                {"listing_id": v.listing_id, "fingerprint": v.fingerprint, **v.values}
                for v in self._vectors.values()
            ]
