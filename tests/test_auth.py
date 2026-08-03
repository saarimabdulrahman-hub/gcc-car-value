"""JWT auth and API key tests."""
import os

import src.auth.jwt as jwt_mod

# Force-set JWT secret and reset the module-level cache
os.environ["JWT_SECRET"] = "test-jwt-secret-" + "x" * 40
jwt_mod._jwt_secret = None

from unittest.mock import patch

import pytest

from src.auth.jwt import create_access_token, create_api_key, verify_api_key, verify_token


@pytest.fixture(autouse=True)
def mock_is_token_revoked():
    with patch("src.auth.jwt.is_token_revoked", return_value=False) as mock:
        yield mock

@pytest.mark.asyncio
async def test_jwt_create_and_verify():
    token = create_access_token("user_123", tier="registered")
    payload = await verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user_123"
    assert payload["tier"] == "registered"


@pytest.mark.asyncio
async def test_jwt_invalid_token_rejected():
    assert await verify_token("bad.token.here") is None
    assert await verify_token("") is None


@pytest.mark.asyncio
async def test_jwt_different_tiers():
    enterprise_token = create_access_token("corp_456", tier="enterprise")
    payload = await verify_token(enterprise_token)
    assert payload["tier"] == "enterprise"


def test_api_key_create_and_verify():
    raw, hashed = create_api_key()
    assert raw.startswith("gccv_")
    assert len(raw) == 37  # gccv_ + 32 hex chars
    assert verify_api_key(raw, hashed)
    assert not verify_api_key("wrong_key", hashed)


def test_api_key_rotation():
    raw1, hash1 = create_api_key()
    raw2, hash2 = create_api_key()
    assert raw1 != raw2
    assert hash1 != hash2
    # Old key doesn't work with new hash
    assert not verify_api_key(raw1, hash2)
