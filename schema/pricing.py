"""Pricing sub-model."""

from dataclasses import dataclass, field


@dataclass
class Pricing:
    """Listing price with currency and negotiability."""
    amount: float = 0.0
    currency: str = "AED"
    negotiable: bool = False
    tax_included: bool = True
    finance_available: bool = False
    price_history: list[dict] = field(default_factory=list)  # [{date, amount, currency}]
