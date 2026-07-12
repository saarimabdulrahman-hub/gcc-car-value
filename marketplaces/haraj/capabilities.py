"""Haraj marketplace capability manifest — discoverable by the shared framework."""

from dataclasses import dataclass


@dataclass
class HarajCapabilities:
    """Describes what Haraj supports for the marketplace framework."""
    supports_search: bool = True
    supports_pagination: bool = True
    supports_images: bool = True
    supports_video: bool = False
    supports_chat: bool = True       # Haraj has built-in chat
    supports_phone: bool = True      # Phone numbers common in listings
    supports_dealer_pages: bool = True
    supports_vehicle_history: bool = False
    supports_favorites: bool = True
    supports_price_history: bool = False
    requires_login: bool = False
    is_arabic_first: bool = True     # RTL, Arabic interface
    supports_english: bool = False
    max_images_per_listing: int = 20
    max_listings_per_page: int = 25
    default_locale: str = "ar-SA"
    default_timezone: str = "Asia/Riyadh"
    default_currency: str = "SAR"
    default_country: str = "SA"
