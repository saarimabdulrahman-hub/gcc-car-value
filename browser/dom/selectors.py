"""Common CSS selector patterns for GCC car marketplaces.

Centralized here so scrapers don't hardcode selectors.
"""

# --- Common listing page selectors ---
LISTING_SELECTORS = {
    "title": "h1, [class*='title'], [class*='heading'], title",
    "price": "[class*='price'], .price-value, [data-testid*='price']",
    "year": "[class*='year'], [data-year]",
    "mileage": "[class*='mileage'], [class*='km'], [class*='odo']",
    "location": "[class*='location'], [class*='city'], [class*='area']",
    "description": "[class*='description'], [class*='details'], [class*='desc']",
    "specs": "[class*='spec'], [class*='feature'], .specs-list li",
    "seller": "[class*='seller'], [class*='dealer'], [class*='owner']",
}

# --- Common listing card selectors (index/search pages) ---
CARD_SELECTORS = {
    "card": "[class*='listing'], [class*='card'], [class*='item'], article, li",
    "card_title": "[class*='title'], h2, h3",
    "card_price": "[class*='price']",
    "card_link": "a[href]",
    "card_image": "img",
    "card_year": "[class*='year']",
    "card_mileage": "[class*='mileage'], [class*='km']",
}
