"""Dubizzle UAE CSS selectors — registered with the Selector Framework.

These are the ONLY place where Dubizzle-specific DOM knowledge exists.
The rest of the connector references selectors by name, never raw CSS.
"""

from browser.selectors.group import create_selector
from browser.selectors.registry import scraper_registry as reg_factory

# Dubizzle selectors are registered at import time into the global registry.
# All selectors have fallback chains for resilience against site changes.

DUBIZZLE_SELECTORS: list = []


def _register():
    """Register all Dubizzle selectors. Call once at startup."""
    import asyncio
    from browser.selectors.registry import SelectorRegistry

    registry = SelectorRegistry()

    async def _reg():
        for s in _SELECTORS:
            await registry.register(s)

    try:
        asyncio.get_event_loop()
        asyncio.create_task(_reg())
    except RuntimeError:
        pass  # Will be registered when first used

    return registry


_SELECTORS = [
    # --- Search/Index page ---
    create_selector("dubizzle.card", "[class*='listing-card'], [data-testid='listing-card'], article.listing",
                    fallbacks=["[class*='card']", "li[class*='listing']"],
                    marketplace="dubizzle_uae", group="listing", description="Listing card on search results"),
    create_selector("dubizzle.card.link", "a[href*='/motors/used-cars/']",
                    fallbacks=["[class*='card'] a", "article a"],
                    marketplace="dubizzle_uae", group="listing", selector_type="url"),
    create_selector("dubizzle.card.title", "h2, [class*='title']",
                    fallbacks=["h3", "[class*='heading']"],
                    marketplace="dubizzle_uae", group="title"),
    create_selector("dubizzle.card.price", "[class*='price']",
                    fallbacks=["[data-testid='price']", "[class*='amount']"],
                    marketplace="dubizzle_uae", group="price", selector_type="currency"),
    create_selector("dubizzle.card.year", "[class*='year']",
                    fallbacks=["[data-year]", "[class*='model-year']"],
                    marketplace="dubizzle_uae", group="year", selector_type="year"),
    create_selector("dubizzle.card.mileage", "[class*='mileage'], [class*='km']",
                    fallbacks=["[class*='odo']", "[class*='distance']"],
                    marketplace="dubizzle_uae", group="mileage", selector_type="integer"),
    create_selector("dubizzle.card.location", "[class*='location']",
                    fallbacks=["[class*='city'], [class*='area']"],
                    marketplace="dubizzle_uae", group="location"),
    create_selector("dubizzle.card.image", "img",
                    fallbacks=["[class*='image'] img"],
                    marketplace="dubizzle_uae", group="images", selector_type="url"),
    create_selector("dubizzle.pagination.next", "a[class*='next'], [class*='pagination'] a:last-child",
                    fallbacks=["a[rel='next']", "a:contains('Next')"],
                    marketplace="dubizzle_uae", group="listing"),

    # --- Detail page ---
    create_selector("dubizzle.detail.title", "h1",
                    fallbacks=["[class*='title']", "[class*='heading']"],
                    marketplace="dubizzle_uae", group="title"),
    create_selector("dubizzle.detail.price", "[class*='price-value'], [class*='amount']",
                    fallbacks=["[class*='price']", "[data-testid='price']"],
                    marketplace="dubizzle_uae", group="price", selector_type="currency"),
    create_selector("dubizzle.detail.mileage", "[class*='mileage'], [class*='kilometers']",
                    fallbacks=["[class*='km']", "[class*='odometer']"],
                    marketplace="dubizzle_uae", group="mileage", selector_type="integer"),
    create_selector("dubizzle.detail.year", "[class*='year']",
                    fallbacks=["[data-year]"],
                    marketplace="dubizzle_uae", group="year", selector_type="year"),
    create_selector("dubizzle.detail.spec", "[class*='spec'], [class*='regional-spec']",
                    fallbacks=["[class*='import']"],
                    marketplace="dubizzle_uae", group="spec"),
    create_selector("dubizzle.detail.transmission", "[class*='transmission']",
                    fallbacks=["[class*='gear']", "[class*='trans']"],
                    marketplace="dubizzle_uae", group="transmission"),
    create_selector("dubizzle.detail.fuel", "[class*='fuel']",
                    fallbacks=["[class*='engine-type']"],
                    marketplace="dubizzle_uae", group="fuel"),
    create_selector("dubizzle.detail.body", "[class*='body-type'], [class*='body']",
                    fallbacks=["[class*='category']"],
                    marketplace="dubizzle_uae", group="body_type"),
    create_selector("dubizzle.detail.color", "[class*='color']",
                    fallbacks=["[class*='exterior']"],
                    marketplace="dubizzle_uae", group="color"),
    create_selector("dubizzle.detail.description", "[class*='description'], [class*='details']",
                    fallbacks=["[class*='body-text'], [class*='content']"],
                    marketplace="dubizzle_uae", group="description"),
    create_selector("dubizzle.detail.seller", "[class*='seller'], [class*='dealer']",
                    fallbacks=["[class*='poster'], [class*='owner']"],
                    marketplace="dubizzle_uae", group="seller"),
    create_selector("dubizzle.detail.images", "[class*='gallery'] img, [class*='carousel'] img",
                    fallbacks=["[class*='image-container'] img", "img[src*='dubizzle']"],
                    marketplace="dubizzle_uae", group="images"),
]
