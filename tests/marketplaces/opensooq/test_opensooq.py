"""Test OpenSooq — multi-country config, discovery, mapper, capabilities."""
import pytest
from marketplaces.opensooq.config import OpenSooqConfig
from marketplaces.opensooq.constants import COUNTRY_CONFIGS, SUPPORTED_COUNTRIES
from marketplaces.opensooq.discovery import OpenSooqDiscovery
from marketplaces.opensooq.mapper import OpenSooqMapper
from marketplaces.opensooq.capabilities import OpenSooqCapabilities


class TestCountryConfiguration:
    def test_all_countries_configured(self):
        assert len(SUPPORTED_COUNTRIES) == 6
        for cc in SUPPORTED_COUNTRIES:
            cfg = COUNTRY_CONFIGS[cc]
            assert "base_url" in cfg
            assert "currency" in cfg
            assert cfg["base_url"].startswith("https://")

    def test_ae_config(self):
        cfg = COUNTRY_CONFIGS["AE"]
        assert cfg["currency"] == "AED"

    def test_kw_config(self):
        cfg = COUNTRY_CONFIGS["KW"]
        assert cfg["currency"] == "KWD"

    def test_config_auto_fills_urls(self):
        c = OpenSooqConfig(country="SA")
        assert "sa.opensooq.com" in c.base_url
        assert c.currency == "SAR"

    def test_config_checkpoint_path(self):
        c = OpenSooqConfig(country="KW")
        assert "KW" in c.checkpoint_path


class TestDiscovery:
    def test_search_url(self):
        d = OpenSooqDiscovery(OpenSooqConfig(country="AE"))
        url = d.search_url()
        assert "opensooq.com" in url

    def test_country_specific_url(self):
        d = OpenSooqDiscovery(OpenSooqConfig(country="SA"))
        url = d.search_url(make="toyota")
        assert "sa.opensooq.com" in url
        assert "toyota" in url


class TestMapper:
    def test_ae_mapping(self):
        m = OpenSooqMapper(OpenSooqConfig(country="AE"))
        listing = m.map_to_canonical({"make": "Toyota", "model": "Camry", "year": 2020, "price": 75000},
                                     url="https://ae.opensooq.com/vehicles/12345")
        assert listing.marketplace == "opensooq_ae"
        assert listing.pricing.currency == "AED"
        assert listing.location.country == "AE"

    def test_kw_mapping(self):
        m = OpenSooqMapper(OpenSooqConfig(country="KW"))
        listing = m.map_to_canonical({"make": "Toyota", "model": "Camry", "year": 2020, "price": 5000},
                                     url="https://kw.opensooq.com/vehicles/67890")
        assert listing.marketplace == "opensooq_kw"
        assert listing.pricing.currency == "KWD"
        assert listing.location.country == "KW"


class TestCapabilities:
    def test_multi_country_support(self):
        caps = OpenSooqCapabilities()
        assert caps.supports_multi_country
        assert len(caps.supported_countries) == 6
        assert caps.supports_rtl
