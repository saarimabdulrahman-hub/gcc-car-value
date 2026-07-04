"""Recommendation engine — content-based from knowledge base and market data.

Suggests cars based on: budget, body type, family size, use case.
Uses the knowledge base ratings + listing data for scoring.
"""
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.listing import Listing
from src.models.model_rating import ModelRating


@dataclass
class Recommendation:
    make: str
    model: str
    score: float
    reason: str
    avg_price: float | None
    reliability: float | None
    resale_value: float | None


async def recommend(
    session: AsyncSession,
    budget_min: float | None = None,
    budget_max: float | None = None,
    body_type: str | None = None,
    family_size: int | None = None,
    prefer_gcc: bool = True,
    limit: int = 10,
) -> list[Recommendation]:
    """Generate car recommendations based on user criteria."""

    # Get active makes/models with pricing
    stmt = (select(
        Listing.make, Listing.model,
        func.avg(Listing.normalized_price_aed).label("avg_price"),
        func.count(Listing.id).label("n"),
    ).where(
        Listing.quality_score >= 60,
        Listing.status == "active",
    ).group_by(Listing.make, Listing.model)
     .having(func.count(Listing.id) >= 10))

    if body_type:
        stmt = stmt.where(Listing.body_type == body_type)

    result = await session.execute(stmt)
    rows = result.all()

    recommendations = []
    for row in rows:
        score = 0.0
        reasons = []

        # Budget fit
        if budget_max and row.avg_price:
            if row.avg_price <= budget_max:
                score += 3
                reasons.append("within budget")
            elif row.avg_price <= budget_max * 1.2:
                score += 1
                reasons.append("slightly above budget")

        # Volume = popularity signal
        if row.n >= 50:
            score += 2
            reasons.append("popular choice")
        elif row.n >= 20:
            score += 1

        # Get knowledge base ratings
        rating_stmt = select(ModelRating).where(
            ModelRating.make == row.make,
            ModelRating.model == row.model,
        ).limit(1)
        rating_result = await session.execute(rating_stmt)
        rating = rating_result.scalar_one_or_none()

        reliability = None
        resale = None
        if rating:
            reliability = rating.reliability
            resale = rating.resale_value
            if rating.overall:
                score += float(rating.overall)
            if rating.fuel_economy and rating.fuel_economy >= 4:
                score += 1
                reasons.append("fuel efficient")
            if family_size and family_size >= 5 and rating.comfort and rating.comfort >= 4:
                score += 1
                reasons.append("family friendly")

        if score > 0:
            recommendations.append(Recommendation(
                make=row.make, model=row.model, score=round(score, 1),
                reason=", ".join(reasons[:3]) if reasons else "market pick",
                avg_price=round(row.avg_price) if row.avg_price else None,
                reliability=reliability,
                resale_value=resale,
            ))

    recommendations.sort(key=lambda r: r.score, reverse=True)
    return recommendations[:limit]
