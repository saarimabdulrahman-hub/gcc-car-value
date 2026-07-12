"""HTML Cleaner — removes scripts, styles, comments, hidden nodes."""

import re
from bs4 import BeautifulSoup, Comment


class HTMLCleaner:
    """Removes scripts, styles, comments, and marks hidden nodes from HTML."""

    def __init__(self, remove_scripts: bool = True,
                 remove_styles: bool = True,
                 remove_comments: bool = True,
                 detect_hidden: bool = True):
        self.remove_scripts = remove_scripts
        self.remove_styles = remove_styles
        self.remove_comments = remove_comments
        self.detect_hidden = detect_hidden

    def clean(self, soup: BeautifulSoup) -> dict:
        """Clean a BeautifulSoup document. Returns counts of removed elements."""
        result = {
            "scripts_removed": 0,
            "styles_removed": 0,
            "comments_removed": 0,
            "hidden_nodes_found": 0,
        }

        # Detect hidden FIRST — before removing inline styles which would strip the signal
        if self.detect_hidden:
            result["hidden_nodes_found"] = self._mark_hidden(soup)

        if self.remove_scripts:
            result["scripts_removed"] = self._remove_tags(soup, ["script", "noscript"])

        if self.remove_styles:
            result["styles_removed"] = self._remove_tags(soup, ["style"])
            result["styles_removed"] += self._remove_inline_styles(soup)

        if self.remove_comments:
            result["comments_removed"] = self._remove_comments(soup)

        return result

    @staticmethod
    def _remove_tags(soup, tag_names: list[str]) -> int:
        count = 0
        for tag in tag_names:
            for el in soup.find_all(tag):
                el.decompose()
                count += 1
        return count

    @staticmethod
    def _remove_inline_styles(soup) -> int:
        count = 0
        for el in soup.find_all(attrs={"style": True}):
            del el["style"]
            count += 1
        return count

    @staticmethod
    def _remove_comments(soup) -> int:
        count = 0
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()
            count += 1
        return count

    @staticmethod
    def _mark_hidden(soup) -> int:
        """Mark hidden nodes with data-was-hidden attribute. Doesn't delete them."""
        count = 0
        for el in soup.find_all(style=True):
            style = el.get("style", "").lower()
            if "display:none" in style or "visibility:hidden" in style:
                el["data-was-hidden"] = "true"
                count += 1
        for el in soup.find_all(attrs={"hidden": True}):
            el["data-was-hidden"] = "true"
            count += 1
        for el in soup.find_all(attrs={"aria-hidden": "true"}):
            el["data-was-hidden"] = "true"
            count += 1
        return count
