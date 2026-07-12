"""Selector data models."""

from dataclasses import dataclass, field
import uuid


@dataclass
class Selector:
    """A reusable CSS selector with fallback chain and versioning."""
    selector_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""                         # e.g., "listing.price"
    css: str = ""                          # Primary CSS selector
    fallbacks: list[str] = field(default_factory=list)  # Fallback CSS selectors
    required: bool = True                  # Is this field required?
    selector_type: str = "text"            # text, integer, currency, year, url, attribute
    marketplace: str = ""                  # e.g., "dubizzle_uae"
    version: int = 1
    description: str = ""
    group: str = ""                        # e.g., "listing", "price"
    attribute_name: str = ""               # For attribute-type selectors
    deprecated: bool = False

    @property
    def all_selectors(self) -> list[str]:
        """Return the full selector chain: [primary] + fallbacks."""
        return [self.css] + self.fallbacks


@dataclass
class SelectorExecutionResult:
    """Result of executing a selector against a DOM document."""
    selector_id: str = ""
    selector_name: str = ""
    matched: bool = False
    matched_selector: str = ""            # Which selector in the chain matched
    fallback_used: bool = False
    fallback_index: int = -1              # Which fallback (0=primary, 1=first fallback)
    nodes_found: int = 0
    value: str = ""                       # Extracted text value
    execution_time_ms: float = 0.0
    error: str | None = None


@dataclass
class SelectorDiagnostics:
    """Diagnostic information for a selector execution."""
    selector: Selector | None = None
    result: SelectorExecutionResult | None = None
    all_tried: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
