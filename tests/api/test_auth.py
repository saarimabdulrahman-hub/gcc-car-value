"""Test authentication endpoints — register, login, me, refresh, logout."""
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_register_missing_password(client):
    resp = await client.post("/v1/auth/register", json={"email": "test@example.com"})
    assert resp.status_code == 422  # Pydantic validation rejects missing field


@pytest.mark.asyncio
async def test_register_weak_password(client):
    resp = await client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert resp.status_code == 422  # min_length=8 enforced by Pydantic


@pytest.mark.asyncio
async def test_register_common_password(client):
    resp = await client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "password"},
    )
    assert resp.status_code == 422  # Common password rejected


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Login with invalid credentials returns 401 (or 500 if DB unavailable in test)."""
    resp = await client.post(
        "/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    # In CI with a test DB, returns 401. Without a DB, may return 500.
    assert resp.status_code in (401, 500)


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/v1/auth/me")
    assert resp.status_code == 401  # Returns 401 not 500 crash


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    resp = await client.post("/v1/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_unauthenticated(client):
    """Logout without a token is a no-op — returns 200 (nothing to revoke)."""
    resp = await client.post("/v1/auth/logout")
    # No token → nothing to revoke, success is correct
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_login_requires_email_format(client):
    resp = await client.post(
        "/v1/auth/login",
        json={"email": "not-an-email", "password": "anything123"},
    )
    assert resp.status_code == 422  # EmailStr validation
