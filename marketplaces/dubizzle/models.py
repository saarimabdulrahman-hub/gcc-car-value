"""Dubizzle-specific data models."""

from dataclasses import dataclass, field


@dataclass
class DubizzleListing:
    """Raw extracted listing before canonicalization."""
    listing_id: str = ""
    url: str = ""
    title: str = ""
    make: str = ""
    model: str = ""
    year: int = 0
    price: float = 0.0
    currency: str = "AED"
    mileage_km: int = 0
    spec: str = ""
    transmission: str = ""
    fuel_type: str = ""
    body_type: str = ""
    color: str = ""
    location: str = ""
    seller_name: str = ""
    description: str = ""
    images: list[str] = field(default_factory=list)
