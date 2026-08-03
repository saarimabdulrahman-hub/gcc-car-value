"""Seed realistic demo listings so /v1/valuate returns real answers.

Usage:
    python scripts/seed_demo_listings.py            # seed
    python scripts/seed_demo_listings.py --clear    # remove seeded rows only

Seeded rows are marked source='seed_demo' so they can be removed cleanly.
"""
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from src.db.session import async_session_factory
from src.models.listing import Listing
from src.models.pipeline_run import PipelineRun

SOURCE = "seed_demo"

# (make, model, base_price_aed, price_drop_per_year)
MODELS = [
    ("Toyota", "Land Cruiser", 280000, 22000),
    ("Toyota", "Camry", 95000, 8000),
    ("Nissan", "Patrol", 250000, 20000),
    ("Nissan", "Altima", 78000, 7000),
    ("Mitsubishi", "Pajero", 110000, 9000),
    ("Lexus", "LX 570", 400000, 30000),
    ("Honda", "Accord", 88000, 7500),
    ("Hyundai", "Sonata", 72000, 6500),
]
CITIES = [("Dubai", "AE"), ("Abu Dhabi", "AE"), ("Sharjah", "AE"), ("Riyadh", "SA")]
SPECS = ["GCC", "GCC", "GCC", "US", "Japan"]  # GCC-weighted, matches the real market


def build_rows(run_id: str) -> list[Listing]:
    rng = random.Random(42)  # deterministic — reruns produce the same spread
    now = datetime.now(timezone.utc)
    rows: list[Listing] = []

    for make, model, base, per_year in MODELS:
        for year in range(2016, 2024):
            age = 2024 - year
            for _ in range(6):  # 6 per (model, year) => 48 per model, 384 total
                city, country = rng.choice(CITIES)
                spec = rng.choice(SPECS)
                price = base - (per_year * age)
                price *= rng.uniform(0.90, 1.10)          # market spread
                price *= 1.0 if spec == "GCC" else 0.90   # non-GCC discount
                price = round(max(price, 5000.0), 2)
                mileage = int(age * rng.uniform(12000, 22000)) or 5000
                first_seen = now - timedelta(days=rng.randint(1, 45))

                rows.append(Listing(
                    id=uuid.uuid4(),
                    source=SOURCE,
                    external_id=f"{make}-{model}-{year}-{uuid.uuid4().hex[:8]}",
                    url=None,
                    first_seen_at=first_seen,
                    last_seen_at=now,
                    status="active",
                    make=make,
                    model=model,
                    year=year,
                    spec=spec,
                    city=city,
                    country=country,
                    mileage_km=mileage,
                    body_type="SUV" if per_year > 15000 else "sedan",
                    transmission="automatic",
                    fuel_type="petrol",
                    seller_type=rng.choice(["dealer", "private"]),
                    original_price=price,
                    original_currency="AED",
                    exchange_rate=1.0,
                    exchange_timestamp=now,
                    normalized_price_aed=price,
                    quality_score=85,
                    quality_flags=[],
                    schema_version=1,
                    parser_version="seed_v1",
                    normalizer_version="seed_v1",
                    pipeline_run_id=run_id,
                ))
    return rows


async def main() -> None:
    clear = "--clear" in sys.argv
    async with async_session_factory() as session:
        result = await session.execute(delete(Listing).where(Listing.source == SOURCE))
        if clear:
            await session.execute(delete(PipelineRun).where(PipelineRun.source == SOURCE))
            await session.commit()
            print(f"cleared {result.rowcount} seeded rows")
            return

        run_id = str(uuid.uuid4())
        session.add(PipelineRun(
            run_id=run_id,
            source=SOURCE,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            success=True,
        ))
        await session.flush()          # parent must exist before the FK children

        rows = build_rows(run_id)
        session.add_all(rows)
        await session.commit()
        print(f"seeded {len(rows)} listings across {len(MODELS)} models")


if __name__ == "__main__":
    asyncio.run(main())
