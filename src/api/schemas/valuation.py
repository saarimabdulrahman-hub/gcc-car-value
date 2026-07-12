"""Pydantic schemas for valuation request/response."""
from pydantic import BaseModel, Field
from typing import Optional


class ValuationRequest(BaseModel):
    make: str = Field(..., description="Vehicle make, e.g. Toyota")
    model: str = Field(..., description="Vehicle model, e.g. Land Cruiser")
    year: int = Field(..., ge=1990, le=2027, description="Manufacturing year")
    mileage_km: int | None = Field(None, ge=0, le=1_000_000, description="Odometer in km")
    spec: str | None = Field(None, description="GCC, US, Japan, European")
    trim: str | None = Field(None, description="Trim level, e.g. VXR")
    city: str | None = Field(None, description="City, e.g. Dubai")
    country: str | None = Field(None, description="Country code: AE, SA, QA, KW, BH, OM")
    asking_price: float | None = Field(None, gt=0, description="Price to evaluate for deal indicator")


class CompSummary(BaseModel):
    price_aed: float
    year: int
    mileage_km: int | None
    spec: str | None
    city: str
    country: str
    status: str
    found_on: str = Field(..., description="Human-readable: 'Found on Dubizzle UAE, Dubai'")
    platform: str
    relevance_score: float


class Adjustment(BaseModel):
    reason: str
    amount: float
    detail: str


class Knowledge(BaseModel):
    generation: str | None = None
    known_issues: list[str] = []
    annual_maintenance_estimate: str | None = None
    market_liquidity: str | None = None


class ValuationResponse(BaseModel):
    estimate: float
    price_low: float
    price_high: float
    confidence: str
    comp_count: int
    segment_median: float
    comps: list[CompSummary]
    adjustments: list[Adjustment]
    confidence_interval_80: tuple[float, float] | None = None
    knowledge: Knowledge | None = None
    deal_indicator: str | None = None  # great_deal, fair_deal, above_market, or None
    deal_description: str | None = None
    # ML integration fields
    prediction_source: str = "statistical"  # "statistical" | "ml" | "ensemble"
    model_version: str | None = None        # e.g. "lightgbm_v20260712_1400"
    fallback_used: bool = False             # True if ML was tried but fell back
