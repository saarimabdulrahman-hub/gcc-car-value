"""Test URL security validation — SSRF protection."""
import pytest

from src.api.security import validate_public_url


class TestValidatePublicUrl:
    def test_allows_legitimate_car_marketplace_urls(self):
        assert validate_public_url("https://uae.dubizzle.com/car-listing/12345") is not None
        assert validate_public_url("https://yallamotor.com/used-cars/toyota") is not None

    def test_rejects_non_http_schemes(self):
        with pytest.raises(ValueError, match="Only http and https"):
            validate_public_url("file:///etc/passwd")
        with pytest.raises(ValueError, match="Only http and https"):
            validate_public_url("gopher://localhost/")

    def test_rejects_loopback(self):
        with pytest.raises(ValueError, match="internal or private"):
            validate_public_url("http://127.0.0.1:8000/admin", allow_all_domains=True)
        with pytest.raises(ValueError, match="internal or private"):
            validate_public_url("http://localhost:5432/", allow_all_domains=True)

    def test_rejects_private_ips(self):
        for ip in ["10.0.0.1", "172.16.0.1", "192.168.1.1"]:
            with pytest.raises(ValueError, match="internal or private"):
                validate_public_url(f"http://{ip}/", allow_all_domains=True)

    def test_rejects_cloud_metadata(self):
        with pytest.raises(ValueError, match="internal or private"):
            validate_public_url("http://169.254.169.254/latest/meta-data/", allow_all_domains=True)

    def test_rejects_url_without_hostname(self):
        with pytest.raises(ValueError, match="valid hostname"):
            validate_public_url("http://")

    def test_rejects_oversized_url(self):
        long_url = "http://example.com/" + "x" * 2048
        with pytest.raises(ValueError, match="too long"):
            validate_public_url(long_url)

    def test_rejects_unknown_domain_when_allowlist_active(self):
        with pytest.raises(ValueError, match="known car marketplaces"):
            validate_public_url("https://evil.com/listing")

    def test_allow_all_domains_flag_bypasses_domain_check(self):
        # In dev/testing, allow_all_domains=True skips the domain allowlist
        assert validate_public_url("https://example.com/car", allow_all_domains=True) is not None
