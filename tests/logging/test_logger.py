"""Test centralized Logger and masking."""
import pytest
from src.core.logging.logger import get_logger, Logger
from src.core.logging.filters import mask_field, mask_event_dict, MASKED


class TestLogger:
    def test_get_logger_returns_logger(self):
        log = get_logger("test.module")
        assert isinstance(log, Logger)

    def test_get_logger_caches(self):
        log1 = get_logger("test.cache")
        log2 = get_logger("test.cache")
        assert log1 is log2

    def test_info_does_not_raise(self):
        log = get_logger("test.info")
        log.info("test_event", key="value")

    def test_warning_does_not_raise(self):
        log = get_logger("test.warn")
        log.warning("test_warning", reason="test")

    def test_error_does_not_raise(self):
        log = get_logger("test.err")
        log.error("test_error", detail="something broke")

    def test_audit_injects_category(self):
        log = get_logger("test.audit")
        log.audit("admin_access", user_id="abc")

    def test_security_does_not_raise(self):
        log = get_logger("test.sec")
        log.security("auth_failed", ip="1.2.3.4")

    def test_performance_does_not_raise(self):
        log = get_logger("test.perf")
        log.performance("db_query", execution_time_ms=45.2)


class TestMasking:
    def test_masks_jwt_token_value(self):
        # JWT starts with eyJ (base64 for {"...})
        result = mask_field("auth_header", "eyJhbGciOiJIUzI1NiJ9.xxx")
        assert result == MASKED

    def test_masks_api_key_value(self):
        result = mask_field("x-api-key", "sk-ant-api03-abc123")
        assert result == MASKED

    def test_masks_our_api_key(self):
        result = mask_field("key", "gccv_a1b2c3d4e5f6a7b8c9d0e1f2")
        assert result == MASKED

    def test_masks_password_field_name(self):
        result = mask_field("db_password", "super-secret-123")
        assert result == MASKED

    def test_masks_secret_field_name(self):
        result = mask_field("jwt_secret", "whatever-value")
        assert result == MASKED

    def test_masks_token_field_name(self):
        result = mask_field("refresh_token", "abc123")
        assert result == MASKED

    def test_masks_authorization_header(self):
        result = mask_field("authorization", "Bearer eyJhbGci...")
        assert result == MASKED

    def test_masks_db_url_password(self):
        result = mask_field("DATABASE_URL",
                           "postgresql+asyncpg://user:secret123@host:5432/db")
        assert "secret123" not in result
        assert "user" in result
        assert "***MASKED***" in result

    def test_does_not_mask_normal_fields(self):
        result = mask_field("make", "Toyota")
        assert result == "Toyota"

    def test_does_not_mask_numeric_values(self):
        result = mask_field("estimate", 125000)
        assert result == 125000

    def test_none_passes_through(self):
        assert mask_field("password", None) is None


class TestMaskEventDict:
    def test_masks_sensitive_keys_in_dict(self):
        event = {
            "event": "config_loaded",
            "jwt_secret": "abc123",
            "db_password": "secret",
            "make": "Toyota",
        }
        cleaned = mask_event_dict(event)
        assert cleaned["jwt_secret"] == MASKED
        assert cleaned["db_password"] == MASKED
        assert cleaned["make"] == "Toyota"

    def test_masks_sensitive_values_in_dict(self):
        event = {
            "event": "auth_check",
            "header": "eyJhbGciOiJIUzI1NiJ9.xxx",  # JWT pattern
            "normal_field": "hello",
        }
        cleaned = mask_event_dict(event)
        assert cleaned["header"] == MASKED
        assert cleaned["normal_field"] == "hello"


class TestContextBinding:
    def test_bind_and_clear(self):
        from src.core.logging.context import bind_context, clear_context, get_context

        bind_context(request_id="req-123", user_id="user-1")
        ctx = get_context()
        assert ctx.get("request_id") == "req-123"
        assert ctx.get("user_id") == "user-1"

        clear_context()
        ctx = get_context()
        assert "request_id" not in ctx

    def test_bind_filters_none_values(self):
        from src.core.logging.context import bind_context, clear_context, get_context

        bind_context(request_id="abc", user_id=None, country=None)
        ctx = get_context()
        assert "request_id" in ctx
        assert "user_id" not in ctx  # None → filtered
        clear_context()

    def test_bind_masks_sensitive_values(self):
        from src.core.logging.context import bind_context, clear_context, get_context

        bind_context(request_id="abc", jwt_secret="secret123")
        ctx = get_context()
        assert ctx.get("jwt_secret") == "***MASKED***"
        clear_context()
