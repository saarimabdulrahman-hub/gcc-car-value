import uuid
from sqlalchemy import Column, Integer, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class DeadLetter(Base):
    __tablename__ = "dead_letter"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    source = Column(Text, nullable=False)
    external_id = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=False)
    raw_data = Column(UniversalJSONB, nullable=False)
    quality_score = Column(Integer, nullable=True)
    pipeline_run_id = Column(UniversalUUID, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
