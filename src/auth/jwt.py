"""JWT authentication — create/verify tokens, user management."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from src.config import get_settings

settings = get_settings()
JWT_SECRET = getattr(settings, 'jwt_secret', secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def create_access_token(user_id: str, tier: str = "registered") -> str:
    """Create a JWT access token for a user."""
    payload = {
        "sub": user_id,
        "tier": tier,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Verify JWT token. Returns payload or None if invalid/expired."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def create_api_key() -> tuple[str, str]:
    """Generate API key + hash pair. Returns (raw_key, hashed_key)."""
    raw = f"gccv_{secrets.token_hex(16)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash."""
    return hashlib.sha256(raw_key.encode()).hexdigest() == stored_hash
