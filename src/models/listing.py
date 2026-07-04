import uuid
from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, ForeignKey, func
from src.db.base import UniversalUUID, UniversalJSONB
from sqlalchemy.orm import relationship
from src.db.base import Base, LineageMixin

class Listing(Base, LineageMixin):
    __tablename__ = "listings"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    canonical_vehicle_id = Column(UniversalUUID, ForeignKey("canonical_vehicles.id"), nullable=True)

    source = Column(Text, nullable=False)
    external_id = Column(Text, nullable=False)
    url = Column(Text, nullable=True)

    first_seen_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text, nullable=False)
    delisted_at = Column(DateTime(timezone=True), nullable=True)
    delisting_confidence = Column(Float, nullable=True)

    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    trim = Column(Text, nullable=True)
    spec = Column(Text, nullable=True)
    body_type = Column(Text, nullable=True)
    transmission = Column(Text, nullable=True)
    fuel_type = Column(Text, nullable=True)
    engine_size = Column(Float, nullable=True)
    color = Column(Text, nullable=True)
    doors = Column(Integer, nullable=True)
    cylinders = Column(Integer, nullable=True)

    original_price = Column(Float, nullable=False)
    original_currency = Column(Text, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    exchange_timestamp = Column(DateTime(timezone=True), nullable=False)
    normalized_price_aed = Column(Float, nullable=False)
    price_history = Column(UniversalJSONB, default=list)

    mileage_km = Column(Integer, nullable=True)
    warranty = Column(Boolean, nullable=True)
    service_history = Column(Boolean, nullable=True)
    seller_type = Column(Text, nullable=True)

    city = Column(Text, nullable=False)
    country = Column(Text, nullable=False)

    quality_score = Column(Integer, nullable=False, default=0)
    quality_flags = Column(UniversalJSONB, default=list)

    raw_data_s3_key = Column(Text, nullable=True)

    snapshots = relationship("ListingSnapshot", back_populates="listing")
