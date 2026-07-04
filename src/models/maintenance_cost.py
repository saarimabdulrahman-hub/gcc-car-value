import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class MaintenanceCost(Base):
    __tablename__ = "maintenance_costs"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    generation = Column(Text, nullable=True)
    service_interval_km = Column(Integer, nullable=True)
    minor_service_cost = Column(Float, nullable=True)
    major_service_cost = Column(Float, nullable=True)
    common_repair_costs = Column(UniversalJSONB, nullable=True)
    annual_insurance_estimate = Column(Float, nullable=True)
    source = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
