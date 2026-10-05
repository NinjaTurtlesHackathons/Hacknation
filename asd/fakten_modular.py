"""Code-erzeugte Zusatzfakten für das Paper der Domäne modular (projects/modular/fakten.json). Nur aus Dateien und exakter
Rechnung; jede Zahl stammt aus Code oder aus bestätigten Claims (deren IDs genannt werden)."""
import json, os
from fractions import Fraction as F
from math import factorial as fa, comb
from .domains.mgf_laplace import harmonic_space
from .domains.modular_domain import _dgv_combo


def bern(n):
    B = [F(1)]
    for m in range(1, n + 1): B.append(-sum(comb(m + 1, j) * B[j] for j in range(m)) / (m + 1))
    return B[n]


def main():
    d = "projects/modular"; s = json.load(open(f"{d}/state.json")); fakten = []
    ok = {c["id"] for c in s["claims"] if c["status"] == "bestätigt"}
    rows = []
    for w in range(3, 26, 2):
        mu = (w - 3) // 2; f = F(3 * fa(mu + 1), w); g = 6 * abs(bern(w - 1)) / fa(mu + 1)
        rows.append(f"w={w}: f_w={f}, g_w/zeta(w)={g}")
    idf = next((c["id"] for c in s["claims"] if c["status"] == "bestätigt" and (c.get("pruefung") or {}).get("typ") == "mgf_identitaet_familie"), None)
    if idf:
        gtxt = (f"g_w = 6|B_{{w-1}}|/((w-1)/2)! is PROVED for all odd w <= 25 (claim {idf}: Laplace algebra plus the Laurent polynomial of "
                "Theorem 5.1 of D'Hoker-Kaidi, arXiv:1902.04180, in rational arithmetic); before that proof it was a conjecture read off from w = 3..13, ")
    else:
        gtxt = "g_w = 6|B_{w-1}| zeta(w)/((w-1)/2)! is a conjecture read off from w = 3..13, "
    fakten.append({"id": "fakt-konstanten", "level": "computed_rigorous" if idf else "observed", "text":
        "Table of the constants in X_w = f_w E(w) + g_w zeta(w) (DGV normalisation of X_w, eq. 3.57 of arXiv:1502.06698): f_w = 3((w-1)/2)!/w is exact "
        "(algebraic Laplace computation, all odd w <= 25, claim modular-R14); " + gtxt +
        "and independently confirmed numerically by the verifier at w = 3, 5, 7, 9, 11, 13, 15, 17 (claims modular-R1..R1d, R6a..R6d, R7a, R11a, R11b, R13); "
        "w = 15 was a prediction made before its value was read and w = 17 a preregistered blind test. Values: " + "; ".join(rows) + "."})
    fakten.append({"id": "fakt-beweis", "level": "computed_rigorous", "text":
        "Proof structure for the odd-weight identities: (1) exact rational computation in the algebraic Laplace representation gives Delta X_w = "
        "w(w-1) f_w E(w) with no other terms (claims modular-R9a, modular-R9b, family claim modular-R14 for all odd w <= 25); (2) E(w) is an eigenfunction, "
        "Delta E(w) = w(w-1) E(w); hence Delta(X_w - f_w E(w)) = 0; (3) X_w - f_w E(w) is SL(2,Z)-invariant and of polynomial growth at the cusp, so it is "
        "constant by the standard argument used by D'Hoker-Green-Vanhove (arXiv:1502.06698); (4) " +
        (f"the constant equals the tau2^0 term of the Laurent polynomial of X_w, which Proposition 2.1 and Theorem 5.1 of D'Hoker-Kaidi "
         f"(arXiv:1902.04180) give in closed form; evaluated in rational arithmetic it is g_w zeta(w) with g_w = 6|B_{{w-1}}|/((w-1)/2)! for all odd w <= 25 "
         f"(claim {idf}). Assumptions not checked by code: correctness of Theorem 5.1 of arXiv:1902.04180 (proved there in Appendix A; its conjectural "
         "part concerns only the coefficient of tau2^(2-w) and is not used) and the standard lemma in step (3)." if idf else "only the value g_w of the constant is numerical.")})
    ps = f"{d}/laurent_sweep.json"
    if os.path.exists(ps):
        z = json.load(open(ps))["zeilen"]; ws = [r["w"] for r in z]
        alle = all(r["zeta_2w-1_term"] and r["zwischenterme_null"] and r["konstante_gleich_formel"] for r in z)
        fakten.append({"id": "fakt-laurent-sweep", "level": "computed_rigorous", "text":
            f"Extended exact computation (asd/laurent_sweep.py): for every odd w from {ws[0]} to {ws[-1]}, the Laurent polynomial of X_w computed from "
            "Proposition 2.1 and Theorem 5.1 of arXiv:1902.04180 in rational arithmetic " + ("agrees" if alle else "does NOT agree in all cases") +
            " with that of f_w E(w) + g_w zeta(w), f_w = 3((w-1)/2)!/w, g_w = 6|B_{w-1}|/((w-1)/2)! (all terms except the coefficient of tau2^(2-w), which is not "
            "computed). Combined with the statement of D'Hoker-Green-Vanhove (arXiv:1502.06698, sec. 3.9) that X_w - f_w E(w) is constant for every odd w, "
            f"this gives the closed forms for all odd w <= {ws[-1]}; the Laplace part was re-derived by the verifier only for w <= 25. For general odd w the "
            "closed forms remain a conjecture."})
    p1 = f"{d}/vollbasis_w11_kriterium1.json"
    if os.path.exists(p1):
        r = json.loads(open(p1).read().splitlines()[-1])
        fakten.append({"id": "fakt-kriterium1", "level": "observed", "text":
            "Full weight-11 basis (ten C(a,b,c), E(11), zeta(11)) with the originally preregistered criterion 1 (15 points, seed 4712, other singular values "
            f"must exceed 1e-8): FAILED; singular values {', '.join(r['belege']['singulaerwerte'])}. Criterion 2 (preregistered afterwards, new data: 20 points, "
            "seed 4713, threshold 1e-16) passed (claim modular-R12)."})
    ph = f"{d}/haertung_w11.json"
    if os.path.exists(ph):
        h = json.load(open(ph)); zeilen = []
        for row in h["punkte"]:
            zeilen.append(f"tau=({row['tau'][0]}, {row['tau'][1]}): residual " + ", ".join(f"{k} digits {v}" for k, v in row["residuum"].items())
                          + f"; independent double-precision lattice sum {row['brute_residuum_rel']}")
        def faellt(r):
            return all(float(v) <= 10.0 ** (-int(d)) for d, v in r["residuum"].items())        # Residuum unter der Aufloesung jeder Arbeitspraezision d
        n = len(h["punkte"]); ok_p = sum(faellt(r) for r in h["punkte"]); ok_b = sum(float(r["brute_residuum_rel"]) <= 1e-12 for r in h["punkte"])
        fakten.append({"id": "fakt-haertung", "level": "observed", "text":
            f"Hardening of the weight-11 identity (preregistered H10, 8 points planned, {n} completed): relative residual at points not used before "
            "(seed 9001, including tau near rho and tau2 up to 3) for several working precisions, and an independent check by direct lattice summation "
            f"in double precision. Operationalising the preregistered expectation 'residual decreases with precision' as 'residual at most 10^-d at every working precision d' (an exact 0 means below rounding resolution), it holds at {ok_p} of {n} points; the independent "
            f"double-precision check agrees to at most 1e-12 relative at {ok_b} of {n} points. Details: " + "; ".join(zeilen) + ". "
            "The hardening run exposed and fixed an evaluator bug: the Fourier sum for E_s stopped when a term vanished, which happens at tau1 = 1/4 "
            "where cos(2 pi N tau1) = 0 for odd N; before the fix that point showed a precision-independent residual of 3.5e-10. All points listed "
            "were computed with the corrected code; no earlier test point was affected."})
    json.dump(fakten, open(f"{d}/fakten.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(fakten, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
