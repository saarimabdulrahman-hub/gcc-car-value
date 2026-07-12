"""Base parser with common extraction helpers for GCC car marketplaces."""

import re
from typing import Any
from scrapers.base.interfaces import BaseParser


class BaseListingParser(BaseParser):
    """Base parser with GCC-marketplace-common extraction helpers.

    Marketplace parsers inherit from this and override parse().
    Helper methods handle common extraction patterns found across
    Dubizzle, YallaMotor, Haraj, OpenSooq, etc.
    """

    async def parse(self, html: str, url: str) -> dict[str, Any]:
        raise NotImplementedError

    # --- Shared extraction helpers ---

    @staticmethod
    def extract_year(text: str) -> int | None:
        """Extract model year (1990–current+1) from text."""
        years = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', text)
        if not years:
            return None
        from datetime import datetime
        current = datetime.utcnow().year
        valid = [int(y) for y in years if 1990 <= int(y) <= current + 1]
        return valid[0] if valid else None

    @staticmethod
    def extract_mileage(text: str) -> int | None:
        """Extract mileage in km from text. Handles '120,000 km' and '120000 km'."""
        match = re.search(r'(\d[\d,]*)\s*km', text, re.IGNORECASE)
        if not match:
            return None
        return int(match.group(1).replace(",", ""))

    @staticmethod
    def extract_price(text: str) -> float | None:
        """Extract price in AED/SAR from text."""
        match = re.search(r'(?:AED|SAR|د\.إ|ر\.س)\s*(\d[\d,]*)', text, re.IGNORECASE)
        if not match:
            # Try plain number near currency words
            match = re.search(r'(\d{2,3}(?:,\d{3})*(?:\s*(?:AED|SAR)))', text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))
        return None

    @staticmethod
    def extract_make_model(title: str) -> tuple[str, str]:
        """Extract make and model from a title. Assumes first 2 tokens."""
        tokens = title.strip().split()
        if len(tokens) >= 2:
            return tokens[0].title(), tokens[1].title()
        if len(tokens) == 1:
            return tokens[0].title(), ""
        return "", ""

    @staticmethod
    def detect_spec(text: str) -> str | None:
        """Detect vehicle specification (GCC, US, Japan, European) from text."""
        text_lower = text.lower()
        if any(t in text_lower for t in ["gcc", "خليجي", "gulf spec"]):
            return "GCC"
        if any(t in text_lower for t in ["american spec", "us spec", "usa spec"]):
            return "US"
        if any(t in text_lower for t in ["japan", "japanese", "ياباني"]):
            return "Japan"
        if any(t in text_lower for t in ["european", "euro spec"]):
            return "European"
        return None
