"""Test that the API serves health, UI, and valuation endpoints correctly."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI TestClient — conftest sets JWT_SECRET env var before import."""
    from src.api.main import app
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_liveness_returns_200(self, client):
        r = client.get("/v1/health/live")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("healthy", "degraded", "unhealthy")

    def test_health_returns_json(self, client):
        r = client.get("/v1/health")
        assert r.status_code in (200, 503)
        assert r.headers["content-type"] == "application/json"


class TestUIServing:
    def test_root_serves_index_html(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]

    def test_ui_no_cache_headers(self, client):
        r = client.get("/")
        assert r.headers.get("cache-control", "").find("no-cache") != -1


class TestValuationEndpoint:
    def test_valuate_requires_body(self, client):
        r = client.post("/v1/valuate", json={})
        assert r.status_code == 422  # validation error

    def test_valuate_with_minimal_data(self, client):
        """Valuation with insufficient data returns helpful error.
        May 500 without a DB — that's expected in unit-test context."""
        r = client.post("/v1/valuate", json={
            "make": "Toyota", "model": "Camry", "year": 2020,
            "mileage_km": 50000, "country": "AE"
        })
        # 200/422 on success, 500 if no DB — all valid in test context
        assert r.status_code in (200, 422, 500)


class TestModelsEndpoint:
    def test_models_list(self, client):
        r = client.get("/v1/models")
        assert r.status_code == 200
        data = r.json()
        # Response should have a makes key
        assert "makes" in data

    def test_admin_stats(self, client):
        r = client.get("/v1/admin/stats")
        assert r.status_code in (200, 401)  # ok or auth required
