"""Extraction validation — required fields, empty nodes, missing attributes."""

from browser.dom.node import DOMNode
from browser.dom.errors import ValidationError


class ExtractionValidator:
    """Validate extraction results and DOM nodes.

    Usage:
        validator = ExtractionValidator()
        validator.require_node(node, "price")
        validator.require_text(node, "title")
    """

    @staticmethod
    def require_node(node: DOMNode | None, field_name: str) -> None:
        """Raise if the node is None (selector matched nothing)."""
        if node is None:
            raise ValidationError(f"Required field '{field_name}' not found")

    @staticmethod
    def require_text(node: DOMNode | None, field_name: str) -> str:
        """Return non-empty text or raise."""
        ExtractionValidator.require_node(node, field_name)
        text = node.text_stripped
        if not text:
            raise ValidationError(f"Required field '{field_name}' is empty")
        return text

    @staticmethod
    def require_attr(node: DOMNode | None, attr_name: str,
                     field_name: str | None = None) -> str:
        """Return non-empty attribute or raise."""
        name = field_name or attr_name
        ExtractionValidator.require_node(node, name)
        val = node.attr(attr_name)
        if not val:
            raise ValidationError(f"Required attribute '{attr_name}' missing on '{name}'")
        return val

    @staticmethod
    def validate_selectors(doc, selectors: dict[str, str]) -> list[str]:
        """Check that all required CSS selectors exist in the document.
        Returns list of missing field names."""
        missing = []
        for field_name, css in selectors.items():
            if not doc.exists(css):
                missing.append(field_name)
        return missing
