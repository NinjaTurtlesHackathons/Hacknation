"""Preregistered confirmatory grid (prereg.md, H-EX1): 63 cells x 20 seeds plus 3 negative-control cells.
  python -m expressivity.confirm [--workers 14]      -> expressivity/results/confirmatory/<arch>__<group>__<alphabet>[__random].json
Already finished cells are skipped (resumable). Protocol constants are fixed here and in prereg.md."""
import argparse, json, os, time
from multiprocessing import Pool

from .predict import TASKS, ARCHS

OUT = "expressivity/results/confirmatory"
SEEDS = list(range(1000, 1020))
PROTOCOL = dict(steps=3000, T=64, B=64, lr=5e-3, beta_bias=2.0, curriculum=True, beta_mode="clamp2", T_final=128,
                evals=((64, (1, 64)), (512, (257, 512)), (1024, (897, 1024))))
NEG = [("hh4", "S5", "all"), ("lstm", "S5", "all"), ("hh2", "A5", "all")]


def path(arch, g, a, rnd=False):
    return f"{OUT}/{arch}__{g.replace('^', 'p')}__{a}{'__random' if rnd else ''}.json"


def job(args):
    arch, g, a, rnd = args
    import torch, numpy as np
    torch.set_num_threads(1)
    from . import train as TR
    from .groups import get_group, alphabet
    if rnd:
        orig = TR.make_batch
        def mb(rng, L, e, B, T):
            tok, _ = orig(rng, L, e, B, T); return tok, rng.integers(0, L.shape[1], size=(B, T))
        TR.make_batch = mb
    G = get_group(g); S = alphabet(G, a); t0 = time.time()
    r = TR.train_ensemble(arch, G, S, SEEDS, **PROTOCOL)
    r.update(alphabet=a, random_targets=rnd, chance=1.0 / G.order, finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    json.dump(r, open(path(arch, g, a, rnd), "w"), indent=1)
    return f"{arch} {g} {a} {'random' if rnd else ''} done in {time.time() - t0:.0f}s"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=14); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    jobs = [(arch, g, al, False) for g, al in TASKS for arch in ARCHS] + [(arch, g, al, True) for arch, g, al in NEG]
    cost = {"hh4": 8, "hh3": 6, "hh2": 4, "lstm": 3, "hh1": 2, "diag_pm": 2, "diag_pos": 2}
    jobs = [j for j in jobs if not os.path.exists(path(j[0], j[1], j[2], j[3]))]
    jobs.sort(key=lambda j: -cost[j[0]])                       # longest first
    print(f"{len(jobs)} jobs", flush=True)
    with Pool(a.workers) as pool:
        for msg in pool.imap_unordered(job, jobs):
            print(time.strftime("%H:%M:%S"), msg, flush=True)


if __name__ == "__main__":
    main()
