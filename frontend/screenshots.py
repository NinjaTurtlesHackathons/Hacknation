"""Playwright-Screenshots: Start, Pipeline (mitten im Lauf), Ergebnisse; hell/dunkel und mobil -> frontend/screenshots/.
  python frontend/screenshots.py   (startet selbst einen lokalen HTTP-Server auf frontend/)"""
import functools, http.server, os, threading, time
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, "screenshots"); os.makedirs(OUT, exist_ok=True)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=D))
threading.Thread(target=srv.serve_forever, daemon=True).start(); B = f"http://127.0.0.1:{srv.server_port}"
SEITEN = [("start", "/index.html", 16000), ("pipeline", "/run.html?run=2026-10-04b&at=60", 1500), ("results", "/results.html", 1500)]
fehler = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
    for modus, vp, schema in [("light", {"width": 1440, "height": 1000}, "light"), ("dark", {"width": 1440, "height": 1000}, "dark"), ("mobile", {"width": 360, "height": 780}, "light")]:
        ctx = br.new_context(viewport=vp, color_scheme=schema, ignore_https_errors=True, device_scale_factor=1 if modus != "mobile" else 2)
        for name, url, warte in SEITEN:
            pg = ctx.new_page(); pg.on("pageerror", lambda e, n=name: fehler.append(f"{n}: {e}"))
            pg.on("console", lambda m, n=name: fehler.append(f"{n}: {m.text}") if m.type == "error" else None)
            pg.goto(B + url, wait_until="networkidle"); pg.wait_for_timeout(warte)
            pg.screenshot(path=f"{OUT}/{name}-{modus}.png", full_page=True); pg.close()
        ctx.close()
    br.close()
print("\n".join(fehler) or "keine JS-Fehler"); print("->", OUT)
