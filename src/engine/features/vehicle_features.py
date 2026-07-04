"""Features from the knowledge base (specs, ratings, issues)."""
import pandas as pd
from src.engine.features.base import BaseFeature, MarketContext, FeatureRegistry


class BrandReliabilityFeature(BaseFeature):
    name = "brand_reliability"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.brand_reliability_score or 3.0
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.brand_reliability_score or 3.0)


class DepreciationRateFeature(BaseFeature):
    name = "depreciation_rate"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.model_depreciation_rate or 0.12
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.model_depreciation_rate or 0.12)


class CommonIssueCountFeature(BaseFeature):
    name = "common_issue_count"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = float(context.model_common_issue_count)
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.model_common_issue_count)


# Register
for cls in [BrandReliabilityFeature, DepreciationRateFeature, CommonIssueCountFeature]:
    FeatureRegistry.register(cls())
