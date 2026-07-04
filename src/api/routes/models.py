"""Model listing endpoints — populate frontend dropdowns from real data."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func
from src.api.dependencies import get_db
from src.models.listing import Listing

router = APIRouter()


@router.get("/models")
async def list_makes(
    db: AsyncSession = Depends(get_db),
    country: str | None = Query(None, description="Filter by country: AE, SA, etc."),
):
    """List all available makes with model counts."""
    stmt = select(
        Listing.make,
        func.count(distinct(Listing.model)).label("model_count"),
        func.count(Listing.id).label("listing_count"),
    ).where(Listing.quality_score >= 60)

    if country:
        stmt = stmt.where(Listing.country == country)

    stmt = stmt.group_by(Listing.make).order_by(Listing.make)
    result = await db.execute(stmt)
    rows = result.all()

    return {
        "makes": [
            {
                "make": row.make,
                "model_count": row.model_count,
                "listing_count": row.listing_count,
            }
            for row in rows
        ]
    }


@router.get("/models/{make}")
async def list_models(
    make: str,
    db: AsyncSession = Depends(get_db),
    country: str | None = Query(None),
):
    """List models for a make with year ranges and listing counts."""
    stmt = select(
        Listing.model,
        func.min(Listing.year).label("year_min"),
        func.max(Listing.year).label("year_max"),
        func.count(Listing.id).label("listing_count"),
    ).where(
        Listing.make == make,
        Listing.quality_score >= 60,
    )

    if country:
        stmt = stmt.where(Listing.country == country)

    stmt = stmt.group_by(Listing.model).order_by(Listing.model)
    result = await db.execute(stmt)
    rows = result.all()

    return {
        "make": make,
        "models": [
            {
                "model": row.model,
                "year_range": f"{row.year_min}–{row.year_max}",
                "listing_count": row.listing_count,
            }
            for row in rows
        ]
    }


@router.get("/models/{make}/{model}")
async def list_model_years(
    make: str,
    model: str,
    db: AsyncSession = Depends(get_db),
    country: str | None = Query(None),
):
    """List available years and trims for a specific make/model."""
    stmt = select(
        Listing.year,
        Listing.trim,
        func.count(Listing.id).label("listing_count"),
        func.avg(Listing.normalized_price_aed).label("avg_price"),
    ).where(
        Listing.make == make,
        Listing.model == model,
        Listing.quality_score >= 60,
    )

    if country:
        stmt = stmt.where(Listing.country == country)

    stmt = stmt.group_by(Listing.year, Listing.trim).order_by(Listing.year.desc())
    result = await db.execute(stmt)
    rows = result.all()

    years: dict[int, dict] = {}
    for row in rows:
        if row.year not in years:
            years[row.year] = {"year": row.year, "listing_count": 0, "trims": []}
        years[row.year]["listing_count"] += row.listing_count
        if row.trim:
            years[row.year]["trims"].append(row.trim)

    return {
        "make": make,
        "model": model,
        "years": sorted(years.values(), key=lambda y: y["year"], reverse=True),
    }
