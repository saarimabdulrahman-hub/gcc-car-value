"""Model listing endpoints."""
import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db  # type: ignore[attr-defined]

logger = structlog.get_logger()
router = APIRouter()


@router.get("/models")
async def list_makes(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    country: str | None = Query(None, description="Filter by country: AE, SA, etc."),
):
    """List all available makes with model counts."""
    try:
        query = """
            SELECT make, COUNT(DISTINCT model) AS model_count, COUNT(*) AS listing_count
            FROM listings WHERE quality_score >= 60
        """
        if country:
            query += " AND country = :country"
            result = await db.execute(text(query + " GROUP BY make ORDER BY make"), {"country": country})  # noqa: E501
        else:
            result = await db.execute(text(query + " GROUP BY make ORDER BY make"))

        rows = result.fetchall()
        return {
            "makes": [
                {"make": r.make, "model_count": r.model_count, "listing_count": r.listing_count}
                for r in rows
            ]
        }
    except Exception:
        logger.exception("models_list_makes_failed")
        return {"makes": [], "error": "Database temporarily unavailable"}


@router.get("/models/{make}")
async def list_models(
    make: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    country: str | None = Query(None),
):
    """List models for a make."""
    try:
        query = """
            SELECT model, MIN(year) AS year_min, MAX(year) AS year_max, COUNT(*) AS listing_count
            FROM listings WHERE make = :make AND quality_score >= 60
        """
        if country:
            query += " AND country = :country"
            result = await db.execute(
                text(query + " GROUP BY model ORDER BY model"),
                {"make": make, "country": country} if country else {"make": make}
            )
        else:
            result = await db.execute(
                text(query + " GROUP BY model ORDER BY model"), {"make": make}
            )

        rows = result.fetchall()
        return {
            "make": make,
            "models": [
                {"model": r.model, "year_range": f"{r.year_min}–{r.year_max}", "listing_count": r.listing_count}  # noqa: E501
                for r in rows
            ]
        }
    except Exception:
        logger.exception("models_list_models_failed", make=make)
        return {"make": make, "models": [], "error": "Database temporarily unavailable"}


@router.get("/models/{make}/{model}")
async def list_model_years(
    make: str, model: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    country: str | None = Query(None),
):
    """List years for a make/model."""
    try:
        query = """
            SELECT year, COUNT(*) AS listing_count
            FROM listings WHERE make = :make AND model = :model AND quality_score >= 60
        """
        if country:
            query += " AND country = :country"
            result = await db.execute(
                text(query + " GROUP BY year ORDER BY year DESC"),
                {"make": make, "model": model, "country": country} if country else {"make": make, "model": model}  # noqa: E501
            )
        else:
            result = await db.execute(
                text(query + " GROUP BY year ORDER BY year DESC"), {"make": make, "model": model}
            )

        rows = result.fetchall()
        return {
            "make": make,
            "model": model,
            "years": [{"year": r.year, "listing_count": r.listing_count} for r in rows]
        }
    except Exception:
        logger.exception("models_list_years_failed", make=make, model=model)
        return {"make": make, "model": model, "years": [], "error": "Database temporarily unavailable"}  # noqa: E501
