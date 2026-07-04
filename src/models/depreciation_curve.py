import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class DepreciationCurve(Base):
    __tablename__ = "depreciation_curves"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    generation = Column(Text, nullable=True)
    msrp_aed = Column(Float, nullable=True)
    residual_pct_year = Column(UniversalJSONB, nullable=False)
    computed_from_rows = Column(Integer, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
