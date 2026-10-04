"""Funktionstest im Browser: Hash-Kette nachrechnen (muss intakt sein), manipulieren (muss brechen), Zertifikat mit Pyodide
nachrechnen (PASS) und manipulieren (FAIL).   python frontend/verify_check.py [--ohne-pyodide]"""
import functools, http.server, os, sys, threading
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=D))
threading.Thread(target=srv.serve_forever, daemon=True).start(); B = f"http://127.0.0.1:{srv.server_port}"
ok = True
def pruefe(name, bed, txt):
    global ok; ok &= bed; print(("OK   " if bed else "FAIL ") + name + ": " + txt)
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
    pg = br.new_context(ignore_https_errors=True).new_page(); fehler = []
    pg.on("pageerror", lambda e: fehler.append(str(e)))
    pg.goto(f"{B}/run.html?run=2026-10-04b&claim=proofreading-O19", wait_until="load")
    pg.click("#hv"); pg.wait_for_function("document.querySelector('#hr').textContent.match(/Intact|Broken/)", timeout=60000)
    t = pg.inner_text("#hr"); pruefe("chain re-verify", "Intact" in t, t)
    pg.click("#ht"); pg.wait_for_function("document.querySelector('#hr').textContent.includes('Broken')", timeout=60000)
    t = pg.inner_text("#hr"); pruefe("chain tamper", "Broken" in t, t)
    if "--ohne-pyodide" not in sys.argv:
        pg.click("#cv"); pg.wait_for_function("document.querySelector('#cr').textContent.match(/PASS|FAIL|could not|Error/)", timeout=240000)
        t = pg.inner_text("#cr"); pruefe("certificate re-verify (Pyodide)", "PASS" in t, t)
        pg.click("#ct"); pg.wait_for_function("document.querySelector('#cr').textContent.includes('FAIL')", timeout=240000)
        t = pg.inner_text("#cr") + " | " + pg.inner_text("#co")[:200]; pruefe("certificate tamper", "FAIL" in t, t)
    pruefe("no JS errors", not fehler, "; ".join(fehler) or "none")
    br.close()
sys.exit(0 if ok else 1)
