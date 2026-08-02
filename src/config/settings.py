from typing import Annotated
from pydantic_settings import BaseSettings, NoDecode
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gcc_car_value"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/gcc_car_value"
    db_pool_size: int = 10
    db_max_overflow: int = 5

    # Scraping
    scraper_rate_limit_rps: float = 2.0
    scraper_max_retries: int = 3
    scraper_retry_delay_seconds: float = 5.0
    scraper_user_agent: str = "GCCCarValue/1.0 (market research bot)"
    scraper_request_timeout: int = 30

    # S3 (raw storage)
    s3_bucket: str = "gcc-car-value-raw"
    s3_endpoint_url: str | None = None  # set for localstack in dev
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_region: str = "me-central-1"

    # Quality
    quality_promotion_threshold: int = 45

    # API
    api_rate_limit_anonymous: str = "10/minute"
    api_rate_limit_registered: str = "30/minute"
    # Bearer-token auth (Authorization header), not cookies — credentials off.
    # Declared before api_cors_origins so the wildcard guard can read it.
    api_cors_allow_credentials: bool = False
    # CORS: explicit allowlist. Default is the local frontend dev server only.
    # Production sets API_CORS_ORIGINS (comma-separated or JSON) to the real
    # frontend origin(s); see render.yaml and the deployment docs.
    api_cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    api_title: str = "GCC Car Value API"
    api_version: str = "1.0.0"

    # Observability
    log_level: str = "INFO"
    otel_enabled: bool = False
    otel_exporter: str = "console"   # "console" | "otlp" | "none"
    otel_sample_rate: float = 1.0    # 1.0 = all, 0.1 = 10%
    otel_otlp_endpoint: str = "http://localhost:4317"

    # Environment
    environment: str = "development"  # development, staging, production

    # Secret provider — where secrets (JWT, DB creds, API keys) are read from.
    # "environment": process env vars (local dev, Docker, Render). Default.
    # "aws": AWS Secrets Manager (requires AWS credentials + secret entries).
    # Explicit so it is NOT derived from `environment` — production on Render
    # must use env vars, not AWS.
    secret_provider: str = "environment"

    # Auth (no default — must be provided via env var or secrets manager)
    jwt_secret: str = ""

    # External API keys (optional)
    claude_api_key: str | None = None
    vin_api_key: str | None = None

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_must_be_set(cls, v: str) -> str:
        """Reject empty JWT secret — must be configured via env var or secrets manager."""
        if not v or not v.strip():
            raise ValueError(
                "JWT_SECRET must be set to a non-empty value. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v.strip()

    @field_validator("secret_provider")
    @classmethod
    def secret_provider_must_be_known(cls, v: str) -> str:
        """Only 'environment' or 'aws' are valid secret providers."""
        allowed = {"environment", "aws"}
        vv = v.strip().lower()
        if vv not in allowed:
            raise ValueError(
                f"SECRET_PROVIDER must be one of {sorted(allowed)}, got '{v}'."
            )
        return vv

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        """Accept a JSON array, a comma-separated string, or a list.

        Env vars are strings; humans set API_CORS_ORIGINS on Render as a plain
        comma-separated list. Also tolerate JSON (["https://a","https://b"]).
        """
        if v is None or v == "":
            return []
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(o).strip() for o in parsed if str(o).strip()]
                except json.JSONDecodeError:
                    pass  # fall through to comma-split
            return [o.strip() for o in s.split(",") if o.strip()]
        if isinstance(v, (list, tuple)):
            return [str(o).strip() for o in v if str(o).strip()]
        return v  # let pydantic raise on unexpected types

    @field_validator("api_cors_origins")
    @classmethod
    def no_wildcard_with_credentials(cls, v: list[str], info) -> list[str]:
        """A wildcard origin with credentials is invalid per the CORS spec and
        is rejected by browsers. Guard against the misconfiguration explicitly."""
        if "*" in v and info.data.get("api_cors_allow_credentials"):
            raise ValueError(
                "api_cors_origins cannot be '*' when api_cors_allow_credentials "
                "is True. List explicit origins, or disable credentials."
            )
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
