import uuid
from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, func
from src.db.base import UniversalUUID
from src.db.base import Base

class CarIssue(Base):
    __tablename__ = "car_issues"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    generation = Column(Text, nullable=True)
    year_start = Column(Integer, nullable=True)
    year_end = Column(Integer, nullable=True)
    issue_title = Column(Text, nullable=False)
    issue_description = Column(Text, nullable=True)
    severity = Column(Text, nullable=True)
    typical_mileage_km = Column(Integer, nullable=True)
    repair_cost_estimate = Column(Float, nullable=True)
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False)
    confirmed_by_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
