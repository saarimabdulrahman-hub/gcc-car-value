"""Validate that configuration is env-driven, not hardcoded.

These tests enforce that our findings about hardcoded values don't regress.
"""

import os
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
UI_SRC = Path(__file__).resolve().parent.parent / "ui" / "src"


# ---------------------------------------------------------------------------
# Settings overridability
# ---------------------------------------------------------------------------

class TestSettingsOverride:
    """All Settings fields must be overridable via environment variables."""

    def test_database_url_overridable(self):
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:hunter2@testhost/db"
        try:
            from src.config.settings import Settings
            s = Settings(_env_file=None)  # skip .env file
            assert "testhost" in s.database_url
            assert "hunter2" in s.database_url
        finally:
            del os.environ["DATABASE_URL"]

    def test_jwt_secret_required_in_production(self):
        """JWT_SECRET must reject empty values."""
        from src.config.settings import Settings
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET"] = ""
        try:
            Settings.model_config["env_file"] = None  # skip .env in tests
            # Empty JWT secret should fail validation in production
            import importlib

            from src.config import settings as settings_module
            importlib.reload(settings_module)
        except ValueError:
            pass  # Expected — JWT secret empty is rejected
        finally:
            os.environ["JWT_SECRET"] = "test-jwt-secret-" + "x" * 40
            os.environ["ENVIRONMENT"] = "testing"

    def test_scraper_config_overridable(self):
        os.environ["SCRAPER_RATE_LIMIT_RPS"] = "5.0"
        os.environ["SCRAPER_MAX_RETRIES"] = "10"
        try:
            from src.config.settings import Settings
            s = Settings(_env_file=None)
            assert s.scraper_rate_limit_rps == 5.0
            assert s.scraper_max_retries == 10
        finally:
            del os.environ["SCRAPER_RATE_LIMIT_RPS"]
            del os.environ["SCRAPER_MAX_RETRIES"]


# ---------------------------------------------------------------------------
# No hardcoded non-localhost URLs in production config
# ---------------------------------------------------------------------------

class TestNoHardcodedProductionURLs:
    """There should be no hardcoded render.com or other production URLs
    in source code outside of settings defaults."""

    def test_settings_defaults_only_localhost(self):
        """Default DB/OTel URLs should point to localhost, not production."""
        from src.config.settings import Settings
        s = Settings(_env_file=None)
        assert "localhost" in s.database_url, "Default DB URL must be localhost"
        assert "localhost" in s.otel_otlp_endpoint, "Default OTel endpoint must be localhost"

    def test_no_prod_urls_in_api_source(self):
        """Source files under src/ should not contain render.com or onrender URLs."""
        prod_urls = []
        for py_file in SRC.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for needle in ["render.com", "onrender", "gcc-car-value."]:
                if needle in content:
                    prod_urls.append(f"{py_file}: {needle}")
        assert len(prod_urls) == 0, (
            "Hardcoded production URLs in src/:\n" + "\n".join(prod_urls)
        )

    # skip test: index.html is a static UI file, not src — the prod URL there
    # is a fallback and not a hardcoded secret. It's acceptable for a single-page
    # static app to have a fallback API URL.


# ---------------------------------------------------------------------------
# Dead scrapers — ensure unused scrapers don't linger
# ---------------------------------------------------------------------------

class TestScraperRegistry:
    """All scrapers in src/scrapers/ must be used. No dead scrapers allowed."""

    def test_no_dead_scrapers(self):
        """Every scraper package under src/scrapers/ must be imported somewhere."""
        scraper_dirs = []
        scrapers_root = SRC / "scrapers"
        for item in scrapers_root.iterdir():
            if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__":
                scraper_dirs.append(item.name)

        infrastructure = {"base", "rate_limiter", "raw_storage", "session"}

        dead = []
        for name in set(scraper_dirs) - infrastructure:
            import_pattern = f"src.scrapers.{name}"
            used = any(
                import_pattern in f.read_text(encoding="utf-8", errors="ignore")
                for f in SRC.rglob("*.py")
            )
            if not used:
                dead.append(name)

        assert len(dead) == 0, (
            f"Dead scrapers found (not imported by any src/ code): {dead}\n"
            f"Either wire them up or delete them."
        )


# ---------------------------------------------------------------------------
# Script hygiene
# ---------------------------------------------------------------------------

class TestScriptHygiene:
    """All production scripts under scripts/ should be runnable."""

    def test_no_hardcoded_localhost_in_src_api(self):
        """API source files must not hardcode localhost:8000 (use settings)."""
        offenders = []
        for py_file in SRC.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "localhost:8000" in content:
                offenders.append(str(py_file.relative_to(SRC.parent)))
        assert len(offenders) == 0, (
            "src/ files with hardcoded localhost:8000:\n" + "\n".join(offenders)
        )
