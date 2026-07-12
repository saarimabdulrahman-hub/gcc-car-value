"""Script removal helper."""

def remove_scripts(soup) -> int:
    count = 0
    for tag_name in ("script", "noscript"):
        for el in soup.find_all(tag_name):
            el.decompose()
            count += 1
    return count
