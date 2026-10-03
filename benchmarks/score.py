"""Bewertung H3 gegen den Antwortschlüssel (Code, nicht LLM). Schreibt results/benchmark/score.json und gibt eine Tabelle aus."""
import glob, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from asd.stats import perm_test, bh

KEY = {q["id"]: q for q in json.load(open("benchmarks/suleman2026.json"))["fragen"]}
SYN = {"hexagonal": ["hexagonal", "hex", "dreieck", "triangular", "rho"], "quadratisch": ["quadrat", "square"],
       "rechteckig": ["rechteck", "rectang"], "bcc": ["bcc", "kubisch-raumzentriert", "raumzentriert", "body-centred", "body-centered"],
       "fcc": ["fcc", "flächenzentriert", "face-centred", "face-centered"], "unstetig": ["unstetig", "diskontinuierlich", "discontinuous", "sprung", "erster ordnung"],
       "stetig": ["stetig", "kontinuierlich", "continuous"], "i": ["tau = i", "tau=i", "quadrat", "square", "punkt i", "bei i", "\"i\"", " i "]}


def category(text, wanted):
    t = " " + str(text).lower().replace("τ", "tau") + " "
    if wanted == "i": t = t.replace("tau = i", " i ").replace("τ=i", " i ")
    hits = {k for k, ws in SYN.items() if any(w in t for w in ws)}
    if wanted == "unstetig": return "unstetig" in hits
    if wanted == "i": return ("i" in hits or t.strip() in ("i",)) and "rho" not in t and "hex" not in t
    others = {"hexagonal", "quadratisch", "rechteckig", "bcc", "fcc"} - {wanted}
    return wanted in hits and not (hits & others)


def grade(qid, ans):
    q = KEY[qid]; a = ans or {}; text = str(a.get("antwort", "")).lower()
    if not text or "unbekannt" in text or "unknown" in text:
        if q["typ"] != "zahl" or a.get("zahl") is None: return "unbekannt"
    num = a.get("zahl")
    try: num = float(num) if num is not None else None
    except (TypeError, ValueError): num = None
    if num is None and q["typ"] in ("zahl", "kategorie+zahl"):
        m = re.search(r"-?\d+\.\d+", text.replace(",", ".")); num = float(m.group(0)) if m else None
    if q["typ"] == "kategorie": return "richtig" if category(text, q["antwort"]) else "falsch"
    if q["typ"] == "zahl": return "richtig" if num is not None and abs(num - q["zahl"]) <= q["toleranz"] else ("unbekannt" if num is None else "falsch")
    ok_cat = category(text, q["antwort"]); ok_num = num is not None and abs(num - q["zahl"]) <= q["toleranz"]
    return "richtig" if ok_cat and ok_num else "falsch"


def load(cond):
    out = {}
    for f in glob.glob(f"results/benchmark/{cond}/*.json"):
        r = json.load(open(f)); out.setdefault(r["frage"], []).append(grade(r["frage"], r["antwort"]))
    return out


if __name__ == "__main__":
    conds = [c for c in ("A1", "A2", "B") if os.path.isdir(f"results/benchmark/{c}")]
    S = {c: load(c) for c in conds}; qids = sorted(KEY, key=lambda s: int(s[1:]))
    acc = {c: np.array([np.mean([g == "richtig" for g in S[c].get(q, [])]) if S[c].get(q) else np.nan for q in qids]) for c in conds}
    wrong = {c: np.array([np.mean([g == "falsch" for g in S[c].get(q, [])]) if S[c].get(q) else np.nan for q in qids]) for c in conds}
    print("Frage  " + "  ".join(f"{c:>18}" for c in conds))
    for i, q in enumerate(qids): print(f"{q:5}  " + "  ".join(f"{' '.join(g[0].upper() for g in S[c].get(q, [])):>18}" for c in conds))
    res = {"pro_frage": {c: S[c] for c in conds}}
    for c in conds: print(f"{c}: richtig {np.nanmean(acc[c]):.1%}, falsch {np.nanmean(wrong[c]):.1%}, Läufe {sum(len(v) for v in S[c].values())}")
    tests = {}
    if "B" in conds:
        for c in ("A1", "A2"):
            if c not in conds: continue
            m = ~np.isnan(acc["B"]) & ~np.isnan(acc[c])
            tests[f"H3_treffer_B_vs_{c}"] = perm_test(-acc["B"][m], -acc[c][m])      # a < b  <=> B hat mehr Treffer
            tests[f"H3_falsch_B_vs_{c}"] = perm_test(wrong["B"][m], wrong[c][m])
        if tests:
            rej, adj = bh(list(tests.values()), 0.1)
            for (k, p), a_, r_ in zip(tests.items(), adj, rej): print(f"{k}: p = {p:.4f}, p_BH = {a_:.4f}, signifikant: {bool(r_)}")
            res["tests"] = {k: {"p": p, "p_bh": float(a_)} for (k, p), a_ in zip(tests.items(), adj)}
    res["summary"] = {c: {"richtig": float(np.nanmean(acc[c])), "falsch": float(np.nanmean(wrong[c]))} for c in conds}
    json.dump(res, open("results/benchmark/score.json", "w"), ensure_ascii=False, indent=1)
