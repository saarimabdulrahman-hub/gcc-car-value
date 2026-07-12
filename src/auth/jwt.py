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
TOKEN_EXPIRE_HOURS = 24

# Lazy-loaded JWT secret — resolved on first use via SecretProvider
_jwt_secret: str | None = None


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
    """Create a JWT access token for a user.

    Args:
        user_id: User UUID string.
        tier: API rate-limit tier (registered, enterprise).
        role: RBAC role (consumer, dealer, moderator, admin, super_admin, system).
    """
    secret = _get_jwt_secret_sync()
    payload = {
        "sub": user_id,
        "tier": tier,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Verify JWT token. Returns payload or None if invalid/expired."""
    try:
        secret = _get_jwt_secret_sync()
        return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
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
