"""CanonicalListing — the single source of truth for every vehicle listing."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from schema.vehicle import Vehicle
from schema.pricing import Pricing
from schema.location import Location
from schema.seller import Seller
from schema.images import Images
from schema.history import VehicleHistory


@dataclass
class CanonicalListing:
    """Canonical vehicle listing — marketplace-agnostic.

    Every marketplace scraper outputs this schema. Every downstream system
    (normalization, ML, valuation, API) consumes this schema. Marketplace-
    specific field names never appear outside the scraper layer.
    """
    # Identity
    listing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    marketplace: str = ""                    # e.g., "dubizzle_uae"
    marketplace_listing_id: str = ""         # Original ID from marketplace
    listing_url: str = ""
    schema_version: int = 1

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = ""
    scraped_at: str = ""

    # Status
    status: str = "active"                   # active, sold, expired, delisted, pending

    # Sub-models
    vehicle: Vehicle = field(default_factory=Vehicle)
    pricing: Pricing = field(default_factory=Pricing)
    location: Location = field(default_factory=Location)
    seller: Seller = field(default_factory=Seller)
    images: Images = field(default_factory=Images)
    history: VehicleHistory = field(default_factory=VehicleHistory)

    # Extra
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a flat dict (for JSON/DB storage)."""
        return {
            "listing_id": self.listing_id,
            "marketplace": self.marketplace,
            "marketplace_listing_id": self.marketplace_listing_id,
            "listing_url": self.listing_url,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "scraped_at": self.scraped_at,
            "status": self.status,
            # Vehicle
            "make": self.vehicle.make,
            "model": self.vehicle.model,
            "trim": self.vehicle.trim,
            "generation": self.vehicle.generation,
            "year": self.vehicle.year,
            "body_type": self.vehicle.body_type,
            "fuel_type": self.vehicle.fuel_type,
            "transmission": self.vehicle.transmission,
            "drivetrain": self.vehicle.drivetrain,
            "engine_size": self.vehicle.engine_size,
            "horsepower": self.vehicle.horsepower,
            "doors": self.vehicle.doors,
            "seats": self.vehicle.seats,
            "color": self.vehicle.color,
            "interior_color": self.vehicle.interior_color,
            "vin": self.vehicle.vin,
            "registration_country": self.vehicle.registration_country,
            "specification": self.vehicle.specification,
            "mileage_km": self.vehicle.mileage_km,
            "mileage_unit": self.vehicle.mileage_unit,
            "odometer_verified": self.vehicle.odometer_verified,
            # Pricing
            "price_amount": self.pricing.amount,
            "price_currency": self.pricing.currency,
            "price_negotiable": self.pricing.negotiable,
            "tax_included": self.pricing.tax_included,
            "finance_available": self.pricing.finance_available,
            # Location
            "country": self.location.country,
            "state": self.location.state,
            "city": self.location.city,
            "district": self.location.district,
            "latitude": self.location.latitude,
            "longitude": self.location.longitude,
            # Seller
            "seller_type": self.seller.seller_type,
            "seller_name": self.seller.seller_name,
            "dealer_name": self.seller.dealer_name,
            "dealer_id": self.seller.dealer_id,
            "seller_verified": self.seller.verified,
            "seller_rating": self.seller.rating,
            "phone_available": self.seller.phone_available,
            "chat_available": self.seller.chat_available,
            # Images
            "cover_image": self.images.cover_image,
            "image_count": self.images.image_count,
            "video_available": self.images.video_available,
            # History
            "accident_history": self.history.accident_history,
            "service_history": self.history.service_history,
            "owners": self.history.owners,
            "warranty": self.history.warranty,
            "export_status": self.history.export_status,
            "import_status": self.history.import_status,
            # Extra
            "metadata": self.metadata,
        }
