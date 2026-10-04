"""Preregistered addendum H-EX2 (prereg.md, 2026-10-04 05:00): hh1/hh2/hh3 on S4/tn and A5/c3c5, 20 seeds, protocol of confirm.py,
run on the MPS GPU.  python -m expressivity.confirm_ex2  -> expressivity/results/confirmatory/<arch>__<group>__<alphabet>.json"""
import json, os, sys, time
import torch
from .confirm import PROTOCOL, SEEDS, path, OUT
from . import train as TR
from .groups import get_group, alphabet

CELLS = [(a, g, al) for g, al in (("A5", "c3c5"), ("S4", "tn")) for a in ("hh2", "hh1", "hh3")]

if __name__ == "__main__":
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    sel = CELLS if len(sys.argv) < 2 else [c for c in CELLS if c[0] in sys.argv[1].split(",")]
    for arch, g, al in sel:
        p = path(arch, g, al)
        if os.path.exists(p): continue
        G = get_group(g); S = alphabet(G, al); t0 = time.time()
        r = TR.train_ensemble(arch, G, S, SEEDS, device=dev, **PROTOCOL)
        r.update(alphabet=al, random_targets=False, chance=1.0 / G.order, finished=time.strftime("%Y-%m-%d %H:%M:%S"), addendum="H-EX2")
        json.dump(r, open(p, "w"), indent=1)
        print(time.strftime("%H:%M:%S"), arch, g, al, f"{time.time() - t0:.0f}s", sum(x >= 0.9 for x in r["acc_T512_pos257-512"]), "of 20", flush=True)
