"""Normalize scraped data to canonical forms. All normalization is idempotent."""
from datetime import datetime, timezone

MAKE_ALIASES: dict[str, str] = {
    "toyota": "Toyota", "nissan": "Nissan",
    "honda": "Honda", "hyundai": "Hyundai", "kia": "Kia",
    "ford": "Ford", "chevrolet": "Chevrolet", "bmw": "BMW",
    "mercedes": "Mercedes-Benz", "mercedes benz": "Mercedes-Benz",
    "audi": "Audi", "lexus": "Lexus", "mazda": "Mazda",
    "mitsubishi": "Mitsubishi", "land rover": "Land Rover",
    "range rover": "Land Rover", "porsche": "Porsche",
    "volkswagen": "Volkswagen", "vw": "Volkswagen",
    "gmc": "GMC", "cadillac": "Cadillac", "jeep": "Jeep",
    "dodge": "Dodge", "chrysler": "Chrysler", "infiniti": "Infiniti",
    "jaguar": "Jaguar", "volvo": "Volvo", "subaru": "Subaru",
    "suzuki": "Suzuki", "renault": "Renault", "peugeot": "Peugeot",
}

SPEC_ALIASES: dict[str, str] = {
    "gcc": "GCC", "gcc spec": "GCC", "gcc_spec": "GCC",
    "us": "US", "usa": "US", "american": "US", "american spec": "US",
    "us spec": "US", "us_spec": "US",
    "japan": "Japan", "japanese": "Japan", "japan spec": "Japan",
    "europe": "European", "european": "European", "euro": "European",
}

CITY_ALIASES: dict[str, str] = {
    "dubai": "Dubai",
    "abu dhabi": "Abu Dhabi",
    "sharjah": "Sharjah",
    "al ain": "Al Ain",
    "ajman": "Ajman",
    "ras al khaimah": "Ras Al Khaimah", "rak": "Ras Al Khaimah",
    "fujairah": "Fujairah",
    "riyadh": "Riyadh",
    "jeddah": "Jeddah",
    "dammam": "Dammam",
    "mecca": "Mecca", "makkah": "Mecca",
    "medina": "Medina", "madinah": "Medina",
    "kuwait city": "Kuwait City",
    "doha": "Doha",
    "muscat": "Muscat",
    "manama": "Manama",
}

EXCHANGE_RATES_TO_AED: dict[str, float] = {
    "AED": 1.0, "SAR": 0.978, "QAR": 1.007, "KWD": 11.94,
    "BHD": 9.76, "OMR": 9.55, "USD": 3.673,
}


def normalize_make(raw: str | None) -> str | None:
    if not raw:
        return None
    return MAKE_ALIASES.get(raw.lower().strip(), raw.strip().title())


def normalize_spec(raw: str | None) -> str | None:
    if not raw:
        return None
    return SPEC_ALIASES.get(raw.lower().strip(), raw.strip())


def normalize_city(raw: str | None) -> str | None:
    if not raw:
        return None
    return CITY_ALIASES.get(raw.lower().strip(), raw.strip().title())


def get_exchange_rate(currency: str) -> float:
    return EXCHANGE_RATES_TO_AED.get(currency.upper().strip(), 1.0)


def normalize_listing(data: dict) -> dict:
    data["make"] = normalize_make(data["make"])
    data["model"] = data.get("model", "").strip()
    data["year"] = int(data["year"])
    data["spec"] = normalize_spec(data.get("spec"))
    data["city"] = normalize_city(data.get("city"))
    original_currency = data.get("original_currency", "AED").upper().strip()
    exchange_rate = get_exchange_rate(original_currency)
    data["original_currency"] = original_currency
    data["exchange_rate"] = exchange_rate
    data["exchange_timestamp"] = data.get(
        "exchange_timestamp", datetime.now(timezone.utc).isoformat()
    )
    data["normalized_price_aed"] = float(data["asking_price"]) * exchange_rate
    data["original_price"] = float(data["asking_price"])
    return data
