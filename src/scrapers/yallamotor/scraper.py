"""YallaMotor scraper — one scraper covers UAE, KSA, QA, KW, BH, OM."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper

# Country config: base URL suffix → country code + default city
COUNTRIES = {
    "uae": ("AE", "Dubai"),
    "ksa": ("SA", "Riyadh"),
    "qatar": ("QA", "Doha"),
    "kuwait": ("KW", "Kuwait City"),
    "bahrain": ("BH", "Manama"),
    "oman": ("OM", "Muscat"),
}

class YallaMotorScraper(BaseScraper):
    source = "yallamotor"

    def __init__(self, country_key: str = "uae"):
        self.country_key = country_key
        self.country_code, self.default_city = COUNTRIES[country_key]
        self.base_url = f"https://{country_key}.yallamotor.com"
        super().__init__()

    async def fetch_index(self, page: int) -> list[str]:
        session = await self.get_session()
        url = f"{self.base_url}/used-cars?page={page}"
        response = await session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        links = []
        for link in soup.select("a[href*='/used-cars/']"):
            href = link.get("href", "")
            if "/used-cars/" in href and href.count("/") > 3:
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                links.append(full_url)
        return list(set(links))

    async def fetch_listing(self, url: str) -> str:
        session = await self.get_session()
        response = await session.get(url)
        response.raise_for_status()
        return response.text

    def parse(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        result = {"url": url, "source": self.source, "status": "active",
                  "country": self.country_code, "city": self.default_city,
                  "original_currency": "AED"}

        # Title
        title = soup.select_one("h1, .car-title, [class*='title']")
        title_text = title.get_text(strip=True) if title else ""

        result["make"], result["model"] = self._extract_make_model(title_text)
        result["year"] = self._extract_number(title_text)
        result["spec"] = self._extract_spec(title_text)
        result["mileage_km"] = self._extract_mileage(title_text)

        # Price
        price_elem = soup.select_one("[class*='price'], .price-value, .car-price")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            result["asking_price"] = self._extract_number(price_text)
        else:
            result["asking_price"] = 0

        # External ID from URL
        match = re.search(r'/(\d+)[/$]', url)
        result["external_id"] = match.group(1) if match else ""

        # Details list
        for item in soup.select("li, .spec-item, .feature-item"):
            text = item.get_text(strip=True).lower()
            if "body" in text:
                result["body_type"] = text.replace("body type", "").strip().strip(":")
            elif "transmission" in text:
                result["transmission"] = text.replace("transmission", "").strip().strip(":")
            elif "fuel" in text:
                result["fuel_type"] = text.replace("fuel type", "").strip().strip(":")

        # Location
        loc = soup.select_one("[class*='location'], .city, [class*='city']")
        if loc:
            result["city"] = loc.get_text(strip=True) or self.default_city

        result["parser_version"] = "yallamotor_v1.0.0"
        result["schema_version"] = 1
        result["normalizer_version"] = "normalizer_v1.0.0"
        return result

    def _extract_make_model(self, title: str) -> tuple[str, str]:
        tokens = title.split()
        return (tokens[0], tokens[1]) if len(tokens) >= 2 else ("", "")

    def _extract_number(self, text: str) -> int | float | None:
        text = re.sub(r'[^\d.]', '', text.replace(",", ""))
        try:
            return float(text) if "." in text else int(float(text))
        except ValueError:
            return None

    def _extract_mileage(self, text: str) -> int | None:
        match = re.search(r'(\d[\d,]*)\s*km', text, re.IGNORECASE)
        return int(match.group(1).replace(",", "")) if match else None

    def _extract_spec(self, text: str) -> str | None:
        t = text.lower()
        if "gcc" in t: return "GCC"
        if "american" in t or "us spec" in t: return "US"
        if "japan" in t: return "Japan"
        return None
