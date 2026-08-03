import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text, func

from src.db.base import Base, UniversalJSONB, UniversalUUID


class DeadLetter(Base):
    __tablename__ = "dead_letter"
    __table_args__ = (
        Index("ix_dead_letter_source_external_id", "source", "external_id"),
    )

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    source = Column(Text, nullable=False)
    external_id = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=False)
    raw_data = Column(UniversalJSONB, nullable=False)
    quality_score = Column(Integer, nullable=True)
    pipeline_run_id = Column(UniversalUUID, ForeignKey("pipeline_runs.run_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
