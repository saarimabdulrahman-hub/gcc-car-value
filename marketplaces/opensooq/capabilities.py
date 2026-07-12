"""OpenSooq capability manifest — multi-country aware."""

from dataclasses import dataclass


@dataclass
class OpenSooqCapabilities:
    supports_search: bool = True
    supports_pagination: bool = True
    supports_images: bool = True
    supports_video: bool = False
    supports_chat: bool = True
    supports_phone: bool = True
    supports_dealer_pages: bool = True
    supports_vehicle_history: bool = False
    supports_multi_country: bool = True   # Key differentiator
    supports_rtl: bool = True             # Arabic interface
    requires_login: bool = False
    max_images_per_listing: int = 15
    max_listings_per_page: int = 24
    default_locale: str = "ar"
    supported_countries: list = None

    def __post_init__(self):
        from marketplaces.opensooq.constants import SUPPORTED_COUNTRIES
        if self.supported_countries is None:
            self.supported_countries = SUPPORTED_COUNTRIES
