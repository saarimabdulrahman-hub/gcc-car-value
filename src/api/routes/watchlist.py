"""Watchlist endpoints — save, list, remove valuations."""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, limiter
from src.auth.dependencies import get_current_user

router = APIRouter()


class SaveValuationRequest(BaseModel):
    make: str
    model: str
    year: int
    mileage_km: int | None = None
    estimated_price: float | None = None


@router.get("/watchlist")
@limiter.limit("30/minute")
async def list_watchlist(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(401, "Authentication required")
    result = await db.execute(
        text("""SELECT id, make, model, year, mileage_km, estimated_price, confidence, created_at
                FROM saved_valuations WHERE user_id = :uid ORDER BY created_at DESC LIMIT 100"""),
        {"uid": user["id"]},
    )
    rows = result.fetchall()
    return {
        "vehicles": [
            {
                "id": str(r.id), "make": r.make, "model": r.model,
                "year": r.year, "mileage_km": r.mileage_km,
                "estimated_price": r.estimated_price, "confidence": r.confidence,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    }


@router.post("/watchlist")
@limiter.limit("30/minute")
async def save_to_watchlist(
    request: Request,
    req: SaveValuationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(401, "Authentication required")
    await db.execute(
        text("""INSERT INTO saved_valuations
                (id, user_id, make, model, year, mileage_km, estimated_price)
                VALUES (gen_random_uuid(), :uid, :make, :model, :year, :mileage, :price)"""),
        {"uid": user["id"], "make": req.make, "model": req.model,
         "year": req.year, "mileage": req.mileage_km, "price": req.estimated_price},
    )
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(500, "Failed to save to watchlist")
    return {"message": "Saved to watchlist"}


@router.delete("/watchlist/{item_id}")
@limiter.limit("30/minute")
async def remove_from_watchlist(
    request: Request,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(401, "Authentication required")
    result = await db.execute(
        text("DELETE FROM saved_valuations WHERE id = :id AND user_id = :uid"),
        {"id": item_id, "uid": user["id"]},
    )
    if result.rowcount == 0:
        raise HTTPException(404, "Item not found in watchlist")
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(500, "Failed to remove from watchlist")
    return {"message": "Removed from watchlist"}
