"""Dubizzle UAE listing parser."""
from bs4 import BeautifulSoup
import re


def parse_listing(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {"url": url, "status": "active"}

    title_elem = soup.select_one("h1, [data-testid='listing-title'], .listing-title")
    title = title_elem.get_text(strip=True) if title_elem else ""

    result["make"], result["model"] = _extract_make_model(title)
    result["year"] = _extract_year(title)
    result["spec"] = _extract_spec(title)
    result["mileage_km"] = _extract_mileage(title)

    price_elem = soup.select_one("[data-testid='listing-price'], .price, [class*='price']")
    if price_elem:
        result["asking_price"] = _extract_price(price_elem.get_text(strip=True))
    else:
        result["asking_price"] = 0
    result["original_currency"] = "AED"

    match = re.search(r'/cars/(\d+)|id[-_](\d+)', url)
    result["external_id"] = match.group(1) or match.group(2) if match else ""

    details = {}
    for row in soup.select("tr, .detail-item, [class*='spec']"):
        cells = row.find_all(["td", "th", "span"])
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True).lower().rstrip(":")
            value = cells[1].get_text(strip=True)
            details[key] = value

    result["body_type"] = details.get("body type") or details.get("body")
    result["transmission"] = details.get("transmission")
    result["fuel_type"] = details.get("fuel type") or details.get("fuel")
    result["engine_size"] = _extract_engine_size(details.get("engine size", ""))
    result["color"] = details.get("color")
    result["trim"] = details.get("trim")
    result["seller_type"] = _extract_seller_type(details)

    loc_elem = soup.select_one("[data-testid='location'], .location, [class*='location']")
    loc_text = loc_elem.get_text(strip=True) if loc_elem else ""
    result["city"] = loc_text.strip() or "Dubai"
    result["country"] = "AE"

    return result


def _extract_make_model(title: str) -> tuple[str, str]:
    tokens = title.split()
    if len(tokens) >= 2:
        return tokens[0], " ".join(tokens[1:3])
    return "", ""


def _extract_year(title: str) -> int | None:
    match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', title)
    return int(match.group(1)) if match else None


def _extract_mileage(title: str) -> int | None:
    match = re.search(r'(\d[\d,]*)\s*km', title, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def _extract_spec(title: str) -> str | None:
    t = title.lower()
    if "gcc" in t:
        return "GCC"
    if "american" in t or "us spec" in t or "usa" in t:
        return "US"
    if "japan" in t or "japanese" in t:
        return "Japan"
    if "european" in t or "euro" in t:
        return "European"
    return None


def _extract_price(text: str) -> float:
    text = re.sub(r'[^\d.]', '', text.replace(",", ""))
    try:
        return float(text)
    except ValueError:
        return 0.0


def _extract_engine_size(text: str) -> float | None:
    match = re.search(r'(\d+\.?\d*)\s*L', text, re.IGNORECASE)
    return float(match.group(1)) if match else None


def _extract_seller_type(details: dict) -> str | None:
    seller = details.get("seller type", details.get("seller", "")).lower()
    if "dealer" in seller or "showroom" in seller:
        return "dealer"
    if "private" in seller or "owner" in seller:
        return "private"
    return None


def extract_html_structure_hash(html: str) -> str:
    import hashlib
    soup = BeautifulSoup(html, "lxml")
    selectors = [el.name for el in soup.select("h1, [class*='price'], [class*='title']")]
    return hashlib.sha256("|".join(selectors).encode()).hexdigest()[:12]
