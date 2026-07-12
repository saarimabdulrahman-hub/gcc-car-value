import os
# Set JWT_SECRET before any src imports — Settings() validates it on construction
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-" + "x" * 40)

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import Settings


@pytest.fixture(autouse=True)
def setup_test_jwt_secret(monkeypatch):
    """Ensure every test has a valid JWT secret configured."""
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-" + "x" * 40)


@pytest.fixture
def settings():
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/gcc_car_value_test",
        environment="testing",
        s3_bucket="test-bucket",
        jwt_secret="test-jwt-secret-" + "x" * 40,
    )


@pytest_asyncio.fixture
async def db_session(settings):
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        from src.models.base import Base
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
