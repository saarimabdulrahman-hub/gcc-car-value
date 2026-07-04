"""Statistical valuation engine — percentile-based with adjustments.

Spec Section 6: Computes fair market value from comparable listings.
Always runs (even when ML is active) as the baseline and explainability layer.
"""
from dataclasses import dataclass, field
from src.engine.comp_finder import CompListing, find_comps
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np


@dataclass
class Adjustment:
    reason: str
    amount: float
    detail: str


@dataclass
class ValuationResult:
    estimate: float                    # point estimate in AED
    price_low: float                   # 10th percentile
    price_high: float                  # 90th percentile
    confidence: str                    # high, medium, low, insufficient
    comp_count: int
    comps: list[dict]                  # top comps with attribution
    adjustments: list[Adjustment]      # what moved the price
    segment_median: float              # raw median of comps before adjustment
    confidence_interval_80: tuple[float, float] | None = None


async def valuate(
    session: AsyncSession,
    make: str,
    model: str,
    year: int,
    mileage_km: int | None = None,
    spec: str | None = None,
    country: str | None = None,
    city: str | None = None,
) -> ValuationResult:
    """Compute a statistical valuation for a vehicle."""

    # Step 1: Find comps
    comps = await find_comps(
        session, make, model, year, mileage_km, spec, country, city
    )

    if len(comps) < 5:
        return ValuationResult(
            estimate=0, price_low=0, price_high=0,
            confidence="insufficient", comp_count=len(comps),
            comps=[], adjustments=[], segment_median=0,
        )

    # Step 2: Compute percentile bands from comps
    prices = np.array([c.asking_price_aed for c in comps])
    p25 = float(np.percentile(prices, 25))
    p50 = float(np.percentile(prices, 50))
    p75 = float(np.percentile(prices, 75))

    estimate = p50
    adjustments: list[Adjustment] = []

    # Step 3: Adjust for mileage delta
    if mileage_km is not None:
        comp_mileages = [c.mileage_km for c in comps if c.mileage_km is not None]
        if comp_mileages:
            comp_median_km = np.median(comp_mileages)
            mileage_delta = comp_median_km - mileage_km
            # Rough depreciation: ~0.25 AED per km for typical GCC cars
            dep_per_km = 0.25
            mileage_adj = mileage_delta * dep_per_km
            estimate += mileage_adj
            adjustments.append(Adjustment(
                reason="mileage",
                amount=mileage_adj,
                detail=f"{'More' if mileage_delta > 0 else 'Fewer'} km than segment avg. Adjustment: {mileage_adj:+.0f} AED"
            ))

    # Step 4: Spec adjustment
    if spec:
        gcc_count = sum(1 for c in comps if c.spec == "GCC")
        non_gcc_count = sum(1 for c in comps if c.spec and c.spec != "GCC")
        if gcc_count > 0 and non_gcc_count > 0:
            gcc_prices = [c.asking_price_aed for c in comps if c.spec == "GCC"]
            non_gcc_prices = [c.asking_price_aed for c in comps if c.spec and c.spec != "GCC"]
            spec_premium = np.median(gcc_prices) - np.median(non_gcc_prices)
            if spec == "GCC":
                estimate += spec_premium * 0.5  # partial adjustment
                adjustments.append(Adjustment(
                    reason="spec", amount=spec_premium * 0.5,
                    detail=f"GCC spec premium: +{spec_premium * 0.5:.0f} AED"
                ))
            else:
                estimate -= spec_premium * 0.5
                adjustments.append(Adjustment(
                    reason="spec", amount=-spec_premium * 0.5,
                    detail=f"Non-GCC spec adjustment: {spec_premium * -0.5:.0f} AED"
                ))

    # Step 5: City premium
    if city and comps:
        same_city = [c.asking_price_aed for c in comps if c.city == city]
        other_city = [c.asking_price_aed for c in comps if c.city != city]
        if same_city and other_city:
            city_delta = np.median(same_city) - np.median(other_city)
            estimate += city_delta * 0.3
            adjustments.append(Adjustment(
                reason="city", amount=city_delta * 0.3,
                detail=f"{city} market adjustment: {city_delta * 0.3:+.0f} AED"
            ))

    # Step 6: Confidence
    confidence = _compute_confidence(comps, prices)

    # Step 7: Bootstrap 80% CI
    ci = _bootstrap_ci(prices)

    # Step 8: Format comps for response (platform attribution, no URLs)
    comp_summaries: list[dict] = []
    for c in sorted(comps, key=lambda c: c.relevance_score, reverse=True)[:10]:
        comp_summaries.append({
            "price_aed": c.asking_price_aed,
            "year": c.year,
            "mileage_km": c.mileage_km,
            "spec": c.spec,
            "city": c.city,
            "country": c.country,
            "status": c.status,
            "found_on": c.found_on_text,
            "platform": c.platform_name,
            "relevance_score": round(c.relevance_score, 1),
        })

    return ValuationResult(
        estimate=round(estimate),
        price_low=round(float(np.percentile(prices, 10))),
        price_high=round(float(np.percentile(prices, 90))),
        confidence=confidence,
        comp_count=len(comps),
        comps=comp_summaries,
        adjustments=adjustments,
        segment_median=round(p50),
        confidence_interval_80=(round(ci[0]), round(ci[1])),
    )


def _compute_confidence(comps: list[CompListing],
                        prices: np.ndarray) -> str:
    n = len(comps)
    cv = float(np.std(prices) / np.mean(prices)) if np.mean(prices) > 0 else 999
    recent = sum(1 for c in comps
                 if c.days_on_market is not None and c.days_on_market <= 30)

    if n >= 30 and cv < 0.15 and recent >= 15:
        return "high"
    elif n >= 10 and cv < 0.30:
        return "medium"
    elif n >= 5:
        return "low"
    return "insufficient"


def _bootstrap_ci(prices: np.ndarray, confidence: float = 0.80,
                  n_bootstrap: int = 1000) -> tuple[float, float]:
    rng = np.random.default_rng(42)
    medians = np.array([
        rng.choice(prices, size=len(prices), replace=True).mean()
        for _ in range(n_bootstrap)
    ])
    low = np.percentile(medians, ((1 - confidence) / 2) * 100)
    high = np.percentile(medians, (1 + confidence) / 2 * 100)
    return float(low), float(high)
