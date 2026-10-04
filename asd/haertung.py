"""Härtung numerischer MGF-Relationen (Präregistrierung H10): Residuum an neuen Punkten bei mehreren Präzisionen
und unabhängige Kontrolle über direkte Gittersummen in doppelter Genauigkeit.
  python -m asd.haertung '<json terme>' --seed 9001 --punkte 8 --dps 30 45 60 --out projects/modular/haertung_w11.json"""
import argparse, json, random, time
import mpmath as mp
from fractions import Fraction as Fr
from .domains import mgf, mgf_brute


def punkte(seed, n):
    r = random.Random(seed); pts = [("0.500000", "0.866026"), ("-0.250000", "0.968246")]     # nahe rho und am Rand des Fundamentalbereichs
    while len(pts) < n: pts.append((f"{r.uniform(-0.5, 0.5):.6f}", f"{r.uniform(0.9, 3.0):.6f}"))
    return pts[:n]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("terme"); ap.add_argument("--seed", type=int, default=9001)
    ap.add_argument("--punkte", type=int, default=8); ap.add_argument("--dps", type=int, nargs="+", default=[30, 45, 60])
    ap.add_argument("--brute-L", type=int, default=20); ap.add_argument("--out", required=True); a = ap.parse_args()
    terme = [(Fr(str(c)), m) for c, m in json.loads(a.terme)]; out = {"terme": [[str(c), m] for c, m in terme], "punkte": [], "datum": time.strftime("%Y-%m-%d %H:%M")}
    for t1, t2 in punkte(a.seed, a.punkte):
        row = {"tau": [t1, t2], "residuum": {}}
        for dps in a.dps:
            with mp.workdps(dps + 10):
                vals = [mp.mpf(c.numerator) / c.denominator * mgf.value(mgf.parse(m), t1, t2, dps) for c, m in terme]
                res = abs(mp.fsum(vals)) / max(abs(v) for v in vals)
            row["residuum"][str(dps)] = mp.nstr(res, 3)
        bv = []
        for c, m in terme:
            pa = mgf.parse(m)[1]; v = 1.0
            for t, x, p in pa:
                v *= (mgf_brute.C(x, float(t1), float(t2), a.brute_L) if t == "C" else mgf_brute.E(x, float(t1), float(t2)) if t == "E" else float(mp.zeta(x))) ** p
            bv.append(float(c) * v)
        row["brute_residuum_rel"] = f"{abs(sum(bv)) / max(abs(x) for x in bv):.3e}"
        out["punkte"].append(row); print(json.dumps(row), flush=True)
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
