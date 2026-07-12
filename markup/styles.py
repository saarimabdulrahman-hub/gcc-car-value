"""Style removal helper."""

def remove_styles(soup) -> int:
    count = 0
    for el in soup.find_all("style"):
        el.decompose()
        count += 1
    for el in soup.find_all(attrs={"style": True}):
        del el["style"]
        count += 1
    return count
