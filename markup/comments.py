"""Comment removal — standalone helper."""

from bs4 import Comment


def remove_comments(soup) -> int:
    """Remove all HTML comments. Returns count removed."""
    count = 0
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
        count += 1
    return count
