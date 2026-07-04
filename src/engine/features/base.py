"""Base feature class — every feature inherits from this."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd


@dataclass
class MarketContext:
    """Lightweight context object built from DB for feature computation."""
    make: str
    model: str
    year: int
    country: str | None
    segment_median_price: float | None = None
    segment_listing_count: int = 0
    segment_median_days_to_sell: float | None = None
    segment_price_volatility: float | None = None
    segment_volume_change_4w: float | None = None
    brand_reliability_score: float | None = None
    model_depreciation_rate: float | None = None
    model_common_issue_count: int = 0
    city_premium_pct: float | None = None
    seasonality_index: float | None = None


class BaseFeature(ABC):
    """Abstract feature. Each feature is a ~30-line class with one responsibility."""

    name: str
    version: str = "1.0.0"
    dependencies: list[str] = []

    @abstractmethod
    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        """Compute feature values for a DataFrame (used during training)."""
        ...

    @abstractmethod
    def compute_single(self, query: dict, context: MarketContext) -> float:
        """Compute feature value for a single valuation query."""
        ...


class FeatureRegistry:
    """Auto-discovers and manages all features."""

    _features: dict[str, BaseFeature] = {}

    @classmethod
    def register(cls, feature: BaseFeature) -> None:
        cls._features[feature.name] = feature

    @classmethod
    def get(cls, name: str) -> BaseFeature:
        return cls._features[name]

    @classmethod
    def all(cls) -> dict[str, BaseFeature]:
        return cls._features

    @classmethod
    def ordered(cls) -> list[BaseFeature]:
        """Topological sort by dependencies."""
        resolved = []
        seen = set()

        def resolve(f: BaseFeature):
            if f.name in seen:
                return
            seen.add(f.name)
            for dep_name in f.dependencies:
                if dep_name in cls._features:
                    resolve(cls._features[dep_name])
            resolved.append(f)

        for f in cls._features.values():
            resolve(f)
        return resolved
