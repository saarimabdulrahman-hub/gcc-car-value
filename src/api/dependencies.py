from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import async_session_factory

limiter = Limiter(key_func=get_remote_address)


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
