import uuid
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, func
from src.db.base import UniversalUUID, UniversalJSONB
from src.db.base import Base

class ScraperHealth(Base):
    __tablename__ = "scraper_health"
    id = Column(UniversalUUID, primary_key=True, default=uuid.uuid4)
    pipeline_run_id = Column(UniversalUUID, ForeignKey("pipeline_runs.run_id", ondelete="SET NULL"), nullable=True)
    source = Column(Text, nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    pages_crawled = Column(Integer, nullable=True)
    listings_found = Column(Integer, nullable=True)
    listings_new = Column(Integer, nullable=True)
    listings_updated = Column(Integer, nullable=True)
    price_extracted_pct = Column(Float, nullable=True)
    year_extracted_pct = Column(Float, nullable=True)
    mileage_extracted_pct = Column(Float, nullable=True)
    spec_extracted_pct = Column(Float, nullable=True)
    trim_extracted_pct = Column(Float, nullable=True)
    city_extracted_pct = Column(Float, nullable=True)
    body_type_extracted_pct = Column(Float, nullable=True)
    transmission_extracted_pct = Column(Float, nullable=True)
    parse_success_rate = Column(Float, nullable=True)
    avg_parse_time_ms = Column(Float, nullable=True)
    html_structure_hash = Column(Text, nullable=True)
    selector_failures = Column(UniversalJSONB, nullable=True)
    unexpected_layouts = Column(Integer, nullable=True)
    scraper_confidence = Column(Float, nullable=True)
    errors = Column(UniversalJSONB, nullable=True)
