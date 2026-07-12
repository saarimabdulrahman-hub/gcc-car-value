"""Text extraction utilities — visible text, normalized, whitespace cleanup."""

import re


def extract_text(node, strip: bool = True, normalize_ws: bool = True) -> str:
    """Extract text from a DOMNode, with whitespace normalization.

    Args:
        node: DOMNode to extract text from.
        strip: Remove leading/trailing whitespace.
        normalize_ws: Collapse multiple whitespace chars to single space.
    """
    if node is None:
        return ""
    text = node.text_stripped if strip else node.text
    if normalize_ws and text:
        text = re.sub(r'\s+', ' ', text)
        if strip:
            text = text.strip()
    return text


def extract_visible_text(node) -> str:
    """Extract text only from visible child nodes."""
    if node is None:
        return ""
    parts = []
    for child in node.children:
        if child.is_visible:
            t = extract_text(child)
            if t:
                parts.append(t)
    return " ".join(parts)
