"""Typed extraction helpers — text, int, float, currency, URL, date."""

import re
from datetime import datetime
from browser.dom.node import DOMNode
from browser.dom.models import ExtractionResult


class Extractor:
    """Collection of typed extraction methods from DOMNodes.

    Each method returns an ExtractionResult with .value, .success, .error.
    All methods handle None nodes gracefully (returns failed result).

    Usage:
        ext = Extractor()
        price = ext.currency(doc.select_one(".price"))
        if price.success:
            print(price.value)  # 75000.0
    """

    def text(self, node: DOMNode | None, default: str = "",
             field: str = "") -> ExtractionResult:
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        return ExtractionResult(success=True, value=node.text_stripped,
                                raw=node.text, field_name=field)

    def integer(self, node: DOMNode | None, default: int = 0,
                field: str = "") -> ExtractionResult:
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        text = node.text_stripped
        nums = re.findall(r'-?\d+', text.replace(',', ''))
        if nums:
            return ExtractionResult(success=True, value=int(nums[0]),
                                    raw=text, field_name=field)
        return ExtractionResult(success=False, value=default,
                                raw=text, error="No integer found",
                                field_name=field)

    def float_val(self, node: DOMNode | None, default: float = 0.0,
                  field: str = "") -> ExtractionResult:
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        text = node.text_stripped
        nums = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
        if nums:
            try:
                return ExtractionResult(success=True, value=float(nums[0]),
                                        raw=text, field_name=field)
            except ValueError:
                pass
        return ExtractionResult(success=False, value=default,
                                raw=text, error="No float found",
                                field_name=field)

    def currency(self, node: DOMNode | None,
                 default: float = 0.0,
                 field: str = "") -> ExtractionResult:
        """Extract a currency value, handling AED/SAR prefixes and commas."""
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        text = node.text_stripped
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
        if cleaned:
            try:
                return ExtractionResult(success=True, value=float(cleaned),
                                        raw=text, field_name=field)
            except ValueError:
                pass
        return ExtractionResult(success=False, value=default,
                                raw=text, error="No currency value found",
                                field_name=field)

    def year(self, node: DOMNode | None,
             default: int = 0,
             field: str = "") -> ExtractionResult:
        """Extract a model year (1990–current+1)."""
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        text = node.text_stripped
        current = datetime.utcnow().year
        years = re.findall(r'\b(19\d{2}|20[0-2]\d)\b', text)
        valid = [int(y) for y in years if 1990 <= int(y) <= current + 1]
        if valid:
            return ExtractionResult(success=True, value=valid[0],
                                    raw=text, field_name=field)
        return ExtractionResult(success=False, value=default,
                                raw=text, error="No valid year found",
                                field_name=field)

    def url(self, node: DOMNode | None,
            default: str = "",
            field: str = "") -> ExtractionResult:
        """Extract a URL from a node's href or src attribute."""
        if node is None:
            return ExtractionResult(success=False, value=default,
                                    error="Node not found", field_name=field)
        for attr in ("href", "src"):
            val = node.attr(attr)
            if val and val.strip():
                return ExtractionResult(success=True, value=val.strip(),
                                        raw=val, field_name=field)
        return ExtractionResult(success=False, value=default,
                                error="No URL attribute found",
                                field_name=field)
