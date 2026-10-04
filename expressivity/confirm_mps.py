"""Second runner for the preregistered H-EX1 grid on the MPS GPU (same protocol constants as confirm.py), processing cells in the
reverse of the CPU pool's order so that both finish earlier; a cell already written is skipped (decision EX21). Device is recorded.
  python -m expressivity.confirm_mps [archs comma-separated]"""
import json, os, sys, time
import torch
from .confirm import PROTOCOL, SEEDS, path
from .predict import TASKS
from . import train as TR
from .groups import get_group, alphabet

if __name__ == "__main__":
    archs = sys.argv[1].split(",") if len(sys.argv) > 1 else ["diag_pos", "diag_pm", "hh1"]
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    for arch in archs:
        for g, al in TASKS:
            p = path(arch, g, al)
            if os.path.exists(p): continue
            G = get_group(g); S = alphabet(G, al); t0 = time.time()
            r = TR.train_ensemble(arch, G, S, SEEDS, device=dev, **PROTOCOL)
            if os.path.exists(p): continue                      # the CPU pool finished it meanwhile: keep its result
            r.update(alphabet=al, random_targets=False, chance=1.0 / G.order, finished=time.strftime("%Y-%m-%d %H:%M:%S"), runner="confirm_mps")
            json.dump(r, open(p, "w"), indent=1)
            print(time.strftime("%H:%M:%S"), arch, g, al, f"{time.time() - t0:.0f}s", sum(x >= 0.9 for x in r["acc_T512_pos257-512"]), "of 20", flush=True)
