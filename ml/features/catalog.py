"""Feature Catalog — 25+ pre-defined features for GCC vehicle valuation."""

from ml.features.models import FeatureDefinition

CATALOG: list[FeatureDefinition] = [
    # --- Vehicle identity ---
    FeatureDefinition("make", "Vehicle make", "object", source="vehicle", required=True),
    FeatureDefinition("model", "Vehicle model", "object", source="vehicle", required=True),
    FeatureDefinition("year", "Model year", "int64", source="vehicle", valid_range=(1990, 2027), required=True),
    FeatureDefinition("trim", "Trim level", "object", source="vehicle"),
    FeatureDefinition("body_type", "Body type", "object", source="vehicle",
                     categorical_values=["suv","sedan","hatchback","coupe","pickup","van","other"]),
    FeatureDefinition("fuel_type", "Fuel type", "object", source="vehicle",
                     categorical_values=["petrol","diesel","hybrid","electric","plugin_hybrid","other"]),
    FeatureDefinition("transmission", "Transmission", "object", source="vehicle",
                     categorical_values=["automatic","manual","cvt","dct","other"]),
    FeatureDefinition("specification", "Regional specification", "object", source="vehicle",
                     categorical_values=["GCC","US","Japan","European","Other"]),

    # --- Vehicle condition ---
    FeatureDefinition("mileage_km", "Odometer in km", "float64", source="vehicle",
                     valid_range=(0, 1000000)),
    FeatureDefinition("color", "Exterior color", "object", source="vehicle"),
    FeatureDefinition("vehicle_age_years", "Age of vehicle in years", "float64", source="vehicle"),
    FeatureDefinition("seller_type", "Seller type", "object", source="vehicle",
                     categorical_values=["private","dealer","auction","certified"]),

    # --- Pricing ---
    FeatureDefinition("price", "Asking price", "float64", source="pricing",
                     valid_range=(0, 10000000)),
    FeatureDefinition("currency", "Price currency", "object", source="pricing",
                     categorical_values=["AED","SAR","KWD","QAR","BHD","OMR","USD"]),

    # --- Location ---
    FeatureDefinition("country", "Listing country", "object", source="pricing",
                     categorical_values=["AE","SA","KW","QA","BH","OM"]),
    FeatureDefinition("city", "Listing city", "object", source="pricing"),

    # --- History & Lifecycle ---
    FeatureDefinition("days_active", "Days listing has been active", "float64", source="history"),
    FeatureDefinition("listing_age_days", "Days since first seen", "float64", source="history"),
    FeatureDefinition("snapshot_count", "Number of historical snapshots", "int64", source="history"),

    # --- Market Intelligence ---
    FeatureDefinition("price_index", "Market price index for segment", "float64", source="market_intelligence"),
    FeatureDefinition("depreciation_rate", "Annual depreciation rate %", "float64", source="market_intelligence"),
    FeatureDefinition("liquidity_score", "Market liquidity score", "float64", source="market_intelligence"),
    FeatureDefinition("market_health_score", "Market health stability score", "float64", source="market_intelligence"),
    FeatureDefinition("price_percentile", "Price percentile rank in segment", "float64", source="market_intelligence"),

    # --- Forecast Inputs ---
    FeatureDefinition("ma_30d", "30-day moving average price", "float64", source="market_intelligence"),
    FeatureDefinition("volatility_90d", "90-day price volatility", "float64", source="market_intelligence"),
    FeatureDefinition("inventory_delta", "30-day inventory change", "float64", source="market_intelligence"),
    FeatureDefinition("momentum_score", "Market momentum score", "float64", source="market_intelligence"),
    FeatureDefinition("freshness_score", "Listing freshness score", "float64", source="market_intelligence"),
]
