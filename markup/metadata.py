"""HTML Metadata Extractor — title, description, OG tags, Twitter cards, etc."""

from bs4 import BeautifulSoup
from markup.models import HTMLMetadata


class MetadataExtractor:
    """Extracts metadata from HTML documents."""

    def extract(self, soup: BeautifulSoup) -> HTMLMetadata:
        meta = HTMLMetadata()

        # Title
        title_tag = soup.title
        if title_tag:
            meta.title = title_tag.get_text(strip=True)

        # Meta description
        desc = soup.find("meta", attrs={"name": "description"})
        if desc:
            meta.description = desc.get("content", "")

        # Keywords
        kw = soup.find("meta", attrs={"name": "keywords"})
        if kw:
            meta.keywords = kw.get("content", "")

        # Language
        html_tag = soup.find("html")
        if html_tag:
            meta.language = html_tag.get("lang", html_tag.get("xml:lang", ""))

        # Charset
        charset_tag = soup.find("meta", attrs={"charset": True})
        if charset_tag:
            meta.charset = charset_tag.get("charset", "")
        else:
            ct = soup.find("meta", attrs={"http-equiv": lambda v: v and v.lower() == "content-type"})
            if ct:
                content = ct.get("content", "")
                import re
                m = re.search(r'charset=([^\s;]+)', content)
                if m:
                    meta.charset = m.group(1)

        # Generator
        gen = soup.find("meta", attrs={"name": "generator"})
        if gen:
            meta.generator = gen.get("content", "")

        # Viewport
        vp = soup.find("meta", attrs={"name": "viewport"})
        if vp:
            meta.viewport = vp.get("content", "")

        # Canonical URL
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical:
            meta.canonical_url = canonical.get("href", "")

        # OpenGraph
        meta.og_title = self._meta_content(soup, "og:title")
        meta.og_description = self._meta_content(soup, "og:description")
        meta.og_image = self._meta_content(soup, "og:image")
        meta.og_type = self._meta_content(soup, "og:type")

        # Twitter
        meta.twitter_card = self._meta_content(soup, "twitter:card")
        meta.twitter_title = self._meta_content(soup, "twitter:title")

        return meta

    @staticmethod
    def _meta_content(soup, property_name: str) -> str:
        tag = soup.find("meta", attrs={"property": property_name})
        if not tag:
            tag = soup.find("meta", attrs={"name": property_name})
        return tag.get("content", "") if tag else ""
