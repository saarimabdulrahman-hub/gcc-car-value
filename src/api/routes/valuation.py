import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, limiter
from src.api.schemas.valuation import ValuationRequest, ValuationResponse, CompSummary, Adjustment, Knowledge
from src.engine.statistical import valuate, ValuationResult
import structlog

router = APIRouter()
logger = structlog.get_logger()


def _compute_cache_key(req: ValuationRequest) -> str:
    raw = (
        f"{req.make}|{req.model}|{req.year}|"
        f"{req.mileage_km or 'NA'}|{req.spec or 'NA'}|"
        f"{req.trim or 'NA'}|{req.city or 'NA'}|"
        f"{req.country or 'NA'}|"
        f"{datetime.now().strftime('%Y-%m-%d')}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def _compute_deal_indicator(asking_price: float | None, result: ValuationResult) -> tuple[str | None, str | None]:
    """Compute Good Deal / Fair Deal / Above Market indicator from spec Section 6.3."""
    if asking_price is None or result.confidence == "insufficient" or result.confidence == "low":
        return None, None

    if asking_price < result.price_low:
        return "great_deal", f"This car is priced below the market range ({asking_price:,.0f} vs {result.price_low:,.0f}–{result.price_high:,.0f} AED)."
    elif asking_price <= result.price_high:
        return "fair_deal", f"This car is priced within the normal market range."
    else:
        return "above_market", f"This car is priced above the market range. Consider negotiating."


@router.post("/valuate", response_model=ValuationResponse)
@limiter.limit("10/minute")
async def valuate_vehicle(
    request: ValuationRequest,
    db: AsyncSession = Depends(get_db),
):
    cache_key = _compute_cache_key(request)

    # Check cache
    from sqlalchemy import select
    from src.models.valuation_query import ValuationQuery
    stmt = select(ValuationQuery).where(ValuationQuery.cache_key == cache_key)
    stmt = stmt.limit(1)
    result = await db.execute(stmt)
    cached = result.scalar_one_or_none()

    if cached and cached.estimated_price is not None:
        logger.info("valuation_cache_hit", cache_key=cache_key)
        return _build_response_from_cache(cached)

    # Compute valuation
    valuation = await valuate(
        db, request.make, request.model, request.year,
        request.mileage_km, request.spec, request.country, request.city,
    )

    deal_indicator, deal_description = _compute_deal_indicator(
        request.asking_price, valuation
    )

    if valuation.confidence == "insufficient":
        raise HTTPException(
            status_code=422,
            detail="Not enough comparable listings for this vehicle. Try a more common make/model or broader criteria."
        )

    # Store in cache
    cache = ValuationQuery(
        cache_key=cache_key,
        make=request.make, model=request.model, year=request.year,
        mileage_km=request.mileage_km, spec=request.spec,
        trim=request.trim, city=request.city, country=request.country,
        estimated_price=valuation.estimate,
        price_low=valuation.price_low,
        price_high=valuation.price_high,
        comp_count=valuation.comp_count,
        confidence=valuation.confidence,
        model_version="statistical_v1",
        model_type="statistical",
        adjustments=[a.__dict__ for a in valuation.adjustments],
        response_ms=0,
        api_version="v1",
    )
    db.add(cache)
    await db.commit()

    logger.info("valuation_computed",
        make=request.make, model=request.model, year=request.year,
        estimate=valuation.estimate, confidence=valuation.confidence,
        comp_count=valuation.comp_count)

    return ValuationResponse(
        estimate=valuation.estimate,
        price_low=valuation.price_low,
        price_high=valuation.price_high,
        confidence=valuation.confidence,
        comp_count=valuation.comp_count,
        segment_median=valuation.segment_median,
        comps=[CompSummary(**c) for c in valuation.comps],
        adjustments=[Adjustment(**a.__dict__) for a in valuation.adjustments],
        confidence_interval_80=valuation.confidence_interval_80,
        knowledge=Knowledge(),
        deal_indicator=deal_indicator,
        deal_description=deal_description,
    )


def _build_response_from_cache(cached):
    return ValuationResponse(
        estimate=cached.estimated_price,
        price_low=cached.price_low,
        price_high=cached.price_high,
        confidence=cached.confidence,
        comp_count=cached.comp_count,
        segment_median=cached.estimated_price,
        comps=[],
        adjustments=[],
        confidence_interval_80=None,
        knowledge=Knowledge(),
        deal_indicator=None,
        deal_description=None,
    )
