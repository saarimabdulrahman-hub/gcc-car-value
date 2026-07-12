"""Test SecretProvider — environment provider, masking, policies."""
import os
import pytest
from src.config.secrets import (
    EnvironmentProvider, SecretName, mask_sensitive_value, MASKED,
    SECRET_POLICIES, get_secret_provider, reset_secret_provider,
)


@pytest.fixture(autouse=True)
def reset_provider():
    """Reset singleton between tests."""
    reset_secret_provider()
    yield
    reset_secret_provider()


class TestEnvironmentProvider:
    @pytest.mark.asyncio
    async def test_get_existing_var(self):
        os.environ["TEST_SECRET_VAR"] = "my-test-value"
        provider = EnvironmentProvider()
        value = await provider.get("TEST_SECRET_VAR")
        assert value == "my-test-value"
        del os.environ["TEST_SECRET_VAR"]

    @pytest.mark.asyncio
    async def test_get_missing_var_returns_none(self):
        provider = EnvironmentProvider()
        value = await provider.get("NONEXISTENT_VAR_XYZ123")
        assert value is None

    @pytest.mark.asyncio
    async def test_get_missing_var_with_default(self):
        provider = EnvironmentProvider()
        value = await provider.get("NONEXISTENT_VAR", default="fallback")
        assert value == "fallback"

    @pytest.mark.asyncio
    async def test_provider_is_always_ready(self):
        provider = EnvironmentProvider()
        assert await provider.ready()

    def test_source_name(self):
        provider = EnvironmentProvider()
        assert provider.source_name == "environment"


class TestSecretMasking:
    def test_masks_jwt_secret_key(self):
        assert mask_sensitive_value("JWT_SECRET", "abc123") == MASKED

    def test_masks_password_key(self):
        assert mask_sensitive_value("DB_PASSWORD", "secret") == MASKED

    def test_masks_api_key_key(self):
        assert mask_sensitive_value("CLAUDE_API_KEY", "sk-abc") == MASKED

    def test_masks_token_in_value(self):
        assert mask_sensitive_value("auth_header", "gccv_abc123") == MASKED

    def test_does_not_mask_non_sensitive_keys(self):
        assert mask_sensitive_value("DATABASE_URL",
            "postgresql://localhost/db") != MASKED

    def test_does_not_mask_environment_name(self):
        assert mask_sensitive_value("ENVIRONMENT", "production") == "production"

    def test_none_value_returns_none(self):
        assert mask_sensitive_value("JWT_SECRET", None) is None


class TestSecretPolicies:
    def test_jwt_secret_has_min_length_32(self):
        assert SECRET_POLICIES[SecretName.JWT_SECRET]["min_length"] == 32

    def test_jwt_secret_require_no_default(self):
        assert SECRET_POLICIES[SecretName.JWT_SECRET]["require_no_default"]

    def test_jwt_secret_rejects_dev_secret_indicator(self):
        indicators = SECRET_POLICIES[SecretName.JWT_SECRET]["default_indicators"]
        assert "dev-secret" in indicators
        assert "change-in-production" in indicators

    def test_all_secret_names_have_policies_or_are_optional(self):
        for name in SecretName:
            if name in SECRET_POLICIES:
                policy = SECRET_POLICIES[name]
                assert "description" in policy


class TestProviderFactory:
    def test_environment_provider_in_dev(self):
        # Default environment is development
        provider = get_secret_provider()
        assert isinstance(provider, EnvironmentProvider)
