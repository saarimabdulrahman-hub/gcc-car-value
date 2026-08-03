import pytest
from httpx import AsyncClient, ASGITransport
from src.api.main import app

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_watchlist_auth_required(client: AsyncClient):
    # GET /watchlist
    res = await client.get("/v1/watchlist")
    assert res.status_code == 401

    # POST /watchlist
    res = await client.post("/v1/watchlist", json={
        "make": "Toyota", "model": "Camry", "year": 2020
    })
    assert res.status_code == 401

    # DELETE /watchlist/{item_id}
    res = await client.delete("/v1/watchlist/some-uuid-here")
    assert res.status_code == 401

    # GET /notifications
    res = await client.get("/v1/notifications")
    assert res.status_code == 401
