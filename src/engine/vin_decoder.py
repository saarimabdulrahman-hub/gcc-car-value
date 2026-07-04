"""VIN decoder — validates VIN format and extracts basic info.

Full VIN decoding requires a commercial API (JATO, NHTSA, etc.).
This provides validation + basic extraction for GCC VINs.
API key configured via VIN_API_KEY env var.
"""
import re


def validate_vin(vin: str) -> bool:
    """Validate VIN format (ISO 3779)."""
    vin = vin.upper().strip()
    if len(vin) != 17:
        return False
    if "I" in vin or "O" in vin or "Q" in vin:
        return False  # These letters are never used in VINs
    return bool(re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin))


def decode_vin_basic(vin: str) -> dict | None:
    """Extract basic info from VIN without external API.

    WMI (chars 1-3) = manufacturer + country
    VDS (chars 4-9) = vehicle attributes
    VIS (chars 10-17) = model year + plant + serial

    Returns basic structure, full decode needs commercial API.
    """
    if not validate_vin(vin):
        return None

    vin = vin.upper()

    # WMI — World Manufacturer Identifier
    wmi = vin[:3]
    manufacturer = _wmi_lookup(wmi)

    # Model year (char 10)
    year_char = vin[9]
    model_year = _vin_year(year_char)

    # Plant code (char 11)
    plant = vin[10]

    return {
        "vin": vin,
        "valid": True,
        "wmi": wmi,
        "manufacturer": manufacturer,
        "model_year": model_year,
        "plant_code": plant,
        "needs_api_for_full_decode": True,
    }


def _wmi_lookup(wmi: str) -> str:
    """Look up manufacturer from WMI (chars 1-3). GCC-common manufacturers."""
    wmi_map = {
        "JTE": "Toyota (Japan)",
        "JTM": "Toyota (Japan)",
        "JTJ": "Lexus (Japan)",
        "JTH": "Lexus (Japan)",
        "JTD": "Toyota (Japan)",
        "JN1": "Nissan (Japan)",
        "JN8": "Nissan (Japan)",
        "JNR": "Nissan (Japan)",
        "JHM": "Honda (Japan)",
        "JH4": "Honda (Japan)",
        "KNA": "Kia (Korea)",
        "KNC": "Kia (Korea)",
        "KMH": "Hyundai (Korea)",
        "KMJ": "Hyundai (Korea)",
        "WBA": "BMW (Germany)",
        "WBS": "BMW M (Germany)",
        "WDD": "Mercedes-Benz (Germany)",
        "WDC": "Mercedes-Benz (Germany)",
        "WAU": "Audi (Germany)",
        "WP1": "Porsche (Germany)",
        "SAL": "Land Rover (UK)",
        "JMZ": "Mazda (Japan)",
        "MMB": "Mitsubishi (Japan)",
        "JM0": "Mazda (Japan)",
        "JM1": "Mazda (Japan)",
        "1FM": "Ford (USA)",
        "1FT": "Ford (USA)",
        "1GC": "Chevrolet (USA)",
        "1GT": "GMC (USA)",
    }
    return wmi_map.get(wmi, f"Unknown ({wmi})")


def _vin_year(char: str) -> int | None:
    """Decode VIN model year character."""
    year_map = {
        "A": 2010, "B": 2011, "C": 2012, "D": 2013, "E": 2014,
        "F": 2015, "G": 2016, "H": 2017, "J": 2018, "K": 2019,
        "L": 2020, "M": 2021, "N": 2022, "P": 2023, "R": 2024,
        "S": 2025, "T": 2026, "V": 2027, "W": 2028, "X": 2029,
        "Y": 2030,
    }
    return year_map.get(char)
