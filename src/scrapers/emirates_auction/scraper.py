"""Emirates Auction scraper — actual transaction (hammer) prices.

This is the most valuable data source: real sale prices, not asking prices.
Provides the ground truth for calibrating asking-to-transaction gap.
"""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper


class EmiratesAuctionScraper(BaseScraper):
    source = "emirates_auction"
    base_url = "https://www.emiratesauction.com"

    async def fetch_index(self, page: int) -> list[str]:
        session = await self.get_session()
        url = f"{self.base_url}/used-cars?page={page}"
        response = await session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        links = []
        for link in soup.select("a[href*='/used-cars/'], a[href*='/car/']"):
            href = link.get("href", "")
            if "/used-cars/" in href or "/car/" in href:
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
        result = {"url": url, "source": self.source, "country": "AE",
                  "original_currency": "AED", "city": "Dubai",
                  "seller_type": "auction"}

        # Auctions have distinct statuses
        if "sold" in html.lower() or "hammer" in html.lower():
            result["status"] = "sold_confirmed"
        elif "ended" in html.lower() or "closed" in html.lower():
            result["status"] = "expired"
        elif "live" in html.lower() or "upcoming" in html.lower():
            result["status"] = "active"
        else:
            result["status"] = "probably_sold"

        # Title
        title = soup.select_one("h1, .car-title, [class*='title'], .lot-title")
        title_text = title.get_text(strip=True) if title else ""
        result["make"], result["model"] = self._extract_make_model(title_text)
        result["year"] = self._extract_year(title_text)
        result["spec"] = self._extract_spec(title_text + " " + html)
        result["mileage_km"] = self._extract_mileage(title_text + " " + html)

        # Auction hammer price — the actual transaction price
        hammer = soup.select_one("[class*='hammer'], [class*='sold-price'], [class*='winning']")
        if hammer:
            result["asking_price"] = self._extract_number(hammer.get_text(strip=True))
        else:
            # If not sold yet, use estimated/starting bid
            bid = soup.select_one("[class*='price'], [class*='bid'], [class*='current']")
            result["asking_price"] = self._extract_number(bid.get_text(strip=True)) if bid else 0

        # External ID
        match = re.search(r'/(\d+)[/$]', url)
        result["external_id"] = match.group(1) if match else ""

        # Body type from description
        if "suv" in html.lower() or "4x4" in html.lower(): result["body_type"] = "SUV"
        elif "sedan" in html.lower(): result["body_type"] = "sedan"

        result["parser_version"] = "emirates_auction_v1.0.0"
        result["schema_version"] = 1
        result["normalizer_version"] = "normalizer_v1.0.0"
        return result

    def _extract_make_model(self, title: str) -> tuple[str, str]:
        tokens = title.split()
        return (tokens[0], tokens[1]) if len(tokens) >= 2 else ("", "")

    def _extract_year(self, text: str) -> int | None:
        match = re.search(r'\b(20[0-2]\d)\b', text)
        return int(match.group(1)) if match else None

    def _extract_number(self, text: str) -> float:
        text = re.sub(r'[^\d.]', '', text.replace(",", ""))
        try: return float(text)
        except ValueError: return 0.0

    def _extract_mileage(self, text: str) -> int | None:
        match = re.search(r'(\d[\d,]*)\s*km', text, re.IGNORECASE)
        return int(match.group(1).replace(",", "")) if match else None

    def _extract_spec(self, text: str) -> str | None:
        t = text.lower()
        if "gcc" in t: return "GCC"
        if "american" in t or "us spec" in t: return "US"
        return None
