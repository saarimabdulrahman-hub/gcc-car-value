"""Test auth dependencies — token creation, verification, and dependency behavior."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from src.auth.jwt import create_access_token, verify_token, create_api_key, verify_api_key


class TestJWT:
    def test_create_and_verify_token(self):
        token = create_access_token("user-123", tier="registered", role="consumer")
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["tier"] == "registered"
        assert payload["role"] == "consumer"

    def test_token_with_admin_role(self):
        token = create_access_token("admin-456", tier="enterprise", role="admin")
        payload = verify_token(token)
        assert payload["role"] == "admin"
        assert payload["tier"] == "enterprise"

    def test_verify_invalid_token_returns_none(self):
        assert verify_token("not.a.valid.token") is None
        assert verify_token("") is None

    def test_verify_tampered_token_returns_none(self):
        token = create_access_token("user-123")
        # Tamper with the payload portion
        parts = token.split(".")
        tampered = parts[0] + "." + "tampered" + "." + parts[2]
        assert verify_token(tampered) is None

    def test_role_included_in_payload(self):
        token = create_access_token("user-789", role="moderator")
        payload = verify_token(token)
        assert payload["role"] == "moderator"


class TestAPIKeys:
    def test_create_and_verify_api_key(self):
        raw, hashed = create_api_key()
        assert raw.startswith("gccv_")
        assert len(raw) == 37  # "gccv_" + 32 hex chars
        assert verify_api_key(raw, hashed)

    def test_verify_wrong_key_fails(self):
        raw, hashed = create_api_key()
        wrong_key = "gccv_" + "0" * 32
        assert not verify_api_key(wrong_key, hashed)

    def test_api_keys_are_unique(self):
        raw1, hash1 = create_api_key()
        raw2, hash2 = create_api_key()
        assert raw1 != raw2
        assert hash1 != hash2
