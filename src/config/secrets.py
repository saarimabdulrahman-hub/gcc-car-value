"""SecretProvider abstraction for centralized secrets management.

All sensitive configuration (JWT secrets, DB passwords, API keys) flows through
a SecretProvider. The application never calls os.getenv() directly for secrets.

Providers:
    EnvironmentProvider  — reads from environment variables (local dev, Docker)
    AwsSecretsManager    — reads from AWS Secrets Manager (production)

Usage:
    from src.config.secrets import get_secret_provider
    provider = get_secret_provider()
    jwt_secret = await provider.get("JWT_SECRET")
"""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any
import os
import re
import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Secret definitions — every secret the application needs
# ---------------------------------------------------------------------------

class SecretName(StrEnum):
    JWT_SECRET = "JWT_SECRET"
    DATABASE_URL = "DATABASE_URL"       # contains password inline
    DATABASE_PASSWORD = "DATABASE_PASSWORD"
    S3_ACCESS_KEY = "S3_ACCESS_KEY"
    S3_SECRET_KEY = "S3_SECRET_KEY"
    CLAUDE_API_KEY = "CLAUDE_API_KEY"
    VIN_API_KEY = "VIN_API_KEY"


# ---------------------------------------------------------------------------
# Secret metadata — strength requirements per secret
# ---------------------------------------------------------------------------

SECRET_POLICIES: dict[str, dict[str, Any]] = {
    SecretName.JWT_SECRET: {
        "min_length": 32,
        "description": "JWT HS256 signing key",
        "require_no_default": True,
        "default_indicators": [
            "dev-secret", "change-me", "change-in-production",
            "replace-me", "your-secret", "example",
        ],
    },
    SecretName.DATABASE_PASSWORD: {
        "min_length": 8,
        "description": "PostgreSQL master password",
    },
    SecretName.S3_SECRET_KEY: {
        "min_length": 8,
        "description": "AWS S3 secret access key",
    },
    SecretName.CLAUDE_API_KEY: {
        "min_length": 16,
        "description": "Anthropic Claude API key",
    },
}


# ---------------------------------------------------------------------------
# Secret mask for logging — prevents accidental exposure
# ---------------------------------------------------------------------------

_SENSITIVE_KEY_PATTERNS = re.compile(
    r'(secret|password|token|key|api_key|credential|database_url)',
    re.IGNORECASE,
)

# Values matching these patterns are masked in logs
_SENSITIVE_VALUE_PATTERNS = [
    re.compile(r'^sk-'),           # OpenAI/Claude API keys
    re.compile(r'^gccv_'),         # Our API keys
    re.compile(r'^AKIA'),          # AWS access keys
]

MASKED = "***MASKED***"


def mask_sensitive_value(key: str, value: Any) -> Any:
    """Mask a value if the key looks like a secret name.

    Returns MASKED string for sensitive values, original value otherwise.
    Database URLs have their inline password masked but the structure preserved.
    """
    if value is None:
        return None
    if _SENSITIVE_KEY_PATTERNS.search(key):
        # Special handling: mask just the password in database URLs
        if 'database_url' in key.lower() or 'DATABASE_URL' in key:
            return _mask_database_url_password(str(value))
        return MASKED
    value_str = str(value)
    for pattern in _SENSITIVE_VALUE_PATTERNS:
        if pattern.search(value_str):
            return MASKED
    return value


def _mask_database_url_password(url: str) -> str:
    """Replace the password in a database URL with ***MASKED***.

    Example:
        postgresql://user:secret@host:5432/db
        → postgresql://user:***MASKED***@host:5432/db
    """
    import re as _re
    return _re.sub(
        r'(://[^:]+:)([^@]+)(@)',
        r'\1***MASKED***\3',
        url
    )


# ---------------------------------------------------------------------------
# SecretProvider interface
# ---------------------------------------------------------------------------

class SecretProvider(ABC):
    """Abstract secret provider. All implementations are async for consistency."""

    @abstractmethod
    async def get(self, name: str, default: str | None = None) -> str | None:
        """Retrieve a secret value. Returns None if not found."""
        ...

    @abstractmethod
    async def ready(self) -> bool:
        """Check if the provider is operational."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable provider name for logging."""
        ...


# ---------------------------------------------------------------------------
# Environment variable provider (local dev, Docker Compose)
# ---------------------------------------------------------------------------

class EnvironmentProvider(SecretProvider):
    """Reads secrets from environment variables (.env file or Docker env)."""

    source_name = "environment"

    async def get(self, name: str, default: str | None = None) -> str | None:
        value = os.getenv(name, default)
        if value:
            logger.debug("secret_read", provider="environment", name=name,
                        value=mask_sensitive_value(name, value))
        return value

    async def ready(self) -> bool:
        return True  # Always ready — env vars are available immediately


# ---------------------------------------------------------------------------
# AWS Secrets Manager provider (production)
# ---------------------------------------------------------------------------

class AwsSecretsManagerProvider(SecretProvider):
    """Reads secrets from AWS Secrets Manager.

    Secret names in AWS are prefixed with the environment:
        gcc-car-value-production-database-url
        gcc-car-value-production-jwt-secret
    """

    source_name = "aws-secrets-manager"

    def __init__(self, environment: str = "production",
                 region: str = "me-central-1"):
        self._environment = environment
        self._region = region
        self._client = None
        self._cache: dict[str, str | None] = {}

    async def get(self, name: str, default: str | None = None) -> str | None:
        # Check cache first
        if name in self._cache:
            return self._cache[name]

        client = self._get_client()
        if client is None:
            logger.warning("secrets_manager_unavailable",
                          name=name, fallback="default")
            return default

        secret_id = f"gcc-car-value-{self._environment}-{name.lower().replace('_', '-')}"
        try:
            response = client.get_secret_value(SecretId=secret_id)
            value = response.get("SecretString")
            if value:
                # AWS stores values as JSON: {"KEY": "value"}
                import json
                try:
                    data = json.loads(value)
                    if isinstance(data, dict) and name in data:
                        value = data[name]
                except json.JSONDecodeError:
                    pass  # Plain string, use as-is
            self._cache[name] = value
            logger.debug("secret_read", provider="aws-secrets-manager",
                        name=name, value=mask_sensitive_value(name, value))
            return value
        except Exception as e:
            logger.warning("secrets_manager_read_failed",
                          secret_id=secret_id, error=str(e)[:200])
            return default

    async def ready(self) -> bool:
        try:
            client = self._get_client()
            if client is None:
                return False
            # Test connectivity
            client.get_secret_value(SecretId="gcc-car-value-health-check")
            return True
        except Exception:
            return False

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import boto3
            self._client = boto3.client(
                "secretsmanager",
                region_name=self._region,
            )
            return self._client
        except Exception as e:
            logger.error("secrets_manager_client_failed", error=str(e)[:200])
            return None

    def invalidate_cache(self) -> None:
        """Clear cache (for secret rotation)."""
        self._cache.clear()
        logger.info("secrets_cache_invalidated")


# ---------------------------------------------------------------------------
# Provider factory — returns the right provider based on environment
# ---------------------------------------------------------------------------

_provider: SecretProvider | None = None


def get_secret_provider() -> SecretProvider:
    """Get or create the singleton SecretProvider.

    Uses AWS Secrets Manager in production, environment variables otherwise.
    """
    global _provider
    if _provider is not None:
        return _provider

    from src.config import get_settings
    settings = get_settings()
    env = settings.environment

    if env == "production":
        _provider = AwsSecretsManagerProvider(
            environment=env,
            region=settings.s3_region,
        )
    else:
        _provider = EnvironmentProvider()

    logger.info("secret_provider_initialized",
                provider=_provider.source_name,
                environment=env)
    return _provider


def reset_secret_provider() -> None:
    """Reset the provider singleton (for testing)."""
    global _provider
    _provider = None
