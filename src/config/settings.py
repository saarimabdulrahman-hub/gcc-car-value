from pydantic_settings import BaseSettings
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
    quality_promotion_threshold: int = 60

    # API
    api_rate_limit_anonymous: str = "10/minute"
    api_rate_limit_registered: str = "30/minute"
    api_cors_origins: list[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://gcc-car-value.vercel.app",
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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
