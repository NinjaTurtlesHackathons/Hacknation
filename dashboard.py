"""Statisches Dashboard. Liest NUR die drei Tabellen (experiments, claims, gates), nie den Code.
  python dashboard.py [tables] -> dashboard/index.html
"""
import html, os, sys
import numpy as np, pandas as pd
from asd import tables as T

src = sys.argv[1] if len(sys.argv) > 1 else "tables"
E, C, G = T.read("experiments", src), T.read("claims", src), T.read("gates", src)
E = E[E.policy != "hypothesis_test"]
N = E.groupby(["dataset", "policy", "seed"]).step.max().reset_index()   # letzter Schritt = N (oder Budget)
esc = lambda s: html.escape(str(s))

def curve_svg(dataset, w=640, h=260):
    """Anteil der Läufe mit Treffer nach t Experimenten (empirische Verteilungsfunktion von N)."""
    sub = N[N.dataset == dataset]; tmax = 150; cols = {"random": "#8a8f98", "gp_ei": "#2f6fdf", "hybrid": "#d9480f", "hybrid_neutral": "#2b8a3e"}
    paths, legend = [], []
    for j, (pol, g) in enumerate(sub.groupby("policy")):
        n = np.sort(g.step.to_numpy()); xs = np.arange(0, tmax + 1); ys = [(n <= t).mean() for t in xs]
        pts = " ".join(f"{40 + t / tmax * (w - 60):.1f},{h - 30 - y * (h - 50):.1f}" for t, y in zip(xs, ys))
        c = cols.get(pol, "#555"); paths.append(f'<polyline fill="none" stroke="{c}" stroke-width="2.2" points="{pts}"/>')
        legend.append(f'<text x="{w - 150}" y="{24 + 16 * j}" fill="{c}" font-size="12">{esc(pol)} (Ø N {g.step.mean():.1f})</text>')
    axes = (f'<line x1="40" y1="{h - 30}" x2="{w - 20}" y2="{h - 30}" stroke="currentColor" opacity=".4"/>'
            f'<line x1="40" y1="20" x2="40" y2="{h - 30}" stroke="currentColor" opacity=".4"/>'
            f'<text x="{w / 2}" y="{h - 6}" font-size="12" text-anchor="middle" fill="currentColor">Experimente t</text>'
            f'<text x="8" y="16" font-size="12" fill="currentColor">Anteil Läufe mit Treffer</text>'
            + "".join(f'<text x="{40 + t / tmax * (w - 60):.0f}" y="{h - 16}" font-size="10" text-anchor="middle" fill="currentColor">{t}</text>' for t in range(0, tmax + 1, 25)))
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Trefferkurve {esc(dataset)}">{axes}{"".join(paths)}{"".join(legend)}</svg>'

gate_rows = "".join(f'<tr class="{"ok" if str(r.passed) == "True" else "bad"}"><td>{"✔" if str(r.passed) == "True" else "✘"}</td><td>{esc(r.gate)}</td><td>{esc(r.reason)}</td></tr>' for r in G.itertuples())
claim_rows = "".join(f'<tr><td><code>{esc(r.claim_id)}</code></td><td>{esc(r.level)}</td><td>{esc(r.status)}</td><td>{esc(r.text)}</td></tr>' for r in C.itertuples())
page = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-Labor Dashboard</title><style>
:root{{--bg:#fbfbfa;--fg:#1d1f23;--mut:#666;--ok:#e6f4ea;--bad:#fdecea;--line:#ddd}}
@media (prefers-color-scheme: dark){{:root{{--bg:#16181c;--fg:#e8e8e8;--mut:#aaa;--ok:#173323;--bad:#3a1d1d;--line:#333}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1000px;padding:16px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}}
tr.ok td:first-child{{background:var(--ok)}}tr.bad td:first-child{{background:var(--bad)}}svg{{width:100%;height:auto;color:var(--fg)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}small{{color:var(--mut)}}
</style></head><body><h1>AI-Labor mit Prüfschicht</h1>
<small>Quelle: nur die Tabellen experiments ({len(E)} Zeilen), claims ({len(C)}), gates ({len(G)}).</small>
<h2>Gates</h2><table><tr><th></th><th>Gate</th><th>Grund</th></tr>{gate_rows}</table>
<h2>Experimente bis zum ersten Top-1-%-Treffer</h2><div class="grid">
<div><h3>Echte Ausbeuten</h3>{curve_svg("echt")}</div><div><h3>Negativkontrolle (Vertauschung je Seed)</h3>{curve_svg("negativkontrolle_je_seed")}</div></div>
<h2>Claims</h2><table><tr><th>ID</th><th>Level</th><th>Status</th><th>Aussage</th></tr>{claim_rows}</table></body></html>"""
os.makedirs("dashboard", exist_ok=True); open("dashboard/index.html", "w").write(page); print("dashboard/index.html")
