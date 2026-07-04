"""End-to-end integration test: comp finder → valuation engine → API response.

Uses SQLite (in-memory) to avoid Docker/PostgreSQL dependency for local testing.
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.db.base import Base
from src.models.listing import Listing
from src.engine.comp_finder import find_comps
from src.engine.statistical import valuate


@pytest_asyncio.fixture
async def populated_db():
    """SQLite database with 30 fake GCC car listings."""
    engine = create_async_engine("sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true")

    async with engine.begin() as conn:
        # Create tables manually (avoid PG-specific types like UUID, JSONB, DATERANGE)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    now = datetime.now(timezone.utc)

    # Seed: 30 Land Cruiser 2018 listings across GCC
    listings_data = [
        # Dubai — GCC spec, low mileage (premium prices)
        {"source": "dubizzle_uae", "ext_id": "dxb001", "city": "Dubai", "country": "AE",
         "price": 135000, "mileage": 60000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb002", "city": "Dubai", "country": "AE",
         "price": 128000, "mileage": 75000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb003", "city": "Dubai", "country": "AE",
         "price": 132000, "mileage": 55000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "yallamotor", "ext_id": "ylm001", "city": "Dubai", "country": "AE",
         "price": 130000, "mileage": 68000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb004", "city": "Dubai", "country": "AE",
         "price": 140000, "mileage": 40000, "spec": "GCC", "seller": "dealer", "status": "sold_confirmed"},
        {"source": "dubizzle_uae", "ext_id": "dxb005", "city": "Sharjah", "country": "AE",
         "price": 118000, "mileage": 90000, "spec": "GCC", "seller": "private", "status": "active"},
        # Dubai — US spec (cheaper)
        {"source": "dubizzle_uae", "ext_id": "dxb006", "city": "Dubai", "country": "AE",
         "price": 98000, "mileage": 80000, "spec": "US", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb007", "city": "Dubai", "country": "AE",
         "price": 95000, "mileage": 95000, "spec": "US", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb008", "city": "Sharjah", "country": "AE",
         "price": 90000, "mileage": 100000, "spec": "US", "seller": "dealer", "status": "active"},
        # Abu Dhabi
        {"source": "dubizzle_uae", "ext_id": "auh001", "city": "Abu Dhabi", "country": "AE",
         "price": 125000, "mileage": 70000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "auh002", "city": "Abu Dhabi", "country": "AE",
         "price": 127000, "mileage": 65000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "auh003", "city": "Abu Dhabi", "country": "AE",
         "price": 122000, "mileage": 72000, "spec": "GCC", "seller": "private", "status": "probably_sold"},
        # Saudi — Riyadh
        {"source": "haraj", "ext_id": "ruh001", "city": "Riyadh", "country": "SA",
         "price": 47000, "mileage": 85000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "haraj", "ext_id": "ruh002", "city": "Riyadh", "country": "SA",
         "price": 45000, "mileage": 90000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "haraj", "ext_id": "ruh003", "city": "Riyadh", "country": "SA",
         "price": 48000, "mileage": 80000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "yallamotor", "ext_id": "ylm002", "city": "Riyadh", "country": "SA",
         "price": 46500, "mileage": 87000, "spec": "GCC", "seller": "dealer", "status": "active"},
        # Saudi — Jeddah
        {"source": "haraj", "ext_id": "jed001", "city": "Jeddah", "country": "SA",
         "price": 44000, "mileage": 95000, "spec": "US", "seller": "private", "status": "active"},
        {"source": "haraj", "ext_id": "jed002", "city": "Jeddah", "country": "SA",
         "price": 46000, "mileage": 88000, "spec": "GCC", "seller": "private", "status": "active"},
        # More Dubai listings for volume
        {"source": "dubizzle_uae", "ext_id": "dxb009", "city": "Dubai", "country": "AE",
         "price": 129000, "mileage": 72000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb010", "city": "Dubai", "country": "AE",
         "price": 133000, "mileage": 58000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb011", "city": "Dubai", "country": "AE",
         "price": 126000, "mileage": 78000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb012", "city": "Dubai", "country": "AE",
         "price": 130500, "mileage": 67000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb013", "city": "Dubai", "country": "AE",
         "price": 131000, "mileage": 64000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb014", "city": "Dubai", "country": "AE",
         "price": 127500, "mileage": 76000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb015", "city": "Dubai", "country": "AE",
         "price": 134000, "mileage": 52000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb016", "city": "Dubai", "country": "AE",
         "price": 97000, "mileage": 90000, "spec": "US", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb017", "city": "Dubai", "country": "AE",
         "price": 138000, "mileage": 45000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb018", "city": "Dubai", "country": "AE",
         "price": 124000, "mileage": 80000, "spec": "GCC", "seller": "private", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb019", "city": "Dubai", "country": "AE",
         "price": 150000, "mileage": 30000, "spec": "GCC", "seller": "dealer", "status": "active"},
        {"source": "dubizzle_uae", "ext_id": "dxb020", "city": "Dubai", "country": "AE",
         "price": 129500, "mileage": 71000, "spec": "GCC", "seller": "dealer", "status": "active"},
    ]

    async with session_factory() as session:
        for i, ld in enumerate(listings_data):
            listing = Listing(
                id=f"00000000-0000-0000-0000-{i:012d}",
                source=ld["source"], external_id=ld["ext_id"],
                first_seen_at=now, last_seen_at=now, status=ld["status"],
                make="Toyota", model="Land Cruiser", year=2018,
                mileage_km=ld["mileage"], spec=ld["spec"],
                city=ld["city"], country=ld["country"],
                original_price=ld["price"], original_currency="SAR" if ld["country"] == "SA" else "AED",
                exchange_rate=0.978 if ld["country"] == "SA" else 1.0,
                exchange_timestamp=now,
                normalized_price_aed=ld["price"] * (0.978 if ld["country"] == "SA" else 1.0),
                quality_score=90,
                seller_type=ld["seller"],
                schema_version=1, parser_version="test", normalizer_version="test",
                pipeline_run_id="00000000-0000-0000-0000-000000000000",
            )
            session.add(listing)
        await session.commit()

    yield session_factory

    await engine.dispose()


@pytest.mark.asyncio
async def test_find_comps_for_gcc_land_cruiser(populated_db):
    """Find comps for a 2018 GCC Land Cruiser in Dubai with 80K km."""
    async with populated_db() as session:
        comps = await find_comps(
            session, "Toyota", "Land Cruiser", year=2018,
            mileage_km=80000, spec="GCC", country="AE", city="Dubai",
        )

    assert len(comps) >= 15, f"Expected >= 15 comps, got {len(comps)}"
    # Best comps should be GCC spec, Dubai, close mileage
    top = comps[0]
    assert top.make == "Toyota"
    assert top.relevance_score > 70
    # Platform attribution present
    assert top.platform_name in ["Dubizzle UAE", "YallaMotor"]
    assert "Dubai" in top.found_on_text or "Dubizzle" in top.found_on_text


@pytest.mark.asyncio
async def test_valuate_returns_estimate(populated_db):
    """Full valuation for a 2018 GCC Land Cruiser in Dubai."""
    async with populated_db() as session:
        result = await valuate(
            session, "Toyota", "Land Cruiser", year=2018,
            mileage_km=80000, spec="GCC", country="AE", city="Dubai",
        )

    assert result.confidence in ("high", "medium"), f"Expected high or medium confidence, got {result.confidence}"
    assert result.comp_count >= 10, f"Expected >= 10 comps, got {result.comp_count}"
    assert 110000 <= result.estimate <= 150000, f"Estimate {result.estimate} outside expected range 110K-150K"
    assert result.price_low < result.estimate < result.price_high

    # Check adjustments
    assert any(a.reason == "mileage" for a in result.adjustments)

    # Check comp attribution
    assert len(result.comps) >= 5
    for comp in result.comps:
        assert "found_on" in comp
        assert comp["platform"] in ["Dubizzle UAE", "YallaMotor"]


@pytest.mark.asyncio
async def test_us_spec_valued_lower(populated_db):
    """US spec Land Cruiser should be valued lower than GCC spec."""
    async with populated_db() as session:
        gcc_result = await valuate(
            session, "Toyota", "Land Cruiser", year=2018,
            mileage_km=80000, spec="GCC", country="AE", city="Dubai",
        )
        us_result = await valuate(
            session, "Toyota", "Land Cruiser", year=2018,
            mileage_km=80000, spec="US", country="AE", city="Dubai",
        )

    assert us_result.estimate < gcc_result.estimate, \
        f"US spec ({us_result.estimate}) should be cheaper than GCC ({gcc_result.estimate})"


@pytest.mark.asyncio
async def test_insufficient_data_for_rare_car(populated_db):
    """Rare car with no comps returns insufficient confidence."""
    async with populated_db() as session:
        result = await valuate(
            session, "Ferrari", "488", year=2022,
            mileage_km=10000, spec="GCC", country="AE", city="Dubai",
        )

    assert result.confidence == "insufficient"
    assert result.comp_count < 5


@pytest.mark.asyncio
async def test_deal_indicator_logic():
    """Test deal indicator thresholds."""
    from src.api.routes.valuation import _compute_deal_indicator
    from src.engine.statistical import ValuationResult

    result = ValuationResult(
        estimate=130000, price_low=120000, price_high=140000,
        confidence="high", comp_count=30, comps=[],
        adjustments=[], segment_median=130000,
    )

    # Great deal: below range
    indicator, desc = _compute_deal_indicator(100000, result)
    assert indicator == "great_deal"

    # Fair deal: in range
    indicator, desc = _compute_deal_indicator(130000, result)
    assert indicator == "fair_deal"

    # Above market
    indicator, desc = _compute_deal_indicator(150000, result)
    assert indicator == "above_market"

    # No asking price → no indicator
    indicator, desc = _compute_deal_indicator(None, result)
    assert indicator is None
