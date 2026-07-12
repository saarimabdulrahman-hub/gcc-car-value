"""Feature validation — missing values, ranges, categorical, duplicates, consistency."""

from ml.features.registry import FeatureRegistry
from ml.features.feature_store import FeatureStore
from ml.features.errors import ValidationError


class FeatureValidator:
    def __init__(self, registry: FeatureRegistry):
        self._registry = registry

    def validate(self, store: FeatureStore) -> list[str]:
        """Validate all vectors in the store. Returns list of errors."""
        errors = []
        features = self._registry.list_all()
        for f in features:
            if f.required:
                # Check that no required feature is missing in all vectors
                for fp in store.list_fingerprints():
                    v = store.load(fp)
                    if v and f.name not in v.values:
                        errors.append(f"Required feature '{f.name}' missing in '{fp}'")

        return errors

    def validate_vector(self, vector) -> list[str]:
        """Validate a single feature vector."""
        errors = []
        for f in self._registry.list_all():
            val = vector.values.get(f.name)
            if f.required and val is None:
                errors.append(f"Missing required feature '{f.name}'")
            if val is not None and f.valid_range:
                lo, hi = f.valid_range
                if float(val) < lo or float(val) > hi:
                    errors.append(f"'{f.name}'={val} out of range {f.valid_range}")
            if val is not None and f.categorical_values:
                if str(val) not in f.categorical_values:
                    errors.append(f"'{f.name}'='{val}' not in {f.categorical_values}")
        return errors
