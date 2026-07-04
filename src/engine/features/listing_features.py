"""Features derived from the listing itself."""
import pandas as pd
from src.engine.features.base import BaseFeature, MarketContext, FeatureRegistry


class MileageFeature(BaseFeature):
    name = "mileage_km"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return df["mileage_km"].fillna(df["mileage_km"].median())

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return float(query.get("mileage_km", 0) or 0)


class VehicleAgeFeature(BaseFeature):
    name = "vehicle_age_years"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - df["year"]

    def compute_single(self, query: dict, context: MarketContext) -> float:
        from datetime import datetime
        return float(datetime.now().year - int(query.get("year", datetime.now().year)))


class SpecGCCFeature(BaseFeature):
    name = "is_gcc_spec"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return (df["spec"].fillna("").str.upper() == "GCC").astype(float)

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return 1.0 if str(query.get("spec", "")).upper() == "GCC" else 0.0


class SpecUSFeature(BaseFeature):
    name = "is_us_spec"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return (df["spec"].fillna("").str.upper() == "US").astype(float)

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return 1.0 if str(query.get("spec", "")).upper() == "US" else 0.0


class SellerDealerFeature(BaseFeature):
    name = "is_dealer"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return (df["seller_type"].fillna("") == "dealer").astype(float)

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return 1.0 if query.get("seller_type") == "dealer" else 0.0


class HasWarrantyFeature(BaseFeature):
    name = "has_warranty"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return df["warranty"].fillna(False).astype(float)

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return 1.0 if query.get("warranty") else 0.0


class HasServiceHistoryFeature(BaseFeature):
    name = "has_service_history"
    version = "1.0.0"

    def compute(self, df: pd.DataFrame, context: MarketContext) -> pd.Series:
        return df["service_history"].fillna(False).astype(float)

    def compute_single(self, query: dict, context: MarketContext) -> float:
        return 1.0 if query.get("service_history") else 0.0


# Register all listing features
for cls in [MileageFeature, VehicleAgeFeature, SpecGCCFeature, SpecUSFeature,
            SellerDealerFeature, HasWarrantyFeature, HasServiceHistoryFeature]:
    FeatureRegistry.register(cls())
