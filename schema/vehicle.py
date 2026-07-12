"""Vehicle sub-model."""

from dataclasses import dataclass, field
from schema.enums import FuelType, Transmission, BodyType, DriveTrain, Specification


@dataclass
class Vehicle:
    """Vehicle identity and specifications."""
    make: str = ""
    model: str = ""
    trim: str = ""
    generation: str = ""
    year: int = 0
    body_type: str = ""
    fuel_type: str = ""
    transmission: str = ""
    drivetrain: str = ""
    engine_size: float = 0.0        # Liters
    horsepower: int = 0
    doors: int = 0
    seats: int = 0
    color: str = ""
    interior_color: str = ""
    vin: str = ""                   # Optional — not always available
    registration_country: str = ""
    specification: str = ""         # GCC, US, Japan, European
    mileage_km: int = 0
    mileage_unit: str = "km"
    odometer_verified: bool = False
