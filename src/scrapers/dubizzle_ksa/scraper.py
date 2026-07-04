"""Dubizzle KSA scraper — shares parser logic with UAE, different base URL."""
from src.scrapers.base import BaseScraper
from src.scrapers.dubizzle_uae.parser import parse_listing


class DubizzleKSAScraper(BaseScraper):
    source = "dubizzle_ksa"
    base_url = "https://ksa.dubizzle.com"

    async def fetch_index(self, page: int) -> list[str]:
        session = await self.get_session()
        url = f"{self.base_url}/motors/used-cars/?page={page}"
        response = await session.get(url)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        links = []
        for link in soup.select("a[href*='/motors/used-cars/']"):
            href = link.get("href", "")
            if "/motors/used-cars/" in href and "/ads/" not in href:
                full_url = href if href.startswith("http") else f"{self.base_url}{href}"
                links.append(full_url)
        return list(set(links))

    async def fetch_listing(self, url: str) -> str:
        session = await self.get_session()
        response = await session.get(url)
        response.raise_for_status()
        return response.text

    def parse(self, html: str, url: str) -> dict:
        result = parse_listing(html, url)
        result["source"] = self.source
        result["country"] = "SA"
        result["original_currency"] = "SAR"
        result["parser_version"] = "dubizzle_ksa_v1.0.0"
        return result
