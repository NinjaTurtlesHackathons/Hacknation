"""Code-Prüfer für getypte Behauptungen (Gitter-Domäne). Kein LLM entscheidet über Wahrheit.

Der Prüfer rechnet unabhängig nach: eigene, höhere Auflösung, eigene Raster und eigene nu-Gitter. Eine
Behauptung gilt nur, wenn sie diese Nachrechnung übersteht. Belegt durch Stechly et al. 2023 (externer
Prüfer 16 % -> ~40 %, Selbstkritik 16 % -> 1 %), siehe research/evidence.md.

Prüfungstypen:
  argmin2d          {nu, erwartet: hexagonal|quadratisch|rechteckig|rhombisch|schief, y?: Seitenverhältnis}
  argmin3d          {nu, erwartet: bcc|fcc|sc}          (Vergleich der Kandidaten + Bain-Pfad-Scan)
  vorzeichenwechsel {groesse: diff_hex_quadrat|eig_min_quadrat|bain_fcc, nu_lo, nu_hi}
  koexistenz        {nu}                                (hexagonal und quadratisch beide lokal stabil)
  grenzwert         {groesse: y_inf|kappa, erwartet, toleranz}
"""
import numpy as np
from .domains import lattice as L

HI2, HI3 = (48, 64), (10, 14)


def _quantity(name, nu):
    if name == "diff_hex_quadrat": return L.compare2d(L.I, L.RHO, nu, HI2)["diff"]
    if name == "eig_min_quadrat": return min(L.hessian2d(L.I, nu, R=HI2)["eigenwerte"])
    if name == "bain_fcc": return L.bain_curvature(np.sqrt(2), nu, R=HI3)["kruemmung"]
    raise ValueError(name)


def check(p):
    """Gibt (bestanden: bool, Begründung: str, Belege: dict) zurück."""
    t = p.get("typ")
    try:
        if t == "argmin2d":
            nu = float(p["nu"]); r = L.minimize2d(nu, grid=18, n_polish=6, R_fine=HI2)
            typ = r["typ"]; ok = typ.split("(")[0] == p["erwartet"]
            if ok and p["erwartet"] == "rechteckig" and p.get("y") is not None:
                y = L.rect_optimum(nu, 1.0, 1.4, HI2)["y"]; ok = abs(y - float(p["y"])) < 2e-3; typ += f", y_pruefer={y:.5f}"
            if ok:
                h = L.hessian2d(complex(*r["tau"]), nu, R=HI2); ok = h["stabil"] or p["erwartet"] in ("hexagonal", "quadratisch")
            return ok, f"Prüfer-Suche (18er-Raster, 6 Polituren, R={HI2}): {typ}", r
        if t == "argmin3d":
            nu = float(p["nu"]); E = {n: L.energy3d(n, nu, HI3)["T"] for n in ("bcc", "fcc", "sc")}
            cas = np.linspace(0.8, 1.7, 19); bain = [L.T(L.bct(c), nu, HI3)[0] for c in cas]
            best = min(E, key=E.get); bain_min = float(cas[int(np.argmin(bain))])
            ok = best == p["erwartet"].lower() and min(bain) >= E[best] - 1e-9 * E[best]
            return ok, f"Energien {', '.join(f'{k}={v:.6f}' for k, v in E.items())}; Bain-Minimum bei c/a={bain_min:.3f}", {"E": E}
        if t == "vorzeichenwechsel":
            lo, hi = float(p["nu_lo"]), float(p["nu_hi"])
            if not (0 < hi - lo <= 0.05 + 1e-9): return False, "Intervall fehlt oder breiter als 0,05", {}
            a, b = _quantity(p["groesse"], lo), _quantity(p["groesse"], hi)
            return bool(np.sign(a) != np.sign(b)), f"{p['groesse']}: f({lo})={a:.3e}, f({hi})={b:.3e}", {"f_lo": a, "f_hi": b}
        if t == "koexistenz":
            nu = float(p["nu"]); hq = L.hessian2d(L.I, nu, R=HI2); hh = L.hessian2d(L.RHO, nu, R=HI2)
            ok = hq["stabil"] and hh["stabil"]
            return ok, f"bei nu={nu}: quadratisch stabil={hq['stabil']}, hexagonal stabil={hh['stabil']}", {"q": hq, "h": hh}
        if t == "grenzwert":
            r = L.asymptote(nus=(100, 160, 250, 400, 640, 1000)); key = {"y_inf": "y_inf_fit", "kappa": "kappa_fit"}[p["groesse"]]
            tol = 2e-4 if p["groesse"] == "y_inf" else 5e-3          # fest: Toleranzen kommen nie aus der Behauptung (Befund H4)
            ok = abs(r[key] - float(p["erwartet"])) <= tol
            return ok, f"Prüfer-Fit über nu={r['nus']}: {key}={r[key]:.6f} (Toleranz {tol})", r
        if t == "vergleich_nd":
            nu = float(p["nu"]); X = p["gitter"].lower(); d = 4 if X in L.LAT4 else 3
            others = [g.lower() for g in p.get("gegen") or (L.LAT4 if d == 4 else L.LAT3) if g.lower() != X]
            Rs = [(4, 6), (6, 8)] if d == 4 else [(8, 12), (10, 14)]
            E = {R: {g: L.energy_nd(g, nu, R)["T"] for g in [X] + others} for R in Rs}
            marg = {g: [E[R][g] - E[R][X] for R in Rs] for g in others}
            ok = all(min(m) > 0 and min(m) > abs(m[1] - m[0]) for m in marg.values())
            return ok, f"nu={nu}: T(andere)-T({X}) bei R={Rs}: " + ", ".join(f"{g}: {m[0]:.4g}/{m[1]:.4g}" for g, m in marg.items()), {"E": {str(k): v for k, v in E.items()}}
        if t == "argmin_nd":
            d, nu, X = int(p["d"]), float(p["nu"]), p["erwartet"].lower()
            r = L.minimize_nd(d, nu, starts=4, seed=1234); tx = r["referenz_T"][X]
            better = [o for o in r["laeufe"] if o["T"] < tx * (1 - 1e-4)]
            found = sum(o["gitter"] == X for o in r["laeufe"])
            ok = not better and found >= 1
            return ok, (f"Prüfer-Suche d={d}, nu={nu}, 4 Starts (Seed 1234): Gitter {[o['gitter'] for o in r['laeufe']]}, "
                        f"T {[round(o['T'], 5) for o in r['laeufe']]}, T({X})={tx:.5f}, besser als {X}: {len(better)}"), r
    except Exception as e:
        return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}
    return False, f"unbekannter Prüfungstyp {t}", {}
