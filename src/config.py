from pydantic_settings import BaseSettings
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
    api_cors_origins: list[str] = ["http://localhost:3000"]
    api_title: str = "GCC Car Value API"
    api_version: str = "1.0.0"

    # Observability
    log_level: str = "INFO"
    otel_enabled: bool = False

    # Environment
    environment: str = "development"  # development, staging, production

    # Auth
    jwt_secret: str = "dev-secret-change-in-production-gcc-car-value-2026"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
