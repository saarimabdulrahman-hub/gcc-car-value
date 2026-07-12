import uuid
from sqlalchemy import Column, Integer, Text, DateTime, func, UniqueConstraint
from src.db.base import UniversalUUID
from src.db.base import Base

class CanonicalVehicle(Base):
    __tablename__ = "canonical_vehicles"
    __table_args__ = (
        UniqueConstraint("make", "model", "year", "generation",
                         name="uq_canonical_vehicles_make_model_year_gen"),
    )

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    generation = Column(Text, nullable=True)
    body_type = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
