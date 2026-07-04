import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID
from src.db.base import Base

class ModelRating(Base):
    __tablename__ = "model_ratings"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    generation = Column(Text, nullable=True)
    reliability = Column(Float, nullable=True)
    comfort = Column(Float, nullable=True)
    performance = Column(Float, nullable=True)
    fuel_economy = Column(Float, nullable=True)
    offroad_capability = Column(Float, nullable=True)
    resale_value = Column(Float, nullable=True)
    overall = Column(Float, nullable=True)
    rating_count = Column(Integer, default=0)
    source = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
