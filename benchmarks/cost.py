"""Kosten je Bedingung aus dem LLM-Cache (B, BK) bzw. aus den Ergebnisdateien (A2)."""
import glob, json, os, sys
import numpy as np
KEY = {q["id"]: q["frage"] for q in json.load(open("benchmarks/suleman2026.json"))["fragen"]}
cache = [json.load(open(f)) for f in glob.glob("cache/llm/*.json")]


def cost_for(cond):
    out = {}
    for f in glob.glob(f"results/benchmark/{cond}/*.json"):
        r = json.load(open(f)); q, s = r["frage"], r["salt"]
        if cond == "A2": out[(q, s)] = r.get("kosten_usd") or 0; continue
        pre = {"A1": f"A1-{s}", "B": f"{s}-", "BK": f"K{s}-"}[cond]
        out[(q, s)] = sum(c.get("cost_usd", 0) for c in cache if str(c.get("salt", "")).startswith(pre) and f"FRAGE: {KEY[q]}" in c["prompt"])
    return out


if __name__ == "__main__":
    for c in sys.argv[1:] or ["A1", "A2", "B", "BK"]:
        if not os.path.isdir(f"results/benchmark/{c}"): continue
        v = cost_for(c); sek = [json.load(open(f)).get("sek", 0) for f in glob.glob(f"results/benchmark/{c}/*.json")]
        print(f"{c}: {len(v)} Läufe, Kosten gesamt {sum(v.values()):.2f} USD, je Frage {np.mean(list(v.values())):.4f} USD, Zeit je Frage Median {np.median(sek):.0f} s")
