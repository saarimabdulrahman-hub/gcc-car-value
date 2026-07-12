"""Admin endpoints — monitoring, health, pipeline stats.

All endpoints require authentication + admin-level permissions.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.api.dependencies import get_db
from src.auth.dependencies import require_permission
from src.auth.roles import Permission
from src.models.pipeline_run import PipelineRun
from src.models.listing import Listing
from src.models.valuation_query import ValuationQuery
from src.models.drift_event import DriftEvent
from src.models.scraper_health import ScraperHealth
from datetime import datetime, timedelta, timezone
import structlog

router = APIRouter()
logger = structlog.get_logger()


@router.get("/admin/stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission(Permission.ADMIN_METRICS)),
):
    """Overall platform statistics."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    total_listings = (await db.execute(select(func.count()).select_from(Listing))).scalar()
    active_listings = (await db.execute(
        select(func.count()).select_from(Listing).where(Listing.status == "active")
    )).scalar()
    recent_valuations = (await db.execute(
        select(func.count()).select_from(ValuationQuery)
        .where(ValuationQuery.queried_at >= week_ago)
    )).scalar()
    total_valuations = (await db.execute(
        select(func.count()).select_from(ValuationQuery)
    )).scalar()

    # Last pipeline run
    last_run = (await db.execute(
        select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(1)
    )).scalar_one_or_none()

    # Active drift events
    drift_count = (await db.execute(
        select(func.count()).select_from(DriftEvent)
        .where(DriftEvent.acknowledged == False, DriftEvent.threshold_exceeded == True)
    )).scalar()

    return {
        "listings": {"total": total_listings, "active": active_listings},
        "valuations": {"total": total_valuations, "last_7_days": recent_valuations},
        "last_pipeline_run": {
            "source": last_run.source if last_run else None,
            "started_at": last_run.started_at.isoformat() if last_run and last_run.started_at else None,
            "completed_at": last_run.completed_at.isoformat() if last_run and last_run.completed_at else None,
            "success": last_run.success if last_run else None,
            "records_ingested": last_run.records_ingested if last_run else 0,
        } if last_run else None,
        "unacknowledged_drifts": drift_count,
        "api_version": "v1",
    }


@router.get("/admin/scrapers")
async def scraper_status(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission(Permission.ADMIN_SCRAPERS)),
):
    """Health status of all scrapers."""
    subquery = (select(
        ScraperHealth.source,
        func.max(ScraperHealth.captured_at).label("last_run")
    ).group_by(ScraperHealth.source)).subquery()

    result = await db.execute(select(
        subquery.c.source,
        subquery.c.last_run,
    ).order_by(subquery.c.last_run.desc()))
    rows = result.all()

    now = datetime.now(timezone.utc)
    scrapers = []
    for row in rows:
        hours_ago = ((now - row.last_run).total_seconds() / 3600) if row.last_run else None
        scrapers.append({
            "source": row.source,
            "last_run": row.last_run.isoformat() if row.last_run else None,
            "hours_since_last_run": round(hours_ago, 1) if hours_ago else None,
            "status": "healthy" if hours_ago and hours_ago < 36 else "stale",
        })
    return {"scrapers": scrapers}


@router.get("/admin/quality")
async def quality_metrics(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission(Permission.ADMIN_QUALITY)),
):
    """Data quality metrics — quality score distribution, rejection rates."""
    total = (await db.execute(select(func.count()).select_from(Listing))).scalar()
    if not total:
        return {"total_listings": 0, "quality_distribution": {}}

    high = (await db.execute(
        select(func.count()).select_from(Listing).where(Listing.quality_score >= 80)
    )).scalar()
    medium = (await db.execute(
        select(func.count()).select_from(Listing)
        .where(Listing.quality_score >= 60, Listing.quality_score < 80)
    )).scalar()
    low = (await db.execute(
        select(func.count()).select_from(Listing).where(Listing.quality_score < 60)
    )).scalar()

    return {
        "total_listings": total,
        "quality_distribution": {
            "high_quality": high, "medium_quality": medium, "low_quality": low,
        },
        "high_quality_pct": round(high / total * 100, 1) if total else 0,
    }
