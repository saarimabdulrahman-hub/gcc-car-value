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

# Trailing tokens that are trim levels, not part of the model name.
# Deliberately excludes ambiguous words that are real model tokens:
# "sport" (Range Rover Sport), "limited", "base", "lx"/"gx" (Lexus models),
# and anything numeric ("LX 570", "320i").
# ALSO excludes "gt"/"gts" (Bentley Continental GT, Mercedes-AMG GT are real
# GCC-market model names) and "ex" (Infiniti EX nameplate).
# ponytail: a curated trim list caps out here; a real model catalogue is the
# proper fix if extraction accuracy ever becomes the bottleneck.
TRIM_WORDS = {
    "se", "le", "xle", "xse", "exl", "sr", "srt", "glx", "gxr", "vxr",
    "platinum", "signature", "ultimate", "touring",
    "premium", "luxury", "prestige", "diamond", "titanium",
    "v6", "v8", "turbo", "awd", "4wd", "4x4", "2dr", "4dr",
    "standard", "comfort",
}

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
    """Take up to n words, dropping a trailing trim token.

    "Patrol Platinum" -> "Patrol"      (Platinum is a trim)
    "Land Cruiser"    -> "Land Cruiser" (Cruiser is part of the model)
    "LX 570"          -> "LX 570"       (570 is part of the model)
    """
    words = text.split()[:n]
    if len(words) == 2 and words[1].lower() in TRIM_WORDS:
        words = words[:1]
    return " ".join(words).strip()


_UPPER_MAKES = {"bmw", "vw", "mg"}


def _title(make: str) -> str:
    if make.lower() == "mercedes benz":
        return "Mercedes-Benz"
    words = make.split()
    return " ".join(w.upper() if w.lower() in _UPPER_MAKES else w.capitalize() for w in words)


def demo() -> None:
    """Self-check. Run: python -m src.scrapers.title_parser"""
    cases = [
        ("Toyota Camry 2020 GCC 50,000 km", ("Toyota", "Camry")),
        ("Land Rover Range Rover Vogue 2019", ("Land Rover", "Range Rover")),
        ("2018 Nissan Patrol Platinum GCC", ("Nissan", "Patrol")),
        ("Mercedes Benz C200 2021", ("Mercedes-Benz", "C200")),
        ("BMW 320i 2017 | 80,000 km", ("BMW", "320i")),
        ("Lexus LX 570 2020 GCC Spec", ("Lexus", "LX 570")),
        ("Toyota Camry SE 2021", ("Toyota", "Camry")),
        ("Nissan Altima SR 2019", ("Nissan", "Altima")),
        ("Toyota Land Cruiser 2019 GCC", ("Toyota", "Land Cruiser")),
        ("Mitsubishi Pajero 2020", ("Mitsubishi", "Pajero")),
    ]
    for title, expected in cases:
        got = extract_make_model(title)
        assert got == expected, f"{title!r}: expected {expected}, got {got}"
    assert extract_make_model("") == ("", "")
    print(f"title_parser: {len(cases)} cases passed")


if __name__ == "__main__":
    demo()
