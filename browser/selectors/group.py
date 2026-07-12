"""Selector groups — pre-defined categories for GCC car marketplace extraction."""

from browser.selectors.models import Selector

# Standard groups that every marketplace scraper can use
GROUPS = {
    "listing": "Listing-level fields (title, url, id)",
    "price": "Price-related fields (asking price, currency)",
    "title": "Title and heading fields",
    "mileage": "Odometer/mileage fields",
    "year": "Model year fields",
    "fuel": "Fuel type fields",
    "transmission": "Transmission type fields",
    "seller": "Seller/dealer information",
    "images": "Image URLs",
    "location": "City, country, region",
    "spec": "Specification (GCC, US, Japan)",
    "body_type": "Body type (SUV, sedan, pickup)",
    "description": "Full text description",
    "contact": "Phone, email, WhatsApp",
}


class SelectorGroup:
    """A named group of selectors for a marketplace."""

    def __init__(self, marketplace: str, group_name: str,
                 selectors: list[Selector]):
        self.marketplace = marketplace
        self.group_name = group_name
        self.selectors = selectors

    @classmethod
    def create(cls, marketplace: str, group_name: str,
               selectors: list[Selector]) -> "SelectorGroup":
        """Create a selector group — ensures all selectors share marketplace+group."""
        for s in selectors:
            s.marketplace = marketplace
            s.group = group_name
        return cls(marketplace, group_name, selectors)


def create_selector(name: str, css: str, fallbacks: list[str] | None = None,
                    required: bool = True, selector_type: str = "text",
                    marketplace: str = "", group: str = "",
                    description: str = "", attribute_name: str = "",
                    ) -> Selector:
    """Factory helper for creating selectors."""
    return Selector(
        name=name, css=css, fallbacks=fallbacks or [],
        required=required, selector_type=selector_type,
        marketplace=marketplace, group=group,
        description=description, attribute_name=attribute_name,
    )
