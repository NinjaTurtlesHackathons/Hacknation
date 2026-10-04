"""Bitgenaues Replay: jeder Benchmark-Lauf wird im reinen Cache-Modus (ASD_LLM=replay, keine neuen LLM-Aufrufe) wiederholt.
Gleiche Eingaben -> gleiche Entscheidungen -> gleiches N. Ergebnis: results/replay_determinism.json
  python benchmarks/replay_determinism.py [--bedingungen LAB,...] [--parallel 3]"""
import argparse, glob, json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser(); ap.add_argument("--bedingungen", default="LAB,OHNE_FEEDBACK,ZUFALL,HEURISTIK"); ap.add_argument("--parallel", type=int, default=3)
a = ap.parse_args(); tmp = tempfile.mkdtemp(prefix="replay-det-")
jobs = [json.load(open(f)) for f in sorted(glob.glob("results/replay_lattice/*.json")) if json.load(open(f))["bedingung"] in a.bedingungen.split(",")]
def lauf(r):
    env = dict(os.environ, ASD_LLM="replay", REPLAY_OUT=tmp)
    p = subprocess.run([sys.executable, "-m", "benchmarks.replay_lattice", "--einzel", r["bedingung"], str(r["seed"]), "--budget", str(r["budget"])], capture_output=True, text=True, env=env)
    fn = f"{tmp}/{r['bedingung']}_{r['seed']}.json"
    if not os.path.exists(fn): return {"lauf": f"{r['bedingung']}_{r['seed']}", "reproduziert": False, "grund": (p.stderr or p.stdout)[-160:]}
    n = json.load(open(fn))
    return {"lauf": f"{r['bedingung']}_{r['seed']}", "N_original": r["N"], "N_replay": n["N"], "reproduziert": n["N"] == r["N"] and n["treffer"] == r["treffer"]}
with ThreadPoolExecutor(a.parallel) as ex: res = list(ex.map(lauf, jobs))
out = {"laeufe": len(res), "reproduziert": sum(r["reproduziert"] for r in res), "anteil": (sum(r["reproduziert"] for r in res) / len(res)) if res else None, "details": res}
json.dump(out, open("results/replay_determinism.json", "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "details"}))
