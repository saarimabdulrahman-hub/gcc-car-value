"""Seller sub-model."""

from dataclasses import dataclass


@dataclass
class Seller:
    """Seller/dealer information."""
    seller_type: str = "private"    # private, dealer, auction, certified
    seller_name: str = ""
    dealer_name: str = ""
    dealer_id: str = ""
    verified: bool = False
    rating: float = 0.0             # 0.0–5.0
    phone_available: bool = False
    chat_available: bool = False
