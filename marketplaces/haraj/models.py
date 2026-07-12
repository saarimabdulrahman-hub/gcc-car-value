"""Haraj data models."""
from dataclasses import dataclass, field

@dataclass
class HarajListing:
    listing_id: str = ""; url: str = ""; title: str = ""; make: str = ""; model: str = ""
    year: int = 0; price: float = 0.0; currency: str = "SAR"; mileage_km: int = 0
    spec: str = ""; transmission: str = ""; fuel_type: str = ""
    body_type: str = ""; color: str = ""; location: str = ""; seller_name: str = ""
    description: str = ""; images: list[str] = field(default_factory=list)
