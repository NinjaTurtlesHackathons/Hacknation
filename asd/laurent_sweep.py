"""Laurent-Polynom der DGV-Kombination X_w für alle ungeraden w <= W (rationale Arithmetik, D'Hoker-Kaidi Prop. 2.1 / Thm. 5.1):
prüft, dass es mit dem von f_w E_w + g_w zeta(w) übereinstimmt (f_w = 3((w-1)/2)!/w, g_w = 6|B_{w-1}|/((w-1)/2)!), ohne den Term l_{2-w}.
  python -m asd.laurent_sweep 61 --out projects/modular/laurent_sweep.json"""
import argparse, json, time
from fractions import Fraction as Fr
from math import factorial as fa
from .domains.mgf_laurent import ell_C
from .domains.modular_domain import _dgv_combo, _g_bernoulli


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("W", type=int); ap.add_argument("--out", required=True); a = ap.parse_args()
    out = {"datum": time.strftime("%Y-%m-%d %H:%M"), "zeilen": []}
    for w in range(3, a.W + 1, 2):
        t = time.time(); X = _dgv_combo(w); f = Fr(3 * fa((w - 1) // 2), w)
        L = {k: sum(Fr(c) * ell_C(abc, k) for abc, c in X.items()) for k in range(w - 1)}
        z = {"w": w, "zeta_2w-1_term": L[0] == f * Fr(4 * fa(2 * w - 3), fa(w - 2) * fa(w - 1)),
             "zwischenterme_null": all(L[k] == 0 for k in range(1, w - 1) if k != (w - 1) // 2),
             "konstante": str(L[(w - 1) // 2]), "konstante_gleich_formel": L[(w - 1) // 2] == _g_bernoulli(w), "sekunden": round(time.time() - t, 1)}
        out["zeilen"].append(z); print(json.dumps(z), flush=True)
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
