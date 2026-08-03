#!/usr/bin/env python3
"""Validate that every production frontend route returns 200.

Reads ui/routes.manifest.json and requests each route against a base URL.
Exit code 0 if all routes return 200, 1 otherwise.

Usage:
    python scripts/validate_routes.py                      # uses manifest default
    python scripts/validate_routes.py https://staging.host  # override base
    FRONTEND_BASE_URL=https://... python scripts/validate_routes.py
"""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "ui" / "routes.manifest.json"
TIMEOUT = 15


def base_url(manifest: dict) -> str:
    if len(sys.argv) > 1:
        return sys.argv[1].rstrip("/")
    env_key = manifest.get("base_url_env", "FRONTEND_BASE_URL")
    return os.getenv(env_key, manifest["default_base_url"]).rstrip("/")


def check(url: str) -> tuple[int | None, str]:
    req = urllib.request.Request(url, method="GET",
                                 headers={"User-Agent": "route-validator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, e.reason
    except Exception as e:  # noqa: BLE001 — surface any transport error as a failure
        return None, str(e)[:120]


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = base_url(manifest)
    routes = manifest["routes"]
    print(f"Validating {len(routes)} routes against {base}\n")

    failures = []
    for route in routes:
        url = f"{base}{route}"
        status, detail = check(url)
        ok = status == 200
        mark = "OK " if ok else "FAIL"
        print(f"  [{mark}] {status if status is not None else 'ERR'}  {route}"
              + (f"  ({detail})" if detail else ""))
        if not ok:
            failures.append((route, status, detail))

    print()
    if failures:
        print(f"{len(failures)} route(s) failed:")
        for route, status, detail in failures:
            print(f"  - {route}: {status} {detail}")
        return 1
    print(f"All {len(routes)} routes returned 200.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
