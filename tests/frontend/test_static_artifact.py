"""Validate the deterministic static frontend release artifact."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UI_DIR = ROOT / "ui"
MANIFEST = UI_DIR / "routes.manifest.json"
ASSET_REF = re.compile(r'(?:href|src)="([^"?#]+)"')


def _route_file(route: str) -> Path:
    name = "index" if route == "/" else route.removeprefix("/")
    return UI_DIR / f"{name}.html"


def test_manifest_routes_have_html_files():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    missing = [route for route in manifest["routes"] if not _route_file(route).is_file()]
    assert missing == [], f"Routes without HTML files: {missing}"


def test_local_static_asset_references_exist():
    missing: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for route in manifest["routes"]:
        page = _route_file(route)
        html = page.read_text(encoding="utf-8")
        for reference in ASSET_REF.findall(html):
            if reference.startswith(("http://", "https://", "data:", "mailto:")):
                continue
            if "${" in reference or "' +" in reference or '" +' in reference:
                continue
            asset = UI_DIR / reference
            if asset.suffix and not asset.is_file():
                missing.append(f"{page.name}: {reference}")

    assert missing == [], "Missing static assets:\n" + "\n".join(missing)


def test_dedicated_pages_ship_shared_assets():
    assert (UI_DIR / "detail.css").is_file()
    assert (UI_DIR / "detail-pages.js").is_file()
