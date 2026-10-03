"""Führt Policies über feste Seeds aus. Der Evaluator (nicht die Policy) kennt die Treffer-Maske."""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import warnings
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from .data import load, hits, SEEDS
from .lab import Lab
from .policies import make_policy

NEG_SEED = 7     # Negativkontrolle: vertauschte Ausbeuten (prereg)


def datasets(ds, seed=None):
    """echt | negativkontrolle (eine feste Vertauschung, Seed 7, prereg) |
    negativkontrolle_je_seed (eigene Vertauschung je Seed; nötig für Policies mit festem Vorwissen,
    sonst sind die 20 Seeds keine unabhängigen Wiederholungen, siehe prereg.md, Nachtrag)."""
    d = {"echt": ds.y, "negativkontrolle": np.random.default_rng(NEG_SEED).permutation(ds.y)}
    if seed is not None:
        d["negativkontrolle_je_seed"] = np.random.default_rng([NEG_SEED, seed]).permutation(ds.y)
    return d


def run_one(args):
    warnings.filterwarnings("ignore")              # sklearn-ConvergenceWarnings beim GP-Refit
    policy, dataset, seed, budget, hyps = args
    ds = load(); y = datasets(ds, seed)[dataset]; hit, k = hits(y)
    run_id = f"{dataset}-{policy}-{seed}"
    lab = Lab(y, run_id, seed, policy, dataset); pol = make_policy(policy, ds, hyps)
    rng = np.random.default_rng(seed); history = []; N = budget + 1
    for t in range(1, budget + 1):
        i = pol.propose(history, rng)
        assert i not in {j for j, _ in history}, "Policy schlägt ein bereits gemessenes Experiment vor"
        history.append((i, lab.run(i)))
        if hit[i]: N = t; break
    leak_ok = len(lab.log) == min(N, budget)          # Leck-Prüfung: N Aufrufe = N Experimente
    return dict(run_id=run_id, policy=policy, dataset=dataset, seed=seed, N=N, k=k, leak_ok=leak_ok,
                alpha=[float(a) for a in getattr(pol, "alpha_trace", [])]), lab.sink


def run_all(policies, seeds=SEEDS, budget=400, hyps=None, workers=None, dsets=("echt", "negativkontrolle", "negativkontrolle_je_seed")):
    jobs = [(p, d, s, budget, hyps) for d in dsets for p in policies for s in seeds]
    with ProcessPoolExecutor(workers or os.cpu_count()) as ex:
        out = list(ex.map(run_one, jobs))
    runs = [r for r, _ in out]; rows = [row for _, sink in out for row in sink]
    return runs, rows
