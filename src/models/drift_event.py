import uuid
from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB, UniversalDATERANGE
from src.db.base import Base

class DriftEvent(Base):
    __tablename__ = "drift_events"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    drift_type = Column(Text, nullable=False)
    feature_name = Column(Text, nullable=True)
    psi_value = Column(Float, nullable=True)
    baseline_period = Column(UniversalDATERANGE, nullable=True)
    current_period = Column(UniversalDATERANGE, nullable=True)
    threshold_exceeded = Column(Boolean, nullable=True)
    details = Column(UniversalJSONB, nullable=True)
    acknowledged = Column(Boolean, default=False)
