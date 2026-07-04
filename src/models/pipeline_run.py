import uuid
from sqlalchemy import Column, Integer, Float, Text, Boolean, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    run_id = Column(UniversalUUID, nullable=False, unique=True, default=uuid.uuid4)
    source = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    pages_crawled = Column(Integer, default=0)
    records_ingested = Column(Integer, default=0)
    records_new = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_promoted = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    quality_score_p50 = Column(Float, nullable=True)
    quality_score_p90 = Column(Float, nullable=True)
    quality_score_mean = Column(Float, nullable=True)
    error_count = Column(Integer, default=0)
    errors = Column(UniversalJSONB, default=list)
    success = Column(Boolean, default=False)
    parser_version = Column(Text, nullable=True)
    normalizer_version = Column(Text, nullable=True)
    git_commit = Column(Text, nullable=True)
