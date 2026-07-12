"""Canonical value catalogs — comprehensive alias maps for every vehicle field."""

# ---------------------------------------------------------------------------
# Make aliases (case-insensitive matching against keys)
# ---------------------------------------------------------------------------
MAKE_ALIASES: dict[str, str] = {
    "toyota": "Toyota", "toyota motors": "Toyota", "toyota uae": "Toyota",
    "nissan": "Nissan",
    "honda": "Honda",
    "hyundai": "Hyundai",
    "kia": "Kia",
    "ford": "Ford",
    "chevrolet": "Chevrolet", "chevy": "Chevrolet",
    "bmw": "BMW",
    "mercedes": "Mercedes-Benz", "mercedes benz": "Mercedes-Benz", "mercedes-benz": "Mercedes-Benz",
    "audi": "Audi",
    "lexus": "Lexus",
    "mazda": "Mazda",
    "mitsubishi": "Mitsubishi",
    "land rover": "Land Rover", "range rover": "Land Rover",
    "porsche": "Porsche",
    "volkswagen": "Volkswagen", "vw": "Volkswagen",
    "gmc": "GMC",
    "cadillac": "Cadillac",
    "jeep": "Jeep",
    "dodge": "Dodge",
    "chrysler": "Chrysler",
    "infiniti": "Infiniti",
    "jaguar": "Jaguar",
    "volvo": "Volvo",
    "subaru": "Subaru",
    "suzuki": "Suzuki",
    "renault": "Renault",
    "peugeot": "Peugeot",
    "mg": "MG",
    "tesla": "Tesla",
    "genesis": "Genesis",
    "lincoln": "Lincoln",
    "bentley": "Bentley",
    "rolls royce": "Rolls-Royce", "rolls-royce": "Rolls-Royce",
    "maserati": "Maserati",
    "ferrari": "Ferrari",
    "lamborghini": "Lamborghini",
    "aston martin": "Aston Martin",
    "alfa romeo": "Alfa Romeo",
    "fiat": "Fiat",
    "mini": "Mini",
    "skoda": "Skoda",
    "seat": "Seat",
    "citroen": "Citroen",
    "opel": "Opel",
    "chery": "Chery",
    "geely": "Geely",
    "jac": "JAC",
    "changan": "Changan",
    "gac": "GAC",
    "jetour": "Jetour",
    "byd": "BYD",
    "great wall": "Great Wall",
    "haval": "Haval",
    "isuzu": "Isuzu",
    "maxus": "Maxus",
    "dfsk": "DFSK",
}

# ---------------------------------------------------------------------------
# Model aliases (case-insensitive, per make)
# ---------------------------------------------------------------------------
MODEL_ALIASES: dict[str, dict[str, str]] = {
    "Toyota": {
        "land cruiser": "Land Cruiser", "landcruiser": "Land Cruiser",
        "lc": "Land Cruiser", "lc200": "Land Cruiser", "lc300": "Land Cruiser",
        "prado": "Prado", "land cruiser prado": "Prado",
        "camry": "Camry", "corolla": "Corolla",
        "hilux": "Hilux", "fortuner": "Fortuner",
        "rav4": "RAV4", "rav 4": "RAV4",
        "yaris": "Yaris", "avalon": "Avalon",
        "c-hr": "C-HR", "chr": "C-HR",
        "supra": "Supra", "gr86": "GR86", "86": "GR86",
        "fj cruiser": "FJ Cruiser", "fj": "FJ Cruiser",
        "4runner": "4Runner", "4 runner": "4Runner",
        "sequoia": "Sequoia", "tundra": "Tundra", "tacoma": "Tacoma",
        "innova": "Innova", "rush": "Rush", "urban cruiser": "Urban Cruiser",
        "coaster": "Coaster", "hiace": "HiAce",
    },
    "Nissan": {
        "patrol": "Patrol", "patrol safari": "Patrol", "patrol super safari": "Patrol",
        "sunny": "Sunny", "altima": "Altima", "maxima": "Maxima",
        "x-trail": "X-Trail", "xtrail": "X-Trail", "x trail": "X-Trail",
        "kicks": "Kicks", "juke": "Juke",
        "pathfinder": "Pathfinder", "armada": "Armada",
        "navara": "Navara", "titan": "Titan",
        "sentra": "Sentra", "versa": "Versa",
        "gt-r": "GT-R", "gtr": "GT-R", "z": "Z",
        "ariya": "Ariya", "leaf": "Leaf",
    },
    "Honda": {
        "accord": "Accord", "civic": "Civic",
        "cr-v": "CR-V", "crv": "CR-V", "cr v": "CR-V",
        "hr-v": "HR-V", "hrv": "HR-V",
        "pilot": "Pilot", "odyssey": "Odyssey",
        "city": "City", "jazz": "Jazz", "fit": "Fit",
        "ridgeline": "Ridgeline",
    },
    "Hyundai": {
        "tucson": "Tucson", "santa fe": "Santa Fe", "santafe": "Santa Fe",
        "elantra": "Elantra", "sonata": "Sonata",
        "accent": "Accent", "venue": "Venue", "kona": "Kona",
        "palisade": "Palisade", "creta": "Creta",
        "ioniq": "Ioniq", "ioniq 5": "Ioniq 5", "ioniq 6": "Ioniq 6",
    },
    "Kia": {
        "sportage": "Sportage", "sorento": "Sorento",
        "telluride": "Telluride", "carnival": "Carnival",
        "seltos": "Seltos", "sonet": "Sonet",
        "k5": "K5", "k8": "K8", "ev6": "EV6", "ev9": "EV9",
        "picanto": "Picanto", "rio": "Rio", "peg": "Pegas",
    },
    "Mitsubishi": {
        "pajero": "Pajero", "lancer": "Lancer",
        "outlander": "Outlander", "asx": "ASX",
        "eclipse cross": "Eclipse Cross", "attrage": "Attrage",
        "montero": "Montero Sport", "montero sport": "Montero Sport",
    },
    "Mazda": {
        "cx-5": "CX-5", "cx5": "CX-5", "cx 5": "CX-5",
        "cx-9": "CX-9", "cx9": "CX-9",
        "cx-30": "CX-30", "cx30": "CX-30",
        "mazda3": "Mazda3", "mazda 3": "Mazda3",
        "mazda6": "Mazda6", "mazda 6": "Mazda6",
        "mx-5": "MX-5", "mx5": "MX-5", "miata": "MX-5",
    },
}

# Fallback: title-case the model name
def _default_model_normalize(raw: str) -> str:
    return raw.strip().title()

# ---------------------------------------------------------------------------
# Transmission aliases
# ---------------------------------------------------------------------------
TRANSMISSION_ALIASES: dict[str, str] = {
    "automatic": "automatic", "auto": "automatic", "at": "automatic",
    "a/t": "automatic", "atm": "automatic",
    "manual": "manual", "mt": "manual", "m/t": "manual",
    "cvt": "cvt", "continuously variable": "cvt",
    "dct": "dct", "dual clutch": "dct", "dual-clutch": "dct",
    "dsg": "dct", "pdk": "dct",
    "tiptronic": "automatic", "steptronic": "automatic",
}

# ---------------------------------------------------------------------------
# Fuel type aliases
# ---------------------------------------------------------------------------
FUEL_ALIASES: dict[str, str] = {
    "petrol": "petrol", "gasoline": "petrol", "gas": "petrol",
    "بنزين": "petrol", "regular": "petrol", "super": "petrol",
    "diesel": "diesel", "ديزل": "diesel",
    "hybrid": "hybrid", "hybrid petrol": "hybrid", "petrol hybrid": "hybrid",
    "electric": "electric", "ev": "electric", "كهرباء": "electric",
    "plugin hybrid": "plugin_hybrid", "plug-in hybrid": "plugin_hybrid",
    "phev": "plugin_hybrid",
    "lpg": "lpg", "gas lpg": "lpg",
    "hydrogen": "other", "cng": "other",
}

# ---------------------------------------------------------------------------
# Body type aliases
# ---------------------------------------------------------------------------
BODY_ALIASES: dict[str, str] = {
    "suv": "suv", "sport utility": "suv", "4x4": "suv", "4wd": "suv",
    "crossover": "suv", "cuv": "suv",
    "sedan": "sedan", "saloon": "sedan",
    "hatchback": "hatchback", "hatch": "hatchback",
    "coupe": "coupe", "coupe": "coupe",
    "convertible": "convertible", "cabriolet": "convertible", "cabrio": "convertible",
    "wagon": "wagon", "estate": "wagon", "station wagon": "wagon",
    "pickup": "pickup", "pick-up": "pickup", "truck": "pickup",
    "minivan": "minivan", "mpv": "minivan",
    "van": "van", "bus": "van",
}

# ---------------------------------------------------------------------------
# Color aliases
# ---------------------------------------------------------------------------
COLOR_ALIASES: dict[str, str] = {
    "white": "White", "pearl white": "White", "bright white": "White",
    "super white": "White", "ivory": "White", "cream": "White",
    "أبيض": "White",
    "black": "Black", "midnight black": "Black", "jet black": "Black",
    "onyx": "Black", "أسود": "Black",
    "grey": "Grey", "gray": "Grey", "silver": "Silver",
    "graphite": "Grey", "charcoal": "Grey", "titanium": "Silver",
    "رمادي": "Grey", "فضي": "Silver",
    "blue": "Blue", "navy blue": "Blue", "dark blue": "Blue",
    "light blue": "Blue", "metallic blue": "Blue", "أزرق": "Blue",
    "red": "Red", "crimson": "Red", "burgundy": "Red", "maroon": "Red",
    "أحمر": "Red",
    "green": "Green", "dark green": "Green", "أخضر": "Green",
    "brown": "Brown", "bronze": "Brown", "copper": "Brown", "بني": "Brown",
    "gold": "Gold", "champagne": "Gold", "ذهبي": "Gold",
    "yellow": "Yellow", "أصفر": "Yellow",
    "orange": "Orange", "برتقالي": "Orange",
    "beige": "Beige", "sand": "Beige", "tan": "Beige", "بيج": "Beige",
    "purple": "Purple", "بنفسجي": "Purple",
}

# ---------------------------------------------------------------------------
# Specification aliases
# ---------------------------------------------------------------------------
SPEC_ALIASES: dict[str, str] = {
    "gcc": "GCC", "gcc spec": "GCC", "gcc specs": "GCC",
    "gulf spec": "GCC", "gulf": "GCC", "gulf specification": "GCC",
    "خليجي": "GCC", "خليجية": "GCC", "مواصفات خليجية": "GCC",
    "us": "US", "usa": "US", "american": "US", "american spec": "US",
    "us spec": "US", "us specs": "US", "امريكي": "US",
    "japan": "Japan", "japanese": "Japan", "japan spec": "Japan",
    "ياباني": "Japan",
    "european": "European", "europe": "European", "euro": "European",
    "european spec": "European", "اوروبي": "European",
    "canadian": "Other", "canada": "Other", "korean": "Other",
    "china": "Other", "chinese": "Other",
}

# ---------------------------------------------------------------------------
# City aliases (GCC)
# ---------------------------------------------------------------------------
CITY_ALIASES: dict[str, str] = {
    "dubai": "Dubai", "dubai city": "Dubai", "دبي": "Dubai",
    "abu dhabi": "Abu Dhabi", "ابوظبي": "Abu Dhabi",
    "sharjah": "Sharjah", "الشارقة": "Sharjah",
    "al ain": "Al Ain", "العين": "Al Ain",
    "ajman": "Ajman", "عجمان": "Ajman",
    "ras al khaimah": "Ras Al Khaimah", "rak": "Ras Al Khaimah",
    "fujairah": "Fujairah", "الفجيرة": "Fujairah",
    "umm al quwain": "Umm Al Quwain", "uaq": "Umm Al Quwain",
    "riyadh": "Riyadh", "الرياض": "Riyadh",
    "jeddah": "Jeddah", "جدة": "Jeddah",
    "dammam": "Dammam", "الدمام": "Dammam",
    "mecca": "Mecca", "makkah": "Mecca", "مكة": "Mecca",
    "medina": "Medina", "madinah": "Medina", "المدينة": "Medina",
    "khobar": "Khobar", "الخبر": "Khobar",
    "kuwait city": "Kuwait City", "الكويت": "Kuwait City",
    "doha": "Doha", "الدوحة": "Doha",
    "muscat": "Muscat", "مسقط": "Muscat",
    "manama": "Manama", "المنامة": "Manama",
}

# ---------------------------------------------------------------------------
# Mileage unit
# ---------------------------------------------------------------------------
MILEAGE_KM_PER_MILE = 1.60934
