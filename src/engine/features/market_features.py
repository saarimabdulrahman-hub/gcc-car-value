"""Features derived from market context."""
import pandas as pd
from src.engine.features.base import BaseFeature, MarketContext, FeatureRegistry


class SegmentMedianPrice(BaseFeature):
    name = "segment_median_price"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.segment_median_price or 0
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.segment_median_price or 0)


class SegmentLiquidity(BaseFeature):
    name = "segment_liquidity_days"
    version = "1.0.0"
    dependencies = ["segment_median_price"]

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.segment_median_days_to_sell or 30
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.segment_median_days_to_sell or 30)


class PriceVolatilityFeature(BaseFeature):
    name = "price_volatility"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.segment_price_volatility or 0.05
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.segment_price_volatility or 0.05)


class MarketTrend4WeekFeature(BaseFeature):
    name = "market_trend_4w"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = context.segment_volume_change_4w or 0.0
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.segment_volume_change_4w or 0.0)


class ListingVolumeFeature(BaseFeature):
    name = "listing_volume"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        val = float(context.segment_listing_count)
        return pd.Series([val] * len(df))

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(context.segment_listing_count)


# Register
for cls in [SegmentMedianPrice, SegmentLiquidity, PriceVolatilityFeature,
            MarketTrend4WeekFeature, ListingVolumeFeature]:
    FeatureRegistry.register(cls())
