"""QA sweep: load every ui/*.html page, collect console errors, 4xx responses,
and horizontal overflow at desktop + mobile widths.

Serves ui/ itself on an ephemeral port, so there is no server to start separately.

Usage: python scripts/qa_sweep.py
"""
import functools
import glob
import http.server
import os
import socketserver
import threading

from playwright.sync_api import sync_playwright


def serve_ui() -> tuple[int, socketserver.TCPServer]:
    """Serve ui/ on an OS-assigned free port. Returns (port, server)."""
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory="ui"
    )
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    httpd.RequestHandlerClass.log_message = lambda *a, **k: None  # quiet
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1], httpd


def main() -> None:
    port, httpd = serve_ui()
    base = f"http://127.0.0.1:{port}"
    pages = sorted(os.path.basename(x) for x in glob.glob("ui/*.html"))
    fail = 0
    print(f"serving ui/ on {base}\n")
    print(f"{'PAGE':22}{'ERR':5}{'4xx':5}{'OVFL1440':10}{'OVFL390':9}TEXT")
    print("-" * 68)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name in pages:
            errors: list[str] = []
            bad: list[str] = []
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.on(
                "console",
                lambda m: errors.append(m.text[:70]) if m.type == "error" else None,
            )
            page.on(
                "response",
                lambda r: bad.append(f"{r.status}:{r.url.split('/')[-1][:20]}")
                if r.status >= 400
                else None,
            )
            try:
                page.goto(f"{base}/{name}", wait_until="networkidle", timeout=25000)
                page.wait_for_timeout(800)
                ov_desktop = page.evaluate(
                    "() => document.documentElement.scrollWidth"
                    " > document.documentElement.clientWidth + 2"
                )
                text_len = len(page.inner_text("body").strip())

                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(500)
                ov_mobile = page.evaluate(
                    "() => document.documentElement.scrollWidth"
                    " > document.documentElement.clientWidth + 2"
                )

                print(
                    f"{name:22}{len(errors):<5}{len(bad):<5}"
                    f"{str(ov_desktop):10}{str(ov_mobile):9}{text_len}"
                )
                if errors:
                    print(f"     err: {errors[:2]}")
                    fail += 1
                if bad:
                    print(f"     4xx: {bad[:3]}")
                if text_len < 200:
                    print("     WARN: page nearly empty")
                    fail += 1
                if ov_mobile:
                    print("     WARN: horizontal overflow at 390px")
            except Exception as exc:  # noqa: BLE001 - report, do not abort the sweep
                print(f"{name:22}LOADFAIL {str(exc)[:44]}")
                fail += 1
            page.close()
        browser.close()

    httpd.shutdown()
    print("-" * 68)
    print(f"pages={len(pages)} pages_with_problems={fail}")


if __name__ == "__main__":
    main()
