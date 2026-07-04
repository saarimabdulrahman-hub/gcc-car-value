import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class ValuationQuery(Base):
    __tablename__ = "valuation_queries"

    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    cache_key = Column(Text, nullable=False, unique=True)
    queried_at = Column(DateTime(timezone=True), server_default=func.now())
    make = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=True)
    spec = Column(Text, nullable=True)
    trim = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    estimated_price = Column(Float, nullable=True)
    price_low = Column(Float, nullable=True)
    price_high = Column(Float, nullable=True)
    comp_count = Column(Integer, nullable=True)
    confidence = Column(Text, nullable=True)
    model_version = Column(Text, nullable=True)
    model_type = Column(Text, nullable=True)
    shap_values = Column(UniversalJSONB, nullable=True)
    feature_importance = Column(UniversalJSONB, nullable=True)
    adjustments = Column(UniversalJSONB, nullable=True)
    response_ms = Column(Integer, nullable=True)
    api_version = Column(Text, nullable=True)
    user_id = Column(Text, nullable=True)
    ip_hash = Column(Text, nullable=True)
