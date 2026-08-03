"""Notification endpoints — price alerts and system notifications."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db, limiter
from src.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/notifications")
@limiter.limit("30/minute")
async def list_notifications(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user is None:
        raise HTTPException(401, "Authentication required")
    result = await db.execute(
        text("""SELECT id, make, model, target_price, last_triggered_at, created_at
                FROM price_alerts
                WHERE user_id = :uid AND active = true
                ORDER BY last_triggered_at DESC NULLS LAST
                LIMIT 50"""),
        {"uid": user["id"]},
    )
    rows = result.fetchall()
    return {
        "notifications": [
            {
                "id": str(r.id),
                "type": "price_alert",
                "title": f"Price alert: {r.make} {r.model}",
                "body": f"Target price AED {r.target_price:,.0f} reached" if r.last_triggered_at and r.target_price is not None else f"Watching {r.make} {r.model}",
                "read": r.last_triggered_at is not None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    }
