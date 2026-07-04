import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, func
from src.db.base import UniversalUUID
from sqlalchemy.orm import relationship
from src.db.base import Base, LineageMixin

class ListingSnapshot(Base, LineageMixin):
    __tablename__ = "listing_snapshots"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    listing_id = Column(UniversalUUID, ForeignKey("listings.id"), nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    asking_price = Column(Float, nullable=False)
    original_currency = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    days_on_market = Column(Integer, nullable=True)
    price_change_pct = Column(Float, nullable=True)

    listing = relationship("Listing", back_populates="snapshots")
