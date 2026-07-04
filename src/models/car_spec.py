import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class CarSpec(Base):
    __tablename__ = "car_specs"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    generation = Column(Text, nullable=True)
    year_start = Column(Integer, nullable=True)
    year_end = Column(Integer, nullable=True)
    trim = Column(Text, nullable=True)
    engine_options = Column(UniversalJSONB, nullable=True)
    transmission_options = Column(UniversalJSONB, nullable=True)
    drivetrain = Column(Text, nullable=True)
    fuel_economy_combined = Column(Float, nullable=True)
    fuel_tank_capacity = Column(Float, nullable=True)
    seating_capacity = Column(Integer, nullable=True)
    cargo_volume_L = Column(Float, nullable=True)
    safety_rating = Column(Text, nullable=True)
    warranty_years = Column(Integer, nullable=True)
    warranty_km = Column(Integer, nullable=True)
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
