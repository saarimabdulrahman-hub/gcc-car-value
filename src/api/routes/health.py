from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.api.dependencies import get_db
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        db_status = "healthy"
    except Exception as e:
        logger.error("db_health_check_failed", error=str(e))
        db_status = "unhealthy"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "0.1.0",
    }
