"""Saved valuations — users can bookmark and track valuations."""
import uuid
from sqlalchemy import Column, Text, DateTime, func, Float, Integer, ForeignKey
from src.db.base import Base, UniversalUUID


class SavedValuation(Base):
    __tablename__ = "saved_valuations"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UniversalUUID, ForeignKey("user_accounts.id"), nullable=False)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=True)
    spec = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    estimated_price = Column(Float, nullable=True)
    confidence = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
