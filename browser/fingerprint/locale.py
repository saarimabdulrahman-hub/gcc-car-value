"""Locale consistency rules for GCC countries."""

# Country → canonical locale and language header
LOCALE_RULES = {
    "AE": {"locale": "en-AE", "language": "en-US,en;q=0.9,ar;q=0.8"},
    "SA": {"locale": "ar-SA", "language": "ar,en-US;q=0.9,en;q=0.8"},
    "KW": {"locale": "en-KW", "language": "en-US,en;q=0.9,ar;q=0.8"},
    "QA": {"locale": "en-QA", "language": "en-US,en;q=0.9,ar;q=0.8"},
    "BH": {"locale": "en-BH", "language": "en-US,en;q=0.9,ar;q=0.8"},
    "OM": {"locale": "en-OM", "language": "en-US,en;q=0.9,ar;q=0.8"},
}


def locale_for_country(country: str) -> str:
    return LOCALE_RULES.get(country, {}).get("locale", "en-AE")


def language_for_country(country: str) -> str:
    return LOCALE_RULES.get(country, {}).get("language", "en-US,en;q=0.9,ar;q=0.8")
