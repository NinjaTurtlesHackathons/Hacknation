"""Records the 40 s live-run demo (frontend/demo.html) as a 1920x1080 video -> video/demo_live_run.webm (+ .mp4 if ffmpeg is present),
plus stills for review in frontend/screenshots/demo_*.png.   python frontend/record_demo.py [--run 2026-10-04b]"""
import argparse, functools, glob, http.server, os, shutil, subprocess, threading
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(D); OUT = os.path.join(ROOT, "video"); os.makedirs(OUT, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--run", default="2026-10-04b"); a = ap.parse_args()
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *x: None}), directory=D))
threading.Thread(target=srv.serve_forever, daemon=True).start()
tmp = os.path.join(OUT, "_rec"); shutil.rmtree(tmp, ignore_errors=True)
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
    ctx = br.new_context(viewport={"width": 1920, "height": 1080}, record_video_dir=tmp, record_video_size={"width": 1920, "height": 1080})
    pg = ctx.new_page(); fehler = []; pg.on("pageerror", lambda e: fehler.append(str(e)))
    pg.goto(f"http://127.0.0.1:{srv.server_port}/demo.html?rec=1&run={a.run}", wait_until="load")
    t = 0
    for s in (2, 6, 12, 17, 20, 23, 26, 31, 35, 37.5, 40.5):
        pg.wait_for_timeout(int((s - t) * 1000)); t = s
        pg.screenshot(path=os.path.join(D, "screenshots", f"demo_{int(s * 10):03d}.png"))
    pg.wait_for_timeout(1500); ctx.close(); br.close()
webm = os.path.join(OUT, "demo_live_run.webm"); shutil.move(glob.glob(os.path.join(tmp, "*.webm"))[0], webm); shutil.rmtree(tmp, ignore_errors=True)
ff = shutil.which("ffmpeg")
if ff: subprocess.run([ff, "-y", "-loglevel", "error", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", webm[:-5] + ".mp4"], check=False)
print("JS errors:", fehler or "none"); print("->", webm, "(+ mp4)" if ff else "(no ffmpeg: convert the webm in your editor or with ffmpeg)")
