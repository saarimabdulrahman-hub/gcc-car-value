"""Location sub-model."""

from dataclasses import dataclass


@dataclass
class Location:
    """Geographic location of the listing."""
    country: str = "AE"
    state: str = ""
    city: str = ""
    district: str = ""
    latitude: float | None = None
    longitude: float | None = None
