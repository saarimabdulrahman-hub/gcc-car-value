from slowapi import Limiter
from slowapi.util import get_remote_address
from src.db.session import get_session as get_db

limiter = Limiter(key_func=get_remote_address)

from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def require_api_key(
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> dict:
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    from sqlalchemy import text
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    result = await db.execute(
        text("SELECT id, email, role FROM user_accounts WHERE api_key_hash = :hash AND is_active = true"),
        {"hash": hashed}
    )
    user = result.fetchone()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return {"id": user.id, "email": user.email, "role": user.role}
