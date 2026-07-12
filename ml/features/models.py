"""Feature and dataset models."""

from dataclasses import dataclass, field
import time


@dataclass
class FeatureDefinition:
    """A single feature registered in the Feature Registry."""
    name: str
    description: str = ""
    dtype: str = "float64"         # float64, int64, object, bool
    version: int = 1
    dependencies: list[str] = field(default_factory=list)
    source: str = ""                # "vehicle", "pricing", "market_intelligence", "history"
    valid_range: tuple = ()         # (min, max) for numeric validation
    categorical_values: list[str] = field(default_factory=list)
    required: bool = False


@dataclass
class DatasetVersion:
    """Version metadata for a built dataset."""
    dataset_id: str = ""
    version: int = 1
    created_at: float = field(default_factory=time.time)
    feature_schema_version: int = 1
    snapshot_range: tuple[float, float] = (0.0, 0.0)
    marketplace_coverage: list[str] = field(default_factory=list)
    row_count: int = 0
    feature_count: int = 0
    checksum: str = ""
    filters_applied: dict = field(default_factory=dict)


@dataclass
class FeatureVector:
    """A single feature vector (one row in the dataset)."""
    listing_id: str = ""
    fingerprint: str = ""
    values: dict[str, float | int | str | bool] = field(default_factory=dict)
