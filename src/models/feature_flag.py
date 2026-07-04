import uuid
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB, Base

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    flag_name = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=False)
    rollout_pct = Column(Integer, default=100)
    target_users = Column(UniversalJSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
