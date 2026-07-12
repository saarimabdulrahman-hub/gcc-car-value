"""NormalizationEngine — transforms marketplace-specific values to canonical forms.

Preserves original values in listing.metadata for audit trail.
"""

from __future__ import annotations

import re
from schema.listing import CanonicalListing
from normalization.models import NormalizationReport, FieldNormalization
from normalization.catalog import (
    MAKE_ALIASES, MODEL_ALIASES, TRANSMISSION_ALIASES,
    FUEL_ALIASES, BODY_ALIASES, COLOR_ALIASES,
    SPEC_ALIASES, CITY_ALIASES, MILEAGE_KM_PER_MILE,
)


class NormalizationEngine:
    """Normalizes a CanonicalListing into canonical values.

    Every normalization records the original → normalized mapping with
    confidence and rule metadata. Original values are preserved in
    listing.metadata["original_values"].

    Usage:
        engine = NormalizationEngine()
        report = engine.normalize(listing)
        # listing.make is now "Toyota" (was "toyota motors")
        # report.changed lists all changed fields
    """

    def normalize(self, listing: CanonicalListing) -> NormalizationReport:
        """Normalize a listing in-place. Returns a report."""
        report = NormalizationReport(
            listing_id=listing.listing_id,
            marketplace=listing.marketplace,
        )

        originals: dict[str, str] = {}

        # --- Make ---
        f = self._normalize_make(listing.vehicle.make)
        if f.original != f.normalized:
            originals["make"] = f.original
            listing.vehicle.make = f.normalized
        report.fields.append(f)

        # --- Model ---
        f = self._normalize_model(listing.vehicle.model, listing.vehicle.make)
        if f.original != f.normalized:
            originals["model"] = f.original
            listing.vehicle.model = f.normalized
        report.fields.append(f)

        # --- Trim ---
        f = self._normalize_trim(listing.vehicle.trim)
        if f.original != f.normalized:
            originals["trim"] = f.original
            listing.vehicle.trim = f.normalized
        report.fields.append(f)

        # --- Transmission ---
        f = self._normalize_transmission(listing.vehicle.transmission)
        if f.original != f.normalized:
            originals["transmission"] = f.original
            listing.vehicle.transmission = f.normalized
        report.fields.append(f)

        # --- Fuel ---
        f = self._normalize_fuel(listing.vehicle.fuel_type)
        if f.original != f.normalized:
            originals["fuel_type"] = f.original
            listing.vehicle.fuel_type = f.normalized
        report.fields.append(f)

        # --- Body ---
        f = self._normalize_body(listing.vehicle.body_type)
        if f.original != f.normalized:
            originals["body_type"] = f.original
            listing.vehicle.body_type = f.normalized
        report.fields.append(f)

        # --- Color ---
        f = self._normalize_color(listing.vehicle.color)
        if f.original != f.normalized:
            originals["color"] = f.original
            listing.vehicle.color = f.normalized
        report.fields.append(f)

        # --- Specification ---
        f = self._normalize_spec(listing.vehicle.specification)
        if f.original != f.normalized:
            originals["specification"] = f.original
            listing.vehicle.specification = f.normalized
        report.fields.append(f)

        # --- Mileage (unit conversion: miles → km) ---
        unit = listing.vehicle.mileage_unit.lower()
        if listing.vehicle.mileage_km > 0 and unit in ("mi", "miles", "mile"):
            original_km = listing.vehicle.mileage_km
            listing.vehicle.mileage_km = int(listing.vehicle.mileage_km * MILEAGE_KM_PER_MILE)
            listing.vehicle.mileage_unit = "km"
            report.fields.append(FieldNormalization(
                field="mileage_km", original=str(original_km),
                normalized=str(listing.vehicle.mileage_km),
                confidence=1.0, rule="mileage_unit_conversion",
                alias_used="mi→km",
            ))
            originals["mileage_km"] = str(original_km)

        # --- Location ---
        f = self._normalize_city(listing.location.city)
        if f.original != f.normalized:
            originals["city"] = f.original
            listing.location.city = f.normalized
        report.fields.append(f)

        # Store originals in metadata for audit
        if originals:
            listing.metadata["original_values"] = originals

        report.total_fields = len(report.fields)
        report.changed_fields = len([f for f in report.fields
                                     if f.original != f.normalized])
        return report

    # ------------------------------------------------------------------
    # Individual normalizers
    # ------------------------------------------------------------------

    def _normalize_make(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("make", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = MAKE_ALIASES.get(key)
        if canonical:
            return FieldNormalization("make", raw, canonical, 1.0,
                                      rule="make_alias", alias_used=key)
        return FieldNormalization("make", raw, raw.strip().title(), 0.7,
                                  rule="title_case")

    def _normalize_model(self, raw: str, make: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("model", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        # Check make-specific aliases
        if make in MODEL_ALIASES:
            canonical = MODEL_ALIASES[make].get(key)
            if canonical:
                return FieldNormalization("model", raw, canonical, 1.0,
                                          rule="model_alias", alias_used=key)
        # Fallback: title case
        cleaned = re.sub(r'\s+', ' ', raw.strip()).title()
        return FieldNormalization("model", raw, cleaned, 0.7,
                                  rule="title_case")

    def _normalize_trim(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("trim", "", "", 1.0, rule="empty")
        # Normalize: remove extra spaces, uppercase
        cleaned = re.sub(r'[\s\-]+', '', raw.strip()).upper()
        # Common patterns: VX-R → VXR, EX-L → EXL, V X R → VXR
        cleaned = re.sub(r'[\s\-]', '', cleaned)
        return FieldNormalization("trim", raw, cleaned, 0.9,
                                  rule="trim_normalize")

    def _normalize_transmission(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("transmission", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = TRANSMISSION_ALIASES.get(key)
        if canonical:
            return FieldNormalization("transmission", raw, canonical, 1.0,
                                      rule="transmission_alias", alias_used=key)
        return FieldNormalization("transmission", raw, raw.strip().lower(), 0.5,
                                  rule="lowercase")

    def _normalize_fuel(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("fuel_type", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = FUEL_ALIASES.get(key)
        if canonical:
            return FieldNormalization("fuel_type", raw, canonical, 1.0,
                                      rule="fuel_alias", alias_used=key)
        return FieldNormalization("fuel_type", raw, raw.strip().lower(), 0.5,
                                  rule="lowercase")

    def _normalize_body(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("body_type", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = BODY_ALIASES.get(key)
        if canonical:
            return FieldNormalization("body_type", raw, canonical, 1.0,
                                      rule="body_alias", alias_used=key)
        return FieldNormalization("body_type", raw, raw.strip().lower(), 0.5,
                                  rule="lowercase")

    def _normalize_color(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("color", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = COLOR_ALIASES.get(key)
        if canonical:
            return FieldNormalization("color", raw, canonical, 1.0,
                                      rule="color_alias", alias_used=key)
        return FieldNormalization("color", raw, raw.strip().title(), 0.5,
                                  rule="title_case")

    def _normalize_spec(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("specification", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = SPEC_ALIASES.get(key)
        if canonical:
            return FieldNormalization("specification", raw, canonical, 1.0,
                                      rule="spec_alias", alias_used=key)
        return FieldNormalization("specification", raw, raw.strip().title(), 0.5,
                                  rule="title_case")

    def _normalize_city(self, raw: str) -> FieldNormalization:
        if not raw:
            return FieldNormalization("city", "", "", 1.0, rule="empty")
        key = raw.lower().strip()
        canonical = CITY_ALIASES.get(key)
        if canonical:
            return FieldNormalization("city", raw, canonical, 1.0,
                                      rule="city_alias", alias_used=key)
        return FieldNormalization("city", raw, raw.strip().title(), 0.6,
                                  rule="title_case")
