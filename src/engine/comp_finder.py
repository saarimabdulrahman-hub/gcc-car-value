"""Comp finder — tiered hard filters with weighted scoring.

Spec Section 5: Finds comparable listings for a target vehicle.
Returns scored and ranked comps with platform attribution (no URLs).
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, text
from src.models.listing import Listing


@dataclass
class CompListing:
    source: str              # 'dubizzle_uae', 'yallamotor', 'haraj'
    make: str
    model: str
    year: int
    mileage_km: int | None
    spec: str | None
    city: str
    country: str
    asking_price_aed: float
    quality_score: int
    status: str
    days_on_market: int | None
    delisting_confidence: float | None
    # Platform attribution — tells user WHERE, not the URL
    platform_name: str       # human-readable: 'Dubizzle UAE', 'Haraj KSA'
    # Scoring
    relevance_score: float = 0.0

    @property
    def found_on_text(self) -> str:
        """Human-readable attribution: 'Found on Dubizzle UAE, Dubai'"""
        return f"Found on {self.platform_name}, {self.city}"


def _platform_name(source: str) -> str:
    names = {
        "dubizzle_uae": "Dubizzle UAE",
        "dubizzle_ksa": "Dubizzle KSA",
        "yallamotor": "YallaMotor",
        "haraj": "Haraj KSA",
        "carswitch": "CarSwitch",
        "emirates_auction": "Emirates Auction",
        "opensooq": "OpenSooq",
    }
    return names.get(source, source)


async def find_comps(
    session: AsyncSession,
    make: str,
    model: str,
    year: int,
    mileage_km: int | None,
    spec: str | None,
    country: str | None,
    city: str | None = None,
    min_comps: int = 15,
    max_comps: int = 50,
) -> list[CompListing]:
    """Find comparable listings using tiered hard filters."""

    tiers = [
        {"year_range": 2, "mileage_pct": 0.30, "same_spec": True,
         "same_country": True},
        {"year_range": 3, "mileage_pct": 0.50, "same_spec": False,
         "same_country": True},
        {"year_range": 4, "mileage_pct": 0.75, "same_spec": False,
         "same_country": False},
    ]

    all_comps: list[CompListing] = []

    for tier in tiers:
        year_min = year - tier["year_range"]
        year_max = year + tier["year_range"]

        conditions = [
            Listing.make == make,
            Listing.model == model,
            Listing.year.between(year_min, year_max),
            Listing.status.in_(["active", "probably_sold", "sold_confirmed"]),
            Listing.quality_score >= 60,
        ]

        if tier["same_country"] and country:
            conditions.append(Listing.country == country)

        if tier["same_spec"] and spec:
            conditions.append(Listing.spec == spec)

        if mileage_km and tier["mileage_pct"]:
            delta = int(mileage_km * tier["mileage_pct"])
            conditions.append(
                Listing.mileage_km.between(mileage_km - delta, mileage_km + delta)
            )

        stmt = (select(Listing)
                .where(and_(*conditions))
                .order_by(Listing.last_seen_at.desc())
                .limit(max_comps * 2))

        result = await session.execute(stmt)
        rows = result.scalars().all()

        for row in rows:
            comp = CompListing(
                source=row.source,
                make=row.make,
                model=row.model,
                year=row.year,
                mileage_km=row.mileage_km,
                spec=row.spec,
                city=row.city,
                country=row.country,
                asking_price_aed=row.normalized_price_aed,
                quality_score=row.quality_score,
                status=row.status,
                days_on_market=_compute_days_on_market(row),
                delisting_confidence=row.delisting_confidence,
                platform_name=_platform_name(row.source),
            )
            comp.relevance_score = _score_comp(
                comp, make, model, year, mileage_km, spec, country
            )
            all_comps.append(comp)

        # Sort by relevance score for this tier
        all_comps.sort(key=lambda c: c.relevance_score, reverse=True)

        if len(all_comps) >= min_comps:
            break

    all_comps.sort(key=lambda c: c.relevance_score, reverse=True)
    return all_comps[:max_comps]


def _compute_days_on_market(listing) -> int | None:
    if listing.first_seen_at:
        now = datetime.now(timezone.utc)
        fs = listing.first_seen_at
        # Handle naive datetimes from SQLite
        if fs.tzinfo is None:
            fs = fs.replace(tzinfo=timezone.utc)
        delta = now - fs
        return delta.days
    return None


def _score_comp(comp: CompListing, make: str, model: str, year: int,
                mileage_km: int | None, spec: str | None,
                country: str | None) -> float:
    score = 100.0

    # Recency
    if comp.days_on_market is not None:
        if comp.days_on_market <= 7:
            score -= 0
        elif comp.days_on_market <= 30:
            score -= 5
        elif comp.days_on_market <= 90:
            score -= 15
        else:
            score -= 30

    # Mileage closeness
    if comp.mileage_km and mileage_km:
        delta_pct = abs(comp.mileage_km - mileage_km) / max(mileage_km, 1)
        score -= delta_pct * 25

    # Year match
    year_delta = abs(comp.year - year)
    score -= year_delta * 8

    # Spec match
    if spec and comp.spec:
        if comp.spec == spec:
            score -= 0
        elif comp.spec == "GCC" and spec != "GCC":
            score -= 5
        else:
            score -= 15

    # Country match
    if country and comp.country == country:
        score -= 0
    else:
        score -= 10

    # Quality bonus
    score += (comp.quality_score / 100) * 10

    # Sold comp bonus (real transaction evidence)
    if comp.status in ("sold_confirmed", "probably_sold"):
        score += 5
    if comp.delisting_confidence and comp.delisting_confidence > 0.8:
        score += 3

    return score
