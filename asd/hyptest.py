"""Planen -> Ausführen -> Prüfen für die einzelnen KI-Hypothesen.

Eigenes, vorab festgelegtes Testexperiment: M zufällige Reaktionen über `Lab.run` (Seed 2000, wird in
`experiments` als policy='hypothesis_test' geloggt). Je Hypothese: Korrelation zwischen vorhergesagtem
Effekt h(x) und gemessener Ausbeute, einseitiger Permutationstest (h(x) sagt Ausbeute positiv voraus).
Der Status wird erst nach Benjamini-Hochberg über alle Tests gesetzt (in asd.gates).
Hybrid nutzt diese Messungen nicht (sonst bekäme es M Gratis-Experimente).
"""
import numpy as np
from .data import design_keys
from .hypotheses import prior_mean
from .lab import Lab

M = 200; SEED = 2000; B = 20000


def corr_perm(h, y, B=B, seed=0):
    h = (h - h.mean()) / (h.std() + 1e-12); yc = (y - y.mean()) / (y.std() + 1e-12)
    r = float(h @ yc / len(y)); rng = np.random.default_rng(seed)
    null = np.array([h @ yc[rng.permutation(len(y))] for _ in range(B)]) / len(y)
    return r, float((null >= r).mean()), float((null <= r).mean())


def run(ds, hyps_by_view):
    lab = Lab(ds.y, f"echt-hypothesis_test-{SEED}", SEED, "hypothesis_test", "echt")
    idx = np.random.default_rng(SEED).choice(ds.n, M, replace=False)
    y = np.array([lab.run(i) for i in idx])
    out = []
    for view, hyps in hyps_by_view.items():
        keys = design_keys(ds, view)[idx]
        for h in hyps:
            r, p_pos, p_neg = corr_perm(prior_mean([h], keys), y)
            out.append(dict(id=h.id, view=view, text=h.text, effect=h.effect, r=r, p=p_pos, p_gegenteil=p_neg))
    return out, lab.sink, lab.ctx["run_id"]
