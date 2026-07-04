import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    trained_at = Column(DateTime(timezone=True), nullable=False)
    model_type = Column(Text, nullable=False)
    model_path = Column(Text, nullable=True)
    model_name = Column(Text, nullable=False)
    mae = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    training_rows = Column(Integer, nullable=True)
    holdout_rows = Column(Integer, nullable=True)
    training_dataset_hash = Column(Text, nullable=True)
    feature_version = Column(Text, nullable=True)
    git_commit = Column(Text, nullable=True)
    hyperparameters = Column(UniversalJSONB, nullable=True)
    training_config = Column(UniversalJSONB, nullable=True)
    features_used = Column(UniversalJSONB, nullable=True)
    status = Column(Text, nullable=False, default="training")
    shadow_started_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Text, nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    rollback_reason = Column(Text, nullable=True)
    shadow_query_count = Column(Integer, nullable=True)
    shadow_mae = Column(Float, nullable=True)
    shadow_vs_active_pct = Column(Float, nullable=True)
