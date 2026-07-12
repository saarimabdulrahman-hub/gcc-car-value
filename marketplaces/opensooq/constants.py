"""OpenSooq constants — multi-country configuration."""

MARKETPLACE_NAME = "opensooq"
DEFAULT_COUNTRY = "AE"

# Country-specific configuration
COUNTRY_CONFIGS = {
    "AE": {"base_url": "https://ae.opensooq.com", "currency": "AED", "locale": "ar",
           "timezone": "Asia/Dubai", "country_name": "UAE"},
    "SA": {"base_url": "https://sa.opensooq.com", "currency": "SAR", "locale": "ar",
           "timezone": "Asia/Riyadh", "country_name": "Saudi Arabia"},
    "KW": {"base_url": "https://kw.opensooq.com", "currency": "KWD", "locale": "ar",
           "timezone": "Asia/Kuwait", "country_name": "Kuwait"},
    "QA": {"base_url": "https://qa.opensooq.com", "currency": "QAR", "locale": "ar",
           "timezone": "Asia/Qatar", "country_name": "Qatar"},
    "BH": {"base_url": "https://bh.opensooq.com", "currency": "BHD", "locale": "ar",
           "timezone": "Asia/Bahrain", "country_name": "Bahrain"},
    "OM": {"base_url": "https://om.opensooq.com", "currency": "OMR", "locale": "ar",
           "timezone": "Asia/Muscat", "country_name": "Oman"},
}

SUPPORTED_COUNTRIES = list(COUNTRY_CONFIGS.keys())
