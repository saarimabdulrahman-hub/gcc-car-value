"""Feature Registry — register, lookup, enumerate feature definitions."""

import threading
from ml.features.models import FeatureDefinition
from ml.features.errors import DuplicateFeatureError, FeatureNotFoundError
from ml.features.catalog import CATALOG


class FeatureRegistry:
    """Thread-safe registry of FeatureDefinitions."""

    def __init__(self):
        self._features: dict[str, FeatureDefinition] = {}
        self._lock = threading.Lock()
        # Auto-register catalog features
        for f in CATALOG:
            self._features[f.name] = f

    def register(self, feature: FeatureDefinition) -> None:
        with self._lock:
            if feature.name in self._features:
                raise DuplicateFeatureError(f"Feature '{feature.name}' already registered")
            self._features[feature.name] = feature

    def get(self, name: str) -> FeatureDefinition:
        with self._lock:
            if name not in self._features:
                raise FeatureNotFoundError(f"Feature '{name}' not found")
            return self._features[name]

    def list_all(self) -> list[FeatureDefinition]:
        with self._lock:
            return list(self._features.values())

    def list_names(self) -> list[str]:
        with self._lock:
            return sorted(self._features.keys())

    def count(self) -> int:
        with self._lock:
            return len(self._features)

    @property
    def schema_version(self) -> int:
        """Schema version increments when features change."""
        return hash(tuple(sorted(self._features.keys()))) % 10000
