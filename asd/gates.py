"""Gates: Gate.check(results) -> (bestanden, Grund). Die KI akzeptiert nichts selbst; nur diese Prüfungen."""
import json, os, shutil, subprocess
import numpy as np
from .stats import perm_test, ratio_ci, bh, first_hit_moments

MIN_SEEDS = 20; ALPHA = 0.05; Q = 0.1


def N_of(results, policy, dataset="echt"):
    rs = sorted([r for r in results["runs"] if r["policy"] == policy and r["dataset"] == dataset], key=lambda r: r["seed"])
    return [r["N"] for r in rs], [r["run_id"] for r in rs]


def compare(results, better, base, dataset="echt"):
    """Gepaarter Test 'better braucht weniger Experimente als base' + Speedup E[N_base]/E[N_better] mit KI."""
    a, ida = N_of(results, better, dataset); b, idb = N_of(results, base, dataset)
    sp, ci = ratio_ci(b, a); p = perm_test(a, b)
    return dict(better=better, base=base, dataset=dataset, seeds=len(a), mean_better=float(np.mean(a)),
                mean_base=float(np.mean(b)), speedup=sp, ci95=ci, p=p, run_ids=ida + idb)


class Gate:
    name = "gate"
    def check(self, results): raise NotImplementedError


class LeakGate(Gate):
    name = "G0_leck"
    def check(self, results):
        bad = [r["run_id"] for r in results["runs"] if not r["leak_ok"]]
        return (not bad, "Jeder Lauf: Zahl der Lab-Aufrufe = N" if not bad else f"Leck in {bad[:5]}")


class TheoryGate(Gate):
    """Theorie-Check: Zufallssuche muss E[N] = (n+1)/(k+1) treffen (|z| < 3)."""
    name = "G1_theorie_zufall"
    def __init__(self, dataset="echt"): self.dataset = dataset; self.name += f"_{dataset}"
    def check(self, results):
        N, _ = N_of(results, "random", self.dataset)
        if not N: return False, "keine Zufallsläufe"
        k = next(r["k"] for r in results["runs"] if r["dataset"] == self.dataset)
        mean, var = first_hit_moments(results["n"], k); z = (np.mean(N) - mean) / np.sqrt(var / len(N))
        return abs(z) < 3, f"gemessen {np.mean(N):.1f}, Theorie {mean:.1f}, z = {z:.2f} (Schranke |z| < 3, {len(N)} Seeds)"


class ReproGate(Gate):
    """Checkpoint 23:15: die neue Pipeline reproduziert die Rohdaten aus results_selftest.json.
    Streng geprüft: echt/random, echt/gp_ei, negativkontrolle/random. negativkontrolle/gp_ei nur berichtet:
    auf vertauschten Ausbeuten ist die EI-Fläche flach, argmax hängt dort von BLAS-Rundung ab
    (auch das unveränderte lab.py liefert auf dieser Maschine andere Werte als die gespeicherten)."""
    name = "G2_reproduktion_selftest"
    def check(self, results):
        ref = json.load(open("results_selftest.json"))
        msgs, ok = [], True
        for lab, ds, p, strict in [("echt", "echt", "random", True), ("echt", "echt", "gp_ei", True),
                                   ("negativkontrolle_vertauscht", "negativkontrolle", "random", True),
                                   ("negativkontrolle_vertauscht", "negativkontrolle", "gp_ei", False)]:
            N, _ = N_of(results, p, ds); R = ref[lab][p]["raw"][:len(N)]; same = N == R
            if strict: ok &= same
            msgs.append(f"{ds}/{p}: " + ("gleich" if same else ("ABWEICHUNG" if strict else
                        f"maschinenabhängig, Ø {np.mean(N):.1f} statt {np.mean(R):.1f} (nur berichtet)")))
        return ok, "; ".join(msgs)


class BaselineGate(Gate):
    """Pflicht-Prüfung 1 / Gate 3: >= 20 Seeds, p < 0,05 und KI-Untergrenze des Speedups > 1."""
    def __init__(self, better, base, name, dataset="echt"):
        self.better, self.base, self.name, self.dataset = better, base, name, dataset
    def check(self, results):
        c = compare(results, self.better, self.base, self.dataset); results.setdefault("comparisons", {})[self.name] = c
        ok = c["seeds"] >= MIN_SEEDS and c["p"] < ALPHA and c["ci95"][0] > 1
        return ok, (f"{self.better} vs {self.base} ({self.dataset}): Ø N {c['mean_better']:.1f} vs {c['mean_base']:.1f}, "
                    f"Speedup {c['speedup']:.2f} (95 %-KI {c['ci95'][0]:.2f}–{c['ci95'][1]:.2f}), p = {c['p']:.4f}, Seeds {c['seeds']}")


class NegControlGate(Gate):
    """Pflicht-Prüfung 2: mit vertauschten Ausbeuten darf keine Strategie den Zufall schlagen."""
    def __init__(self, policy, dataset="negativkontrolle_je_seed"):
        self.policy, self.dataset = policy, dataset
        self.name = f"G4_negativkontrolle_{policy}" + ("_seed7" if dataset == "negativkontrolle" else "")
    def check(self, results):
        c = compare(results, self.policy, "random", self.dataset); results.setdefault("comparisons", {})[self.name] = c
        ok = not (c["p"] < ALPHA and c["ci95"][0] > 1)
        return ok, f"Speedup {c['speedup']:.2f} (KI {c['ci95'][0]:.2f}–{c['ci95'][1]:.2f}), p = {c['p']:.3f}: " + ("kein Effekt, wie erwartet" if ok else "Strategie schlägt Zufall auf Rauschen: Fehler im Code")


class ContaminationGate(Gate):
    """Pflicht-Prüfung 3 / H2: bleibt der Gewinn mit neutralen Codes + Deskriptoren bestehen?"""
    name = "G5_kontamination_H2"
    def check(self, results):
        c = compare(results, "hybrid_neutral", "gp_ei"); results.setdefault("comparisons", {})["H2"] = c
        n1, _ = N_of(results, "hybrid"); n2, _ = N_of(results, "hybrid_neutral")
        drop = ratio_ci(n2, n1); c["hybrid_vs_neutral"] = {"ratio": drop[0], "ci95": drop[1], "p": perm_test(n1, n2)}
        ok = c["p"] < ALPHA and c["ci95"][0] > 1
        return ok, (f"hybrid_neutral vs gp_ei: Speedup {c['speedup']:.2f} (KI {c['ci95'][0]:.2f}–{c['ci95'][1]:.2f}), p = {c['p']:.4f}; "
                    f"Ø N hybrid {np.mean(n1):.1f} vs hybrid_neutral {np.mean(n2):.1f} (Verhältnis {drop[0]:.2f}, KI {drop[1][0]:.2f}–{drop[1][1]:.2f}). "
                    + ("Gewinn bleibt ohne Namen bestehen." if ok else "Gegenüber gp_ei ist kein Gewinn belegt; wird offen berichtet."))


class BHGate(Gate):
    """Pflicht-Prüfung 4: Benjamini-Hochberg über alle Tests (m = Gesamtzahl), q = 0,1. Setzt Hypothesen-Status."""
    name = "G6_benjamini_hochberg"
    def check(self, results):
        fam = [(f"vergleich:{k}", v["p"]) for k, v in results.get("comparisons", {}).items()]
        fam += [(f"hypothese:{h['id']}", h["p"]) for h in results.get("hyptests", [])]
        rej, adj = bh([p for _, p in fam], Q); results["bh"] = {name: {"p": p, "p_adj": float(a), "abgelehnt": bool(r)}
                                                               for (name, p), a, r in zip(fam, adj, rej)}
        for h in results.get("hyptests", []):
            b = results["bh"][f"hypothese:{h['id']}"]; h["p_adj"] = b["p_adj"]
            h["status"] = "bestätigt" if b["abgelehnt"] else ("widerlegt" if h["p_gegenteil"] < ALPHA else "offen")
        n_conf = sum(h["status"] == "bestätigt" for h in results.get("hyptests", []))
        return True, f"m = {len(fam)} Tests, {int(rej.sum())} nach BH (q = {Q}) signifikant; KI-Hypothesen bestätigt: {n_conf}/{len(results.get('hyptests', []))}"


class LeanGate(Gate):
    """Lemma E[N_random] = (n+1)/(k+1) in Lean 4 geprüft (lean/ENRandom.lean)."""
    name = "G7_lean_lemma"
    def check(self, results):
        lean = shutil.which("lean") or os.path.expanduser("~/.elan/bin/lean")
        if not os.path.exists(lean): return False, "Lean nicht installiert: Lemma ungeprüft"
        src = open("lean/ENRandom.lean").read()
        if "sorry" in src: return False, "Beweis enthält sorry"
        p = subprocess.run([lean, "lean/ENRandom.lean"], capture_output=True, text=True, timeout=300)
        ok = p.returncode == 0 and "sorryAx" not in p.stdout
        return ok, ("lean lean/ENRandom.lean: Exit 0, Axiome: " + p.stdout.strip().split("axioms:")[-1].strip()) if ok else p.stdout[-300:] + p.stderr[-300:]


def default_gates(policies, reproducible):
    g = [LeakGate(), TheoryGate("echt"), TheoryGate("negativkontrolle"), TheoryGate("negativkontrolle_je_seed")]
    if reproducible: g.append(ReproGate())
    if "gp_ei" in policies: g.append(BaselineGate("gp_ei", "random", "G3_gp_ei_schlaegt_zufall"))
    if "hybrid" in policies:
        g.append(BaselineGate("hybrid", "random", "G3_hybrid_schlaegt_zufall"))
        g.append(BaselineGate("hybrid", "gp_ei", "H1_hybrid_schlaegt_gp_ei"))
    for p in policies:
        if p != "random": g.append(NegControlGate(p))
    if "gp_ei" in policies: g.append(NegControlGate("gp_ei", "negativkontrolle"))   # prereg-Design, Seed 7
    if {"hybrid", "hybrid_neutral", "gp_ei"} <= set(policies): g.append(ContaminationGate())
    g += [BHGate(), LeanGate()]
    return g
