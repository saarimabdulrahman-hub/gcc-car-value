import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, limiter
from src.api.schemas.valuation import (
    ValuationRequest, ValuationResponse, CompSummary, Adjustment, Knowledge,
)
from src.engine.statistical import valuate, ValuationResult
from src.ml.model_loader import ModelLoader
from src.ml.prediction_service import PredictionService
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
    request: Request,
    valuation_req: ValuationRequest,
    db: AsyncSession = Depends(get_db),
):
    cache_key = _compute_cache_key(valuation_req)

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

    # Compute statistical valuation (always runs — baseline)
    valuation = await valuate(
        db, valuation_req.make, valuation_req.model, valuation_req.year,
        valuation_req.mileage_km, valuation_req.spec, valuation_req.country, valuation_req.city,
    )

    # --- ML prediction (optional — graceful fallback) ---
    ml_result = None
    prediction_source = "statistical"
    ml_model_version = None
    fallback_used = False

    if valuation.confidence != "insufficient":
        try:
            loader = ModelLoader(db)
            ml_model, ml_metadata = await loader.get_model()

            if ml_model is not None:
                svc = PredictionService(ml_model, ml_metadata)
                ml_result = svc.predict(
                    make=valuation_req.make,
                    model=valuation_req.model,
                    year=valuation_req.year,
                    mileage_km=valuation_req.mileage_km,
                    spec=valuation_req.spec,
                    country=valuation_req.country,
                    city=valuation_req.city,
                    market_context={
                        "segment_median_price": valuation.segment_median,
                        "listing_volume": valuation.comp_count,
                    },
                )
                ml_model_version = ml_result.model_version

                # Cross-reference: if ML and statistical disagree by >15%,
                # default to statistical and flag the discrepancy
                if valuation.estimate > 0:
                    pct_diff = abs(ml_result.predicted_value - valuation.estimate) / valuation.estimate
                    if pct_diff > 0.15:
                        logger.warning("ml_statistical_disagreement",
                            make=valuation_req.make, model=valuation_req.model,
                            statistical_estimate=valuation.estimate,
                            ml_estimate=round(ml_result.predicted_value),
                            pct_diff=round(pct_diff * 100, 1))
                        # Use statistical as the primary, but record ML
                        prediction_source = "statistical"
                        fallback_used = True
                    else:
                        # ML and statistical agree — use ensemble (average)
                        prediction_source = "ensemble"
                        valuation.estimate = round(
                            (valuation.estimate + ml_result.predicted_value) / 2
                        )
            else:
                logger.info("ml_model_unavailable", reason="no_active_model")
        except Exception as e:
            logger.warning("ml_prediction_failed",
                error=str(e)[:200],
                make=valuation_req.make, model=valuation_req.model)
            fallback_used = True
            prediction_source = "statistical"

    deal_indicator, deal_description = _compute_deal_indicator(
        valuation_req.asking_price, valuation
    )

    if valuation.confidence == "insufficient":
        raise HTTPException(
            status_code=422,
            detail="Not enough comparable listings for this vehicle. Try a more common make/model or broader criteria."
        )

    # Store in cache
    cache = ValuationQuery(
        cache_key=cache_key,
        make=valuation_req.make, model=valuation_req.model, year=valuation_req.year,
        mileage_km=valuation_req.mileage_km, spec=valuation_req.spec,
        trim=valuation_req.trim, city=valuation_req.city, country=valuation_req.country,
        estimated_price=valuation.estimate,
        price_low=valuation.price_low,
        price_high=valuation.price_high,
        comp_count=valuation.comp_count,
        confidence=valuation.confidence,
        model_version=ml_model_version or "statistical_v1",
        model_type="lightgbm" if prediction_source in ("ml", "ensemble") else "statistical",
        adjustments=[a.__dict__ for a in valuation.adjustments],
        response_ms=0,
        api_version="v1",
    )
    db.add(cache)
    await db.commit()

    logger.info("valuation_computed",
        make=valuation_req.make, model=valuation_req.model, year=valuation_req.year,
        estimate=valuation.estimate, confidence=valuation.confidence,
        comp_count=valuation.comp_count,
        prediction_source=prediction_source,
        ml_model_version=ml_model_version,
        fallback_used=fallback_used)

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
        prediction_source=prediction_source,
        model_version=ml_model_version,
        fallback_used=fallback_used,
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
        prediction_source=cached.model_type or "statistical",
        model_version=cached.model_version,
        fallback_used=False,
    )
