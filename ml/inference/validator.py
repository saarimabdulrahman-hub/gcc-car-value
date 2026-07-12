"""Request Validator — missing features, numeric ranges, required fields, categorical values."""

from ml.inference.errors import ValidationError


class RequestValidator:
    def __init__(self, required_fields: list[str] | None = None,
                 numeric_ranges: dict[str, tuple[float, float]] | None = None,
                 categorical_values: dict[str, list[str]] | None = None):
        self._required = required_fields or ["make", "model", "year"]
        self._ranges = numeric_ranges or {
            "year": (1990, 2027), "mileage_km": (0, 1000000),
            "price": (0, 10000000),
        }
        self._categorical = categorical_values or {}

    def validate(self, features: dict) -> list[str]:
        """Validate feature dict. Returns list of errors (empty = valid)."""
        errors = []
        for field in self._required:
            if field not in features or features[field] is None or features[field] == "":
                errors.append(f"Missing required field: {field}")

        for field, (lo, hi) in self._ranges.items():
            val = features.get(field)
            if val is not None and val != "":
                try:
                    fval = float(val)
                    if fval < lo or fval > hi:
                        errors.append(f"Field '{field}'={fval} out of range [{lo}, {hi}]")
                except (ValueError, TypeError):
                    pass

        for field, allowed in self._categorical.items():
            val = features.get(field)
            if val is not None and val != "":
                if str(val) not in allowed:
                    errors.append(f"Field '{field}'='{val}' not in {allowed}")

        return errors

    def validate_or_raise(self, features: dict) -> None:
        errors = self.validate(features)
        if errors:
            raise ValidationError("; ".join(errors))
