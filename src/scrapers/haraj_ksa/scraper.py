"""Haraj KSA scraper — Saudi Arabia's largest car marketplace."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper

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

        result["make"], result["model"] = self._extract_make_model(title_text)
        result["year"] = self._extract_year(title_text)
        result["spec"] = self._extract_spec(title_text + " " + html)
        result["mileage_km"] = self._extract_mileage(title_text + " " + html)

        # Price — Haraj prices are in SAR
        price_elem = soup.select_one("[class*='price'], .price-value, td:contains('السعر') + td")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            result["asking_price"] = self._extract_number(price_text)
        else:
            result["asking_price"] = 0

        # External ID
        match = re.search(r'/(\d+)[/$]', url)
        result["external_id"] = match.group(1) if match else ""

        # Body type
        if "suv" in html.lower() or "دفع رباعي" in html:
            result["body_type"] = "SUV"
        elif "sedan" in html.lower() or "سيدان" in html:
            result["body_type"] = "sedan"

        # Transmission
        if "automatic" in html.lower() or "اوتوماتيك" in html or "أوتوماتيك" in html:
            result["transmission"] = "automatic"
        elif "manual" in html.lower() or "عادي" in html:
            result["transmission"] = "manual"

        # City
        city_match = re.search(r'(الرياض|جدة|الدمام|مكة|المدينة|القصيم|تبوك|الخبر)', html)
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

    def _extract_make_model(self, title: str) -> tuple[str, str]:
        # Handle both Arabic and English titles
        tokens = title.split()
        return (tokens[0], tokens[1]) if len(tokens) >= 2 else ("", "")

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
        if "gcc" in t or "خليجي" in t: return "GCC"
        if "american" in t or "us spec" in t or "امريكي" in t: return "US"
        if "japan" in t or "ياباني" in t: return "Japan"
        return None
