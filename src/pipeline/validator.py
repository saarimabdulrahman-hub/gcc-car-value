from dataclasses import dataclass, field
from datetime import datetime
import pandera as pa


class ListingSchema(pa.DataFrameModel):
    make: str = pa.Field(nullable=False)
    model: str = pa.Field(nullable=False)
    year: int = pa.Field(in_range={"min_value": 1990, "max_value": 2027}, nullable=False)
    asking_price: float = pa.Field(gt=0, lt=10_000_000, nullable=False)
    mileage_km: int = pa.Field(ge=0, le=1_000_000, nullable=True)
    spec: str = pa.Field(isin=["GCC", "US", "Japan", "European", "Other", None], nullable=True)
    city: str = pa.Field(nullable=False)
    country: str = pa.Field(isin=["AE", "SA", "QA", "KW", "BH", "OM"], nullable=False)
    source: str = pa.Field(nullable=False)
    external_id: str = pa.Field(nullable=False)

    # Remaining columns are optional and not validated strictly
    # — they may or may not be present in scraped data

    class Config:
        coerce = True

    @pa.dataframe_check
    def year_not_future(cls, df):
        return df["year"] <= datetime.now().year + 1

    @pa.dataframe_check
    def reasonable_price(cls, df):
        suspicious = df["asking_price"].isin([1, 123, 1234, 12345, 123456])
        return ~suspicious.any()


@dataclass
class ValidationResult:
    is_valid: bool
    data: dict | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_listing(data: dict) -> ValidationResult:
    import pandas as pd

    errors = []
    warnings = []

    required = ["make", "model", "year", "asking_price", "city", "country", "source", "external_id"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"missing_required_field: {field}")

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    try:
        data["year"] = int(data["year"])
        data["asking_price"] = float(data["asking_price"])
        if "mileage_km" in data and data["mileage_km"] is not None:
            data["mileage_km"] = int(data["mileage_km"])
    except (ValueError, TypeError) as e:
        errors.append(f"type_coercion_error: {e}")
        return ValidationResult(is_valid=False, data=data, errors=errors)

    try:
        # Build DataFrame with only schema-defined columns
        schema_cols = {
            "make", "model", "year", "asking_price", "mileage_km",
            "spec", "city", "country", "source", "external_id",
        }
        df_data = {k: v for k, v in data.items() if k in schema_cols}
        # Ensure all required columns exist
        for col in schema_cols:
            if col not in df_data:
                df_data[col] = None
        df = pd.DataFrame([df_data])
        ListingSchema.validate(df)
    except pa.errors.SchemaError as e:
        errors.append(f"schema_error: {e}")
        return ValidationResult(is_valid=False, data=data, errors=errors)

    if data.get("mileage_km") and data["mileage_km"] > 500_000:
        warnings.append("high_mileage")
    if data.get("year") and data["year"] < 2000:
        warnings.append("old_vehicle")

    return ValidationResult(is_valid=True, data=data, errors=errors, warnings=warnings)
