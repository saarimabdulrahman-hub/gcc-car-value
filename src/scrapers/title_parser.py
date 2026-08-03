"""Shared make/model extraction from listing titles.

All scrapers use this. Multi-word makes must be matched longest-first,
otherwise "Land Rover Range Rover" yields make="Land".
"""
import re

# Longest-first so "Land Rover" wins over "Land". Lowercase keys.
MULTI_WORD_MAKES = [
    "mercedes benz", "mercedes-benz", "land rover", "range rover",
    "alfa romeo", "aston martin", "rolls royce", "rolls-royce",
    "great wall",
]

SINGLE_WORD_MAKES = [
    "toyota", "nissan", "honda", "hyundai", "kia", "ford", "chevrolet",
    "bmw", "mercedes", "audi", "lexus", "mazda", "mitsubishi", "porsche",
    "volkswagen", "vw", "gmc", "cadillac", "jeep", "dodge", "chrysler",
    "infiniti", "jaguar", "volvo", "subaru", "suzuki", "renault",
    "peugeot", "bentley", "ferrari", "lamborghini", "maserati", "mini",
    "tesla", "genesis", "changan", "chery", "haval", "mg", "byd",
]

_NOISE = re.compile(
    r'\b(19\d{2}|20[0-3]\d)\b'                 # years
    r'|\b\d[\d,]*\s*km\b'                       # mileage
    r'|\bgcc\b|\bus\s*spec\b|\bjapan(ese)?\b|\beuro(pean)?\b|\bamerican\b'
    r'|\bfor sale\b|\bused\b|\bnew\b|\baed\b|\bsar\b',
    re.IGNORECASE,
)


def extract_make_model(title: str) -> tuple[str, str]:
    """Return (make, model). Either may be "" if not confidently found.

    Strips years, mileage, spec words, and filler before taking the model,
    so "Toyota Camry 2020 GCC 50,000 km" -> ("Toyota", "Camry").
    """
    if not title:
        return "", ""

    cleaned = _NOISE.sub(" ", title)
    cleaned = re.sub(r'[|/,\-–—]+', " ", cleaned)
    cleaned = re.sub(r'\s+', " ", cleaned).strip()
    low = cleaned.lower()

    for make in MULTI_WORD_MAKES:
        if low.startswith(make) or f" {make}" in low:
            idx = low.find(make)
            rest = cleaned[idx + len(make):].strip()
            return _title(make), _first_words(rest, 2)

    for make in SINGLE_WORD_MAKES:
        if re.search(rf'\b{re.escape(make)}\b', low):
            idx = low.find(make)
            rest = cleaned[idx + len(make):].strip()
            return _title(make), _first_words(rest, 2)

    tokens = cleaned.split()
    if len(tokens) >= 2:
        return tokens[0], tokens[1]
    return "", ""


def _first_words(text: str, n: int) -> str:
    return " ".join(text.split()[:n]).strip()


_UPPER_MAKES = {"bmw", "vw", "mg"}


def _title(make: str) -> str:
    words = make.split()
    return " ".join(w.upper() if w.lower() in _UPPER_MAKES else w.capitalize() for w in words)


def demo() -> None:
    """Self-check. Run: python -m src.scrapers.title_parser"""
    cases = [
        ("Toyota Camry 2020 GCC 50,000 km", ("Toyota", "Camry")),
        ("Land Rover Range Rover Vogue 2019", ("Land Rover", "Range Rover")),
        ("2018 Nissan Patrol Platinum GCC", ("Nissan", "Patrol Platinum")),
        ("Mercedes Benz C200 2021", ("Mercedes Benz", "C200")),
        ("BMW 320i 2017 | 80,000 km", ("BMW", "320i")),
        ("Lexus LX 570 2020 GCC Spec", ("Lexus", "LX 570")),
    ]
    for title, expected in cases:
        got = extract_make_model(title)
        assert got == expected, f"{title!r}: expected {expected}, got {got}"
    assert extract_make_model("") == ("", "")
    print(f"title_parser: {len(cases)} cases passed")


if __name__ == "__main__":
    demo()
