"""URL-based valuation — paste a listing URL, we fetch it, parse it, and value it."""
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from bs4 import BeautifulSoup
import httpx
from src.api.dependencies import get_db
from src.engine.statistical import valuate
from src.pipeline.normalizer import normalize_listing
import structlog

router = APIRouter()
logger = structlog.get_logger()


class URLValuationRequest(BaseModel):
    url: str
    asking_price: float | None = None  # optional — if user knows the price


async def fetch_url(url: str) -> str:
    """Fetch a URL with a browser-like user agent."""
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        r = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        })
        r.raise_for_status()
        return r.text


def parse_listing_from_html(html: str, url: str) -> dict | None:
    """Try to extract car listing details from any car marketplace page."""
    soup = BeautifulSoup(html, "lxml")
    result = {"url": url, "source": "url_paste", "status": "active",
              "original_currency": "AED", "country": "AE"}

    # Try to find title
    title = (soup.select_one("h1") or soup.select_one("title") or
             soup.select_one("[class*='title']") or soup.select_one("[class*='heading']"))
    title_text = title.get_text(strip=True) if title else ""

    # Extract make/model from title
    tokens = title_text.split()
    result["make"] = tokens[0] if tokens else ""
    result["model"] = tokens[1] if len(tokens) > 1 else ""

    # Year
    year_match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', title_text + " " + html)
    result["year"] = int(year_match.group(1)) if year_match else None

    # Mileage
    mileage_match = re.search(r'(\d[\d,]*)\s*km', title_text + " " + html, re.IGNORECASE)
    result["mileage_km"] = int(mileage_match.group(1).replace(",", "")) if mileage_match else None

    # Price
    price_selectors = [
        "[class*='price']", "[data-testid*='price']", ".price-value",
        "meta[property='product:price']", "[itemprop='price']",
        "span:contains('AED')", "div:contains('AED')",
    ]
    for sel in price_selectors:
        try:
            price_el = soup.select_one(sel)
            if price_el:
                price_text = price_el.get("content") or price_el.get_text(strip=True)
                price_text = re.sub(r'[^\d.]', '', price_text.replace(",", ""))
                if price_text and float(price_text) > 100:
                    result["asking_price"] = float(price_text)
                    break
        except Exception:
            continue

    if "asking_price" not in result:
        result["asking_price"] = 0

    # Spec
    text_lower = (title_text + " " + html).lower()
    if "gcc" in text_lower or "خليجي" in text_lower: result["spec"] = "GCC"
    elif "american spec" in text_lower or "us spec" in text_lower: result["spec"] = "US"
    elif "japan" in text_lower or "ياباني" in text_lower: result["spec"] = "Japan"

    # City
    cities = ["Dubai", "Abu Dhabi", "Sharjah", "Riyadh", "Jeddah", "Dammam",
              "Kuwait City", "Doha", "Muscat", "Manama"]
    for city in cities:
        if city.lower() in text_lower:
            result["city"] = city
            break

    if "city" not in result:
        result["city"] = "Dubai"

    # Country
    if "haraj" in url: result["country"] = "SA"
    elif "ksa" in url or "saudi" in url: result["country"] = "SA"
    elif "dubizzle" in url: result["country"] = "AE"
    elif "yallamotor" in url:
        if "ksa" in url: result["country"] = "SA"
        else: result["country"] = "AE"
    elif "qatar" in url: result["country"] = "QA"
    elif "kuwait" in url or "q8car" in url: result["country"] = "KW"
    elif "bahrain" in url: result["country"] = "BH"
    elif "oman" in url: result["country"] = "OM"

    # Body type
    if "suv" in text_lower or "4x4" in text_lower: result["body_type"] = "SUV"
    elif "sedan" in text_lower: result["body_type"] = "sedan"

    # Transmission
    if "automatic" in text_lower or "auto" in text_lower: result["transmission"] = "automatic"

    # Source detection
    if "dubizzle" in url: result["source"] = "dubizzle"
    elif "yallamotor" in url: result["source"] = "yallamotor"
    elif "haraj" in url: result["source"] = "haraj"
    elif "carswitch" in url: result["source"] = "carswitch"
    elif "opensooq" in url: result["source"] = "opensooq"

    # External ID from URL
    id_match = re.search(r'/(\d{5,})[/$]', url)
    result["external_id"] = id_match.group(1) if id_match else url[-20:]

    if not result.get("make") or not result.get("year"):
        return None

    return result


@router.post("/valuate-url")
async def valuate_from_url(
    request: URLValuationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Paste a car listing URL, we fetch it, parse the details, and return a valuation."""
    try:
        html = await fetch_url(request.url)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=422, detail=f"Could not fetch URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error fetching URL: {e}")

    parsed = parse_listing_from_html(html, request.url)
    if not parsed:
        raise HTTPException(
            status_code=422,
            detail="Could not extract car details from this URL. Try entering the details manually."
        )

    logger.info("url_parsed", url=request.url, make=parsed.get("make"),
                model=parsed.get("model"), year=parsed.get("year"))

    # Normalize and valuate
    parsed = normalize_listing(parsed)
    if request.asking_price:
        parsed["asking_price"] = request.asking_price

    valuation = await valuate(
        db, parsed["make"], parsed["model"], parsed.get("year", 2020),
        parsed.get("mileage_km"), parsed.get("spec"),
        parsed.get("country"), parsed.get("city"),
    )

    if valuation.confidence == "insufficient":
        raise HTTPException(
            status_code=422,
            detail="Not enough comparable listings for this vehicle. Try a more common make/model."
        )

    return {
        "parsed_from_url": {
            "make": parsed.get("make"),
            "model": parsed.get("model"),
            "year": parsed.get("year"),
            "mileage_km": parsed.get("mileage_km"),
            "spec": parsed.get("spec"),
            "city": parsed.get("city"),
            "country": parsed.get("country"),
            "price_found": parsed.get("asking_price", 0),
        },
        "estimate": valuation.estimate,
        "price_low": valuation.price_low,
        "price_high": valuation.price_high,
        "confidence": valuation.confidence,
        "comp_count": valuation.comp_count,
        "segment_median": valuation.segment_median,
        "adjustments": [{"reason": a.reason, "amount": a.amount, "detail": a.detail}
                        for a in valuation.adjustments],
        "comps": valuation.comps,
        "confidence_interval_80": valuation.confidence_interval_80,
    }
