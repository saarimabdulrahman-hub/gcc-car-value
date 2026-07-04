import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.listing import Listing
from src.models.dead_letter import DeadLetter
from src.config import get_settings

settings = get_settings()


async def promote_listing(
    data: dict, score: int, flags: list[str], session: AsyncSession
) -> Listing | None:
    threshold = settings.quality_promotion_threshold

    if score < threshold:
        dead = DeadLetter(
            source=data["source"],
            external_id=data.get("external_id"),
            rejection_reason=f"quality_score_{score}_below_{threshold}",
            raw_data=data,
            quality_score=score,
            pipeline_run_id=data.get("pipeline_run_id", str(uuid.uuid4())),
        )
        session.add(dead)
        return None

    stmt = select(Listing).where(
        Listing.source == data["source"],
        Listing.external_id == data["external_id"],
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if existing:
        existing.last_seen_at = now
        existing.status = data.get("status", "active")
        existing.original_price = data["original_price"]
        existing.original_currency = data["original_currency"]
        existing.exchange_rate = data["exchange_rate"]
        existing.exchange_timestamp = now
        existing.normalized_price_aed = data["normalized_price_aed"]
        existing.mileage_km = data.get("mileage_km")
        existing.quality_score = score
        existing.quality_flags = flags
        existing.schema_version = data.get("schema_version", 1)
        existing.parser_version = data.get("parser_version", "1.0.0")
        existing.normalizer_version = data.get("normalizer_version", "1.0.0")
        existing.pipeline_run_id = data.get("pipeline_run_id", str(uuid.uuid4()))
        return existing

    listing = Listing(
        source=data["source"], external_id=data["external_id"],
        url=data.get("url"), first_seen_at=now, last_seen_at=now,
        status=data.get("status", "active"), make=data["make"],
        model=data["model"], year=data["year"], trim=data.get("trim"),
        spec=data.get("spec"), body_type=data.get("body_type"),
        transmission=data.get("transmission"), fuel_type=data.get("fuel_type"),
        engine_size=data.get("engine_size"), color=data.get("color"),
        city=data["city"], country=data["country"],
        original_price=data["original_price"],
        original_currency=data["original_currency"],
        exchange_rate=data["exchange_rate"], exchange_timestamp=now,
        normalized_price_aed=data["normalized_price_aed"],
        mileage_km=data.get("mileage_km"), seller_type=data.get("seller_type"),
        quality_score=score, quality_flags=flags,
        schema_version=data.get("schema_version", 1),
        parser_version=data.get("parser_version", "1.0.0"),
        normalizer_version=data.get("normalizer_version", "1.0.0"),
        pipeline_run_id=data.get("pipeline_run_id", str(uuid.uuid4())),
        raw_data_s3_key=data.get("raw_data_s3_key"),
    )
    session.add(listing)
    return listing
