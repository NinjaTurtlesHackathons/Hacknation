"""Gemessene Beschleunigung (präregistriert als H7 in prereg.md): Replay des bekannten Resultats y_inf ≈ 1,249621 (Domäne lattice).

  python -m benchmarks.replay_lattice                       # 10 Seeds, alle Bedingungen, danach Auswertung
  python -m benchmarks.replay_lattice --seeds 2             # Probelauf
  python -m benchmarks.replay_lattice --nur-auswertung      # nur results/replay_lattice.json + Abbildung neu

Bedingungen LAB | OHNE_FEEDBACK | ZUFALL. Metrik N = Verifier-Aufrufe bis zum ersten Treffer (Budget+1 bei Scheitern).
Treffer = vom unveränderten Verifier bestandene Behauptung grenzwert/y_inf aus dem Behauptungspfad (Code, nicht LLM)."""
import argparse, json, os, random, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

BED = ("LAB", "OHNE_FEEDBACK", "ZUFALL", "HEURISTIK")
SEEDS = list(range(1000, 1025))
BUDGET = 30
ZIEL = 1.249621
OUT = os.environ.get("REPLAY_OUT", "results/replay_lattice")
POOL = json.load(open("benchmarks/replay_pool.json"))


class BudgetErschoepft(BaseException): pass        # BaseException: wird von keiner Fehlerbehandlung im Labor geschluckt
class Treffer(BaseException): pass


def ist_treffer(p, ok):
    return bool(ok) and isinstance(p, dict) and p.get("typ") == "grenzwert" and p.get("groesse") == "y_inf"


class Zaehler:
    """Umhüllt Domain.check: zählt jeden Aufruf, erkennt Treffer per Code, stoppt beim Budget. Der Verifier selbst bleibt unverändert."""
    def __init__(self, D, budget):
        self.D, self.budget, self.n, self.abgelehnt, self.modus, self.n_treffer, self.treffer_claim = D, budget, 0, 0, "claim", None, None
        self.orig = D.check; D.check = self.check
    def check(self, p):
        if self.n >= self.budget: raise BudgetErschoepft()
        self.n += 1; r = self.orig(p); ok = bool(r[0])
        if self.modus == "claim":
            if not ok: self.abgelehnt += 1
            if ist_treffer(p, ok): self.n_treffer = self.n; self.treffer_claim = p; raise Treffer()
        return r


# ---------------------------------------------------------------------------------------------------------------
def kanarien(D, extra=""):
    """Leckschutz-Test: der gesamte Agenten-Kontext darf das Zielresultat nicht enthalten. Gibt Liste der Funde zurück."""
    from asd.discovery import CLAIM_DOC
    from asd import planner
    ctx = "\n".join([D.kontext, D.primitive_doc, CLAIM_DOC, json.dumps(POOL, ensure_ascii=False), extra,
                     json.dumps(planner.options(D, {"id": "F1", "frage": POOL["auftrag"]}, {"fragen": [], "runden": [], "claims": [], "widerlegt": []}), ensure_ascii=False)])
    funde = [m for m in ("1.2496", "1,2496", "sqrt(17)", "√17", "1.4317", "1,4317") if m in ctx]
    for m in re.finditer(r"17", ctx):
        umg = ctx[max(0, m.start() - 40): m.end() + 40].lower()
        if any(k in umg for k in ("seitenverh", "aspect", "y_inf")): funde.append(f"'17' nahe Seitenverhältnis: {umg!r}")
    return funde


def lauf_lab(D, z, seed, log):
    from asd import lab_loop, novelty, discovery, planner
    novelty.check_claim = lambda *a, **k: {"status": "nicht_geprueft", "grund": "Benchmark: Neuheitsprüfung aus"}
    rt_orig = lab_loop.red_team
    def red_team(*a, **k):
        z.modus = "redteam"
        try: return rt_orig(*a, **k)
        finally: z.modus = "claim"
    lab_loop.red_team = red_team
    sc_orig = lab_loop.solve_cascade
    def solve_cascade(kontext, frage, **k):               # Code-Planer: beste Option als Vorgehen an die Frage hängen
        q = next((x for x in P.s["fragen"] if x["frage"] == frage), {"id": "?", "frage": frage})
        o = planner.options(D, q, P.s)[0]; P.s.setdefault("entscheidungen", []).append({"frage": q["id"], "gewaehlt": o["id"], "art": o["art"]})
        return sc_orig(kontext, frage + f"\n\nVorgehen ({o['art']}): {o['vorgehen']}", **k)
    lab_loop.solve_cascade = solve_cascade
    name = f"_replay_LAB_s{seed}"; shutil.rmtree(f"projects/{name}", ignore_errors=True)
    P = lab_loop.Project(name); D.projekt = name
    P.s["fragen"].append({"id": "F1", "frage": POOL["auftrag"], "status": "offen", "faden_id": "F1"}); P.save()
    a = SimpleNamespace(fragen="", gezielt=False)
    for runde in range(1, 3 * BUDGET):
        weiter = lab_loop.runde_ausfuehren(P, D, a, runde, log); P.save()
        if not weiter and not [q for q in P.s["fragen"] if q["status"] == "offen"]: break


def lauf_einzelversuche(D, z, seed, bed, log):
    from asd.discovery import forscher, Lab, KASKADE
    from asd.llm import LLMError
    rng = random.Random(seed)
    for k in range(3 * BUDGET):                          # Obergrenze gegen Endlosschleifen bei lauter Formatfehlern
        if bed == "OHNE_FEEDBACK": frage, (strat, model) = POOL["auftrag"], KASKADE[k % len(KASKADE)]
        elif bed == "HEURISTIK":                                   # starke naive Baseline: einfachste (kürzeste) Frage zuerst, feste Reihenfolge
            pool = sorted(POOL["pool"], key=len); frage, (strat, model) = pool[k % len(pool)], KASKADE[k % len(KASKADE)]
        else: frage, (strat, model) = rng.choice(POOL["pool"]), rng.choice(KASKADE)
        try: tr = forscher(D.kontext, frage, strat, Lab(D), f"{bed}-{k}", model=model)
        except (LLMError, json.JSONDecodeError, KeyError, TypeError) as e: log(f"Versuch {k}: Fehler {str(e)[:80]}"); continue
        a = tr.get("final") or {}
        ps = [p for p in (a.get("pruefungen") or ([a["pruefung"]] if isinstance(a.get("pruefung"), dict) else [])) if isinstance(p, dict)]
        for p in ps: D.check(p)
        log(f"Versuch {k} ({strat}/{model}): {len(ps)} Prüfung(en), Verifier-Aufrufe bisher {z.n}")


def einzel(bed, seed, budget):
    """Ein Lauf (Bedingung, Seed) in eigenem Prozess; Ergebnis als JSON nach results/replay_lattice/."""
    os.environ["ASD_SEED_SALT"] = f"replay-{bed}-{seed}-"
    from asd.domains.base import get_domain
    D = get_domain("lattice"); f = kanarien(D)
    if f: raise SystemExit(f"KANARIEN-TEST ROT, Abbruch: {f}")
    z = Zaehler(D, budget); t0 = time.time(); ereignis = "budget"
    os.makedirs(OUT, exist_ok=True); logf = open(f"{OUT}/{bed}_{seed}.log", "w")
    log = lambda m: (logf.write(f"[{time.time() - t0:7.1f}s] {m}\n"), logf.flush())
    try:
        if bed == "LAB": lauf_lab(D, z, seed, log)
        else: lauf_einzelversuche(D, z, seed, bed, log)
        ereignis = "ohne_treffer_beendet"
    except Treffer: ereignis = "treffer"
    except BudgetErschoepft: ereignis = "budget"
    N = z.n_treffer if z.n_treffer else budget + 1
    from asd.llm import COST_LOG
    r = {"bedingung": bed, "seed": seed, "N": N, "treffer": bool(z.n_treffer), "verifier_aufrufe": z.n, "abgelehnt": z.abgelehnt,
         "sek": round(time.time() - t0, 1), "ereignis": ereignis, "budget": budget, "treffer_claim": z.treffer_claim,
         "kosten_usd_neu": round(sum(COST_LOG), 4), "llm_aufrufe_neu": len(COST_LOG)}
    json.dump(r, open(f"{OUT}/{bed}_{seed}.json", "w"), indent=1); log(json.dumps(r)); print(json.dumps(r))


# ---------------------------------------------------------------------------------------------------------------
def clopper_pearson(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1); hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return [float(lo), float(hi)]


def auswertung(seeds, budget):
    import numpy as np
    from asd.stats import perm_test, ratio_ci, bh
    R = {b: {} for b in BED}
    for b in BED:
        for s in seeds:
            fn = f"{OUT}/{b}_{s}.json"
            if os.path.exists(fn): R[b][s] = json.load(open(fn))
    gem = [s for s in seeds if all(s in R[b] for b in ("LAB", "OHNE_FEEDBACK", "ZUFALL"))]
    res = {"praeregistrierung": "prereg.md, Abschnitt H7", "budget": budget, "seeds": gem, "bedingungen": {}, "tests": {}}
    for b in BED:
        rows = [R[b][s] for s in gem if s in R[b]]; N = [r["N"] for r in rows]; k = sum(r["treffer"] for r in rows)
        res["bedingungen"][b] = {"N": N, "mittel_N": float(np.mean(N)) if N else None, "median_N": float(np.median(N)) if N else None,
                                 "treffer": k, "trefferquote": k / len(rows) if rows else None, "treffer_ki95": clopper_pearson(k, len(rows)) if rows else None,
                                 "mittel_sek": float(np.mean([r["sek"] for r in rows])) if rows else None,
                                 "mittel_abgelehnt": float(np.mean([r["abgelehnt"] for r in rows])) if rows else None}
    for b in BED:
        if not res["bedingungen"][b]["N"]: continue
        N = res["bedingungen"][b]["N"]; res["bedingungen"][b]["recall_bei_budget"] = {str(B): sum(1 for n in N if n <= B) / len(N) for B in (5, 10, 20, 30)}
        rows = [R[b][s] for s in gem if s in R[b]]; k = sum(r_["treffer"] for r_ in rows)
        kost = [r_.get("kosten_usd_neu") for r_ in rows if r_.get("kosten_usd_neu") is not None]
        res["bedingungen"][b]["kosten_usd_neu_gesamt"] = round(sum(kost), 3) if kost else None
        res["bedingungen"][b]["kosten_usd_pro_treffer"] = round(sum(kost) / k, 3) if kost and k else None
    res["bedingungen"]["ORAKEL"] = {"N": [1] * len(gem), "mittel_N": 1.0, "median_N": 1.0, "analytisch": True,
                                    "erklaerung": "kennt die Antwort und reicht die Treffer-Behauptung direkt ein (Obergrenze, nicht gerechnet)"}
    if len(gem) >= 2:
        lab = [R["LAB"][s]["N"] for s in gem]; ps = []
        for h, b in (("H8a", "ZUFALL"), ("H8b", "HEURISTIK"), ("H8c", "OHNE_FEEDBACK")):
            ss = [s for s in gem if s in R[b]]
            if len(ss) < 2: continue
            cmp = [R[b][s]["N"] for s in ss]; lb = [R["LAB"][s]["N"] for s in ss]; sp, ki = ratio_ci(cmp, lb); p = perm_test(lb, cmp)
            res["tests"][h] = {"vergleich": b, "speedup": sp, "ki95": ki, "p": p, "n_seeds": len(ss)}; ps.append(p)
        if ps:
            rej, adj = bh(ps, q=0.1)
            for (h, t), pa, rj in zip(res["tests"].items(), adj, rej):
                t["p_bh"] = float(pa); t["erfolg"] = bool(pa < 0.1 and t["ki95"][0] > 1)
        s10 = [s for s in gem if s < 1010]                         # H7 (präregistriert, 10 Seeds) unverändert mitführen
        if len(s10) >= 2:
            lab10 = [R["LAB"][s]["N"] for s in s10]; res["H7_10_seeds"] = {}
            for h, b in (("H7a", "ZUFALL"), ("H7b", "OHNE_FEEDBACK")):
                cmp = [R[b][s]["N"] for s in s10]; sp, ki = ratio_ci(cmp, lab10); res["H7_10_seeds"][h] = {"vergleich": b, "speedup": sp, "ki95": ki, "p": perm_test(lab10, cmp)}
    json.dump(res, open("results/replay_lattice.json", "w"), indent=1, ensure_ascii=False)
    abbildung(res); return res


def abbildung(res):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
    try:
        from asd.figstyle import apply_style; apply_style()
    except Exception: pass
    fig, ax = plt.subplots(figsize=(6.2, 3.6)); rng = np.random.default_rng(0)
    for i, b in enumerate(BED):
        N = res["bedingungen"][b]["N"]
        if not N or res["bedingungen"][b].get("analytisch"): continue
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(N)), N, s=22, alpha=0.75, color=f"C{i}")
        ax.hlines(np.median(N), i - 0.25, i + 0.25, color="k", lw=2)
    ax.axhline(res["budget"] + 1, ls=":", color="grey", lw=1); ax.text(len(BED) - 0.55, res["budget"] + 1, "failed (budget+1)", fontsize=7, va="bottom", ha="right", color="grey")
    ax.set_xticks(range(len(BED))); ax.set_xticklabels(["LAB", "NO FEEDBACK", "RANDOM", "SIMPLEST\nFIRST"])
    ax.axhline(1, ls="--", color="C4", lw=1); ax.text(len(BED) - 0.6, 1.3, "oracle (N = 1)", fontsize=7, color="C4", ha="right")
    ax.set_ylabel("verifier calls to first hit (N)"); ax.set_title(f"Replay y_inf (lattice), {len(res['seeds'])} seeds; bar = median", fontsize=9)
    fig.tight_layout(); fig.savefig("results/replay_lattice.png", dpi=160); fig.savefig("results/replay_lattice.pdf")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=10); ap.add_argument("--bedingungen", default=",".join(BED)); ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--parallel", type=int, default=4); ap.add_argument("--neu", action="store_true", help="vorhandene Einzelergebnisse ignorieren")
    ap.add_argument("--nur-auswertung", action="store_true"); ap.add_argument("--einzel", nargs=2, metavar=("BEDINGUNG", "SEED"))
    a = ap.parse_args(); seeds = SEEDS[:a.seeds]
    if a.einzel: return einzel(a.einzel[0], int(a.einzel[1]), a.budget)
    from asd.domains.base import get_domain
    f = kanarien(get_domain("lattice")); print("Kanarien-Test:", "GRÜN" if not f else f"ROT {f}")
    if f: raise SystemExit(1)
    if not a.nur_auswertung:
        jobs = [(b, s) for s in seeds for b in a.bedingungen.split(",") if a.neu or not os.path.exists(f"{OUT}/{b}_{s}.json")]
        def job(bs):
            p = subprocess.run([sys.executable, "-m", "benchmarks.replay_lattice", "--einzel", bs[0], str(bs[1]), "--budget", str(a.budget)], capture_output=True, text=True)
            print(f"{bs[0]:14s} {bs[1]}: " + (p.stdout.strip().splitlines()[-1] if p.returncode == 0 and p.stdout.strip() else f"FEHLER {p.stderr[-300:]}"), flush=True)
        with ThreadPoolExecutor(a.parallel) as ex: list(ex.map(job, jobs))
    res = auswertung(seeds, a.budget)
    print(json.dumps({b: {k: v for k, v in r.items() if k != "N"} for b, r in res["bedingungen"].items()}, indent=1, ensure_ascii=False))
    print(json.dumps(res["tests"], indent=1))


if __name__ == "__main__":
    main()
