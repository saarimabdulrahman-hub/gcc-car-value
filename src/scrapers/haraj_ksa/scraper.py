"""Haraj KSA scraper — Saudi Arabia's largest car marketplace."""
import re

from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper
from src.scrapers.title_parser import extract_make_model


class HarajKSAScraper(BaseScraper):
    source = "haraj_ksa"
    base_url = "https://haraj.com.sa"

    async def fetch_index(self, page: int) -> list[str]:
        session = await self.get_session()
        url = f"{self.base_url}/haraj-cars/?page={page}"
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
        result = {
            "url": url, "source": self.source, "status": "active",
            "country": "SA", "city": "Riyadh",
            "original_currency": "SAR",
        }

        # Title: "تويوتا لاند كروزر 2018" or "Toyota Land Cruiser 2018"
        title = soup.select_one("h1, .title, [class*='title']")
        title_text = title.get_text(strip=True) if title else ""

        result["make"], result["model"] = extract_make_model(title_text)
        result["year"] = self._extract_year(title_text)

        # Scope to the listing body; fall back to the title only, never whole HTML.
        body = soup.select_one("[class*='postBody'], [class*='post-body'], article, main")
        scope_text = body.get_text(" ", strip=True) if body else title_text

        result["spec"] = self._extract_spec(scope_text)
        result["mileage_km"] = self._extract_mileage(scope_text)

        # Price — Haraj prices are in SAR
        price_elem = soup.select_one("[class*='price'], .price-value")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            result["asking_price"] = self._extract_number(price_text)
        else:
            result["asking_price"] = 0

        # External ID
        match = re.search(r'/(\d+)[/$]', url)
        result["external_id"] = match.group(1) if match else ""

        # Body type
        scope_lower = scope_text.lower()
        if "suv" in scope_lower or "دفع رباعي" in scope_text:
            result["body_type"] = "SUV"
        elif "sedan" in scope_lower or "سيدان" in scope_text:
            result["body_type"] = "sedan"

        # Transmission
        if "automatic" in scope_lower or "اوتوماتيك" in scope_text or "أوتوماتيك" in scope_text:
            result["transmission"] = "automatic"
        elif "manual" in scope_lower or "عادي" in scope_text:
            result["transmission"] = "manual"

        # City
        city_match = re.search(r'(الرياض|جدة|الدمام|مكة|المدينة|القصيم|تبوك|الخبر)', scope_text)
        if city_match:
            city_map = {
                "الرياض": "Riyadh", "جدة": "Jeddah", "الدمام": "Dammam",
                "مكة": "Mecca", "المدينة": "Medina", "القصيم": "Qassim",
                "تبوك": "Tabuk", "الخبر": "Khobar",
            }
            result["city"] = city_map.get(city_match.group(1), "Riyadh")

        result["parser_version"] = "haraj_ksa_v1.0.0"
        result["schema_version"] = 1
        result["normalizer_version"] = "normalizer_v1.0.0"
        return result

    def _extract_year(self, text: str) -> int | None:
        match = re.search(r'\b(19\d{2}|20[0-2]\d)\b', text)
        return int(match.group(1)) if match else None

    def _extract_number(self, text: str) -> float:
        text = re.sub(r'[^\d.]', '', text.replace(",", ""))
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _extract_mileage(self, text: str) -> int | None:
        match = re.search(r'(\d[\d,]*)\s*km', text, re.IGNORECASE)
        return int(match.group(1).replace(",", "")) if match else None

    def _extract_spec(self, text: str) -> str | None:
        t = text.lower()
        if "gcc" in t or "خليجي" in t: return "GCC"  # noqa: E701
        if "american" in t or "us spec" in t or "امريكي" in t: return "US"  # noqa: E701
        if "japan" in t or "ياباني" in t: return "Japan"  # noqa: E701
        return None
