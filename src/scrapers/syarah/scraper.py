"""Syarah KSA scraper — modern Saudi used car platform with financing data."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper

class SyarahScraper(BaseScraper):
    source = "syarah"
    base_url = "https://syarah.com"

    async def fetch_index(self, page: int) -> list[str]:
        session = await self.get_session()
        url = f"{self.base_url}/cars?page={page}"
        response = await session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        links = []
        for link in soup.select("a[href*='/car/'], a[href*='/cars/']"):
            href = link.get("href", "")
            if "/car/" in href or "/cars/" in href:
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
        result = {"url": url, "source": self.source, "country": "SA",
                  "original_currency": "SAR", "city": "Riyadh", "status": "active"}

        title = soup.select_one("h1, .car-title, [class*='title']")
        title_text = title.get_text(strip=True) if title else ""
        result["make"], result["model"] = self._extract_make_model(title_text)
        result["year"] = self._extract_year(title_text)
        result["mileage_km"] = self._extract_mileage(title_text + " " + html)
        result["spec"] = self._extract_spec(html)

        price_elem = soup.select_one("[class*='price'], .price-value")
        result["asking_price"] = self._extract_number(price_elem.get_text(strip=True)) if price_elem else 0

        match = re.search(r'/(\d+)[/$]', url)
        result["external_id"] = match.group(1) if match else ""

        if "suv" in html.lower() or "4x4" in html.lower(): result["body_type"] = "SUV"
        elif "sedan" in html.lower(): result["body_type"] = "sedan"
        if "automatic" in html.lower(): result["transmission"] = "automatic"

        result["parser_version"] = "syarah_v1.0.0"
        result["schema_version"] = 1
        result["normalizer_version"] = "normalizer_v1.0.0"
        return result

    def _extract_make_model(self, title: str) -> tuple[str, str]:
        tokens = title.split()
        return (tokens[0], tokens[1]) if len(tokens) >= 2 else ("", "")
    def _extract_year(self, text: str) -> int | None:
        m = re.search(r'\b(20[0-2]\d)\b', text); return int(m.group(1)) if m else None
    def _extract_number(self, text: str) -> float:
        text = re.sub(r'[^\d.]', '', text.replace(",", ""))
        try: return float(text)
        except ValueError: return 0.0
    def _extract_mileage(self, text: str) -> int | None:
        m = re.search(r'(\d[\d,]*)\s*km', text, re.IGNORECASE)
        return int(m.group(1).replace(",", "")) if m else None
    def _extract_spec(self, text: str) -> str | None:
        t = text.lower()
        if "gcc" in t or "خليجي" in t: return "GCC"
        if "american" in t or "us spec" in t: return "US"
        return None
