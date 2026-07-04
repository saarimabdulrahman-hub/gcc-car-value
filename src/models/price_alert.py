"""Price alerts — notify users when market prices move."""
import uuid
from sqlalchemy import Column, Text, DateTime, func, Float, Integer, Boolean, ForeignKey
from src.db.base import Base, UniversalUUID


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UniversalUUID, ForeignKey("user_accounts.id"), nullable=False)
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year_min = Column(Integer, nullable=True)
    year_max = Column(Integer, nullable=True)
    country = Column(Text, nullable=True)
    target_price = Column(Float, nullable=True)  # alert when median drops below this
    active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
