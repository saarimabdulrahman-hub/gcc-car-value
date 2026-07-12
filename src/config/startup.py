"""Startup validation — checks secrets and configuration before the app starts.

Runs before FastAPI app creation. Fails fast with clear error messages if
any security-critical configuration is missing, weak, or insecure.

Usage (in main.py, before app = FastAPI()):
    from src.config.startup import validate_startup
    validate_startup()  # raises StartupError if insecure
"""

import re
import structlog
from src.config.secrets import (
    SecretName, SECRET_POLICIES, get_secret_provider, mask_sensitive_value,
)

logger = structlog.get_logger()


class StartupError(RuntimeError):
    """Raised when the application cannot start due to configuration issues."""


class SecretValidationError(StartupError):
    """Raised when a required secret fails validation."""


async def validate_startup() -> None:
    """Run all startup validations. Raises StartupError on failure."""
    provider = get_secret_provider()

    errors: list[str] = []

    # Validate each secret with a defined policy
    for secret_name, policy in SECRET_POLICIES.items():
        value = await provider.get(secret_name.value)

        # Check required secrets
        if value is None:
            if policy.get("require_no_default"):
                errors.append(
                    f"{secret_name.value}: REQUIRED but not found. "
                    f"Set via {provider.source_name}. "
                    f"Description: {policy['description']}"
                )
            continue

        # Check minimum length
        min_length = policy.get("min_length", 0)
        if len(value) < min_length:
            errors.append(
                f"{secret_name.value}: too short "
                f"({len(value)} chars, minimum {min_length}). "
                f"Description: {policy['description']}"
            )

        # Check for default/example values
        default_indicators = policy.get("default_indicators", [])
        value_lower = value.lower()
        for indicator in default_indicators:
            if indicator in value_lower:
                errors.append(
                    f"{secret_name.value}: appears to be a default/example value "
                    f"(contains '{indicator}'). "
                    f"Replace with a strong generated secret."
                )
                break

    # Validate JWT secret specifically (most critical)
    jwt_value = await provider.get(SecretName.JWT_SECRET.value)
    if jwt_value:
        _validate_jwt_secret_strength(jwt_value, errors)

    # Validate database URL format (no password in loggable URLs)
    db_url = await provider.get(SecretName.DATABASE_URL.value)
    if db_url:
        _validate_database_url(db_url, errors)

    if errors:
        error_msg = "Startup validation failed:\n  - " + "\n  - ".join(errors)
        logger.critical("startup_validation_failed",
                       error_count=len(errors),
                       provider=provider.source_name)
        raise StartupError(error_msg)

    logger.info("startup_validation_passed",
                provider=provider.source_name,
                secrets_checked=len(SECRET_POLICIES))


def _validate_jwt_secret_strength(value: str, errors: list[str]) -> None:
    """JWT-specific strength checks."""
    # Check entropy: at least 2 of [uppercase, lowercase, digits, special chars]
    categories = 0
    if re.search(r'[A-Z]', value):
        categories += 1
    if re.search(r'[a-z]', value):
        categories += 1
    if re.search(r'[0-9]', value):
        categories += 1
    if re.search(r'[^A-Za-z0-9]', value):
        categories += 1
    if categories < 2:
        errors.append(
            f"JWT_SECRET: insufficient complexity. "
            f"Use at least 2 of: uppercase, lowercase, digits, special chars."
        )

    # Check length
    if len(value) < 32:
        errors.append(
            f"JWT_SECRET: too short ({len(value)} chars, minimum 32). "
            f"Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Check common patterns
    common = ["secret", "password", "1234", "abcd", "test", "dev", "admin"]
    value_lower = value.lower()
    for pattern in common:
        if pattern in value_lower:
            errors.append(
                f"JWT_SECRET: contains common weak pattern '{pattern}'."
            )
            break


def _validate_database_url(db_url: str, errors: list[str]) -> None:
    """Check database URL format."""
    if not db_url.startswith(("postgresql://", "postgresql+asyncpg://",
                              "sqlite://")):
        errors.append(
            f"DATABASE_URL: must start with postgresql://, "
            f"postgresql+asyncpg://, or sqlite://"
        )


def generate_secure_jwt_secret() -> str:
    """Generate a cryptographically secure JWT secret.

    Usage:
        python -c "from src.config.startup import generate_secure_jwt_secret; print(generate_secure_jwt_secret())"
    """
    import secrets
    return secrets.token_hex(32)
