"""Timezone consistency rules for GCC countries."""

# Country → valid timezone
COUNTRY_TO_TIMEZONE = {
    "AE": "Asia/Dubai",
    "SA": "Asia/Riyadh",
    "KW": "Asia/Kuwait",
    "QA": "Asia/Qatar",
    "BH": "Asia/Bahrain",
    "OM": "Asia/Muscat",
}


def timezone_for_country(country: str) -> str:
    """Return the canonical timezone for a GCC country."""
    return COUNTRY_TO_TIMEZONE.get(country, "Asia/Dubai")


def is_valid_timezone(country: str, timezone: str) -> bool:
    expected = COUNTRY_TO_TIMEZONE.get(country)
    return expected is not None and expected == timezone
