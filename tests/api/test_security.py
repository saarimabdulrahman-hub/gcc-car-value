"""Security tests — CORS allowlist and response security headers.

These enforce the Phase 5 hardening gate:
  - unapproved origins are rejected by CORS
  - approved origins are allowed
  - security headers are present on every response

The app reads CORS config at import time (module-level middleware wiring), so
these tests build a fresh app in a subprocess-free way by reloading the module
with the desired environment. To keep it simple and fast, we assert against a
freshly configured app instance per scenario.
"""

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _build_app(monkeypatch, **env):
    """Reload the FastAPI app with the given environment overrides applied."""
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # Settings + app are configured at import time — reload both.
    from src.config import settings as settings_module
    settings_module.get_settings.cache_clear()
    import src.api.main as main_module
    importlib.reload(main_module)
    return main_module.app


APPROVED = "https://gcc-car-value.vercel.app"
UNAPPROVED = "https://evil.example.com"
RENDER_CONFIG = Path(__file__).resolve().parents[2] / "render.yaml"


@pytest.fixture
def prod_client(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "Xk9#mN5^pQ8&rT1@vW4aL3bZ7cY2jU6wE0")
    app = _build_app(
        monkeypatch,
        ENVIRONMENT="production",
        SECRET_PROVIDER="environment",
        API_CORS_ORIGINS=APPROVED,
    )
    with TestClient(app) as c:
        yield c
    # Restore module state so later tests see the ambient (testing) config.
    # monkeypatch reverts the env vars after this fixture, but the reloaded
    # module holds a production-configured `app` — reload it back to avoid
    # polluting tests that import src.api.main afterwards.
    monkeypatch.undo()
    from src.config import settings as settings_module
    settings_module.get_settings.cache_clear()
    import src.api.main as main_module
    importlib.reload(main_module)


class TestCORS:
    def test_render_allows_production_frontend(self):
        """Deployment config must supply the canonical frontend allowlist."""
        render_config = RENDER_CONFIG.read_text(encoding="utf-8")
        assert "API_CORS_ORIGINS" in render_config
        assert APPROVED in render_config

    def test_approved_origin_allowed(self, prod_client):
        r = prod_client.get("/v1/health/live", headers={"Origin": APPROVED})
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == APPROVED

    def test_unapproved_origin_rejected(self, prod_client):
        """An unapproved origin must NOT receive an ACAO header echoing it."""
        r = prod_client.get("/v1/health/live", headers={"Origin": UNAPPROVED})
        acao = r.headers.get("access-control-allow-origin")
        assert acao != UNAPPROVED
        assert acao != "*"

    def test_preflight_unapproved_origin_rejected(self, prod_client):
        r = prod_client.options(
            "/v1/valuate",
            headers={
                "Origin": UNAPPROVED,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert r.headers.get("access-control-allow-origin") != UNAPPROVED

    def test_no_wildcard_origin(self, prod_client):
        r = prod_client.get("/v1/health/live", headers={"Origin": APPROVED})
        assert r.headers.get("access-control-allow-origin") != "*"


class TestSecurityHeaders:
    def test_content_type_options(self, prod_client):
        r = prod_client.get("/v1/health/live")
        assert r.headers.get("x-content-type-options") == "nosniff"

    def test_frame_options(self, prod_client):
        r = prod_client.get("/v1/health/live")
        assert r.headers.get("x-frame-options") == "DENY"

    def test_referrer_policy(self, prod_client):
        r = prod_client.get("/v1/health/live")
        assert r.headers.get("referrer-policy") == "strict-origin-when-cross-origin"

    def test_csp_present(self, prod_client):
        r = prod_client.get("/v1/health/live")
        csp = r.headers.get("content-security-policy", "")
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp

    def test_hsts_in_production(self, prod_client):
        r = prod_client.get("/v1/health/live")
        hsts = r.headers.get("strict-transport-security", "")
        assert "max-age=" in hsts
        assert int(hsts.split("max-age=")[1].split(";")[0]) >= 31536000
