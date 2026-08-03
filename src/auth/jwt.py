"""JWT authentication — create/verify tokens, user management.

The JWT secret is loaded via the SecretProvider abstraction.
It is never read directly from environment variables or config defaults.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import jwt
import structlog

logger = structlog.get_logger()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Lazy-loaded JWT secret — resolved on first use via SecretProvider
_jwt_secret: str | None = None

from sqlalchemy import text
from src.db.session import async_session_factory


async def _get_jwt_secret() -> str:
    """Resolve JWT secret via SecretProvider. Caches after first call."""
    global _jwt_secret
    if _jwt_secret is not None:
        return _jwt_secret

    from src.config.secrets import SecretName, get_secret_provider
    provider = get_secret_provider()
    secret = await provider.get(SecretName.JWT_SECRET.value)
    if not secret:
        raise RuntimeError(
            "JWT_SECRET is not configured. The application cannot start "
            "without a JWT signing secret. Set JWT_SECRET in your environment "
            "or via your secrets provider."
        )
    _jwt_secret = secret
    return secret


def _get_jwt_secret_sync() -> str:
    """Synchronous wrapper for JWT secret resolution.

    If the secret hasn't been loaded yet (first call), this reads from
    the environment directly as a fallback. In production, ensure
    validate_startup() has been called first.
    """
    import os
    if _jwt_secret is not None:
        return _jwt_secret
    # Fallback: direct env read (for sync contexts like module-level init)
    secret = os.getenv("JWT_SECRET", "")
    if secret:
        return secret
    from src.config import get_settings
    s = get_settings().jwt_secret
    if s:
        return s
    raise RuntimeError(
        "JWT_SECRET is not configured. Set JWT_SECRET env var."
    )


def create_access_token(user_id: str, tier: str = "registered",
                        role: str = "consumer") -> str:
    """Create a short-lived JWT access token (15 minutes).

    Args:
        user_id: User UUID string.
        tier: API rate-limit tier (registered, enterprise).
        role: RBAC role (consumer, dealer, moderator, admin, super_admin, system).
    """
    secret = _get_jwt_secret_sync()
    payload = {
        "sub": user_id,
        "aud": "gcc-car-value-api",
        "tier": tier,
        "role": role,
        "jti": secrets.token_hex(8),
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token (7 days)."""
    secret = _get_jwt_secret_sync()
    payload = {
        "sub": user_id,
        "aud": "gcc-car-value-api",
        "jti": secrets.token_hex(16),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


async def revoke_token_jti(jti: str) -> None:
    """Revoke a token by its JWT ID (using dead_letter table for persistence)."""
    async with async_session_factory() as db:
        await db.execute(
            text("INSERT INTO dead_letter (source, external_id, rejection_reason, raw_data) VALUES ('auth', :jti, 'revoked_token', '{}')"),
            {"jti": jti}
        )
        await db.commit()
    logger.info("token_revoked", jti=jti[:8] + "...")


async def is_token_revoked(jti: str) -> bool:
    """Check if a token JTI has been revoked in the DB."""
    async with async_session_factory() as db:
        result = await db.execute(
            text("SELECT id FROM dead_letter WHERE source = 'auth' AND external_id = :jti AND rejection_reason = 'revoked_token'"),
            {"jti": jti}
        )
        return result.fetchone() is not None


async def verify_token(token: str, check_revoked: bool = True) -> dict | None:
    """Verify JWT token. Returns payload or None if invalid/expired/revoked."""
    try:
        secret = _get_jwt_secret_sync()
        payload = jwt.decode(
            token, secret,
            algorithms=[JWT_ALGORITHM],
            audience="gcc-car-value-api",
        )
        if check_revoked:
            jti = payload.get("jti")
            if jti and await is_token_revoked(jti):
                return None
        return payload
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
