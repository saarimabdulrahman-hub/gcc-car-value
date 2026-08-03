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


class TestProviderSelection:
    """Provider is chosen by SECRET_PROVIDER, never derived from ENVIRONMENT.

    Regression guard: production on Render must use env vars, not AWS.
    """

    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        from src.config.settings import get_settings
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    def test_environment_provider_selected_explicitly(self, monkeypatch):
        monkeypatch.setenv("SECRET_PROVIDER", "environment")
        monkeypatch.setenv("ENVIRONMENT", "production")  # must NOT force AWS
        reset_secret_provider()
        provider = get_secret_provider()
        assert isinstance(provider, EnvironmentProvider)
        assert provider.source_name == "environment"

    def test_production_env_does_not_imply_aws(self, monkeypatch):
        """The old bug: ENVIRONMENT=production selected AWS. It must not."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("SECRET_PROVIDER", raising=False)  # default applies
        reset_secret_provider()
        provider = get_secret_provider()
        assert isinstance(provider, EnvironmentProvider)

    def test_aws_provider_selected_explicitly(self, monkeypatch):
        from src.config.secrets import AwsSecretsManagerProvider
        monkeypatch.setenv("SECRET_PROVIDER", "aws")
        monkeypatch.setenv("ENVIRONMENT", "production")
        reset_secret_provider()
        provider = get_secret_provider()
        assert isinstance(provider, AwsSecretsManagerProvider)
        assert provider.source_name == "aws-secrets-manager"

    def test_invalid_provider_rejected(self, monkeypatch):
        from src.config.settings import Settings
        with pytest.raises(ValueError, match="SECRET_PROVIDER"):
            Settings(_env_file=None, secret_provider="vault",
                     jwt_secret="x" * 40)

    @pytest.mark.asyncio
    async def test_environment_provider_reads_render_style_secret(self, monkeypatch):
        """Render supplies JWT_SECRET as an env var; provider must return it."""
        monkeypatch.setenv("SECRET_PROVIDER", "environment")
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET", "R3nd3r" + "a" * 40)
        reset_secret_provider()
        provider = get_secret_provider()
        value = await provider.get(SecretName.JWT_SECRET.value)
        assert value == "R3nd3r" + "a" * 40
