"""Seed realistic demo listings so /v1/valuate returns real answers.

Usage:
    python scripts/seed_demo_listings.py            # seed
    python scripts/seed_demo_listings.py --clear    # remove seeded rows only

Seeded rows are marked found_on='seed_demo' so they can be removed cleanly.
"""
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from src.db.session import async_session_factory

SEED_MARKER = "seed_demo"

# (make, model, base_price_aed, price_per_year_older)
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
SPECS = ["GCC", "GCC", "GCC", "US", "Japan"]


def build_rows() -> list[dict]:
    rng = random.Random(42)
    now = datetime.now(timezone.utc)
    rows = []
    for make, model, base, per_year in MODELS:
        for year in range(2016, 2024):
            age = 2024 - year
            for _ in range(6):
                city, country = rng.choice(CITIES)
                spec = rng.choice(SPECS)
                price = base - (per_year * age)
                price *= rng.uniform(0.90, 1.10)
                price *= 1.0 if spec == "GCC" else 0.90
                mileage = int(age * rng.uniform(12000, 22000)) or 5000
                rows.append({
                    "id": str(uuid.uuid4()),
                    "make": make, "model": model, "year": year,
                    "mileage_km": mileage, "spec": spec,
                    "city": city, "country": country,
                    "price_aed": round(price, 2),
                    "quality_score": 85,
                    "found_on": SEED_MARKER,
                    "captured_at": now,
                })
    return rows


async def main() -> None:
    clear = "--clear" in sys.argv
    async with async_session_factory() as session:
        if clear:
            r = await session.execute(
                text("DELETE FROM listings WHERE found_on = :marker"),
                {"marker": SEED_MARKER})
            await session.commit()
            print(f"cleared {r.rowcount} seeded rows")
            return

        rows = build_rows()
        await session.execute(
            text("""INSERT INTO listings
                    (id, make, model, year, mileage_km, spec, city, country,
                     price_aed, quality_score, found_on, captured_at)
                    VALUES (:id, :make, :model, :year, :mileage_km, :spec,
                            :city, :country, :price_aed, :quality_score,
                            :found_on, :captured_at)"""),
            rows)
        await session.commit()
        print(f"seeded {len(rows)} listings across {len(MODELS)} models")


if __name__ == "__main__":
    asyncio.run(main())
