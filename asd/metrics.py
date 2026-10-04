"""Beschleunigung, automatisch aus dem Protokoll gemessen: Latenz Ergebnis -> Entscheidung, Zeit Frage -> Zertifikat,
Zerlegung jeder Runde (Agenten-/LLM-Zeit, Verifier-Rechenzeit, Experiment-Rechenzeit, Warten auf Menschen), Durchsatz und Kosten.

  python -m asd.metrics <domain> [--run runs/omnigent/<datum>]   -> results/metrics_<domain>.json, results/metrics_<domain>.png, Tabelle

Liest NUR die Protokolle eines aufgezeichneten Laufs (record.jsonl, Session-Exporte). Gibt es eine Hash-Kette (CHAIN.json), wird sie zuerst
geprüft; ist sie gebrochen, bricht das Skript ab. Manuelle Baseline: baselines/manual.jsonl (gemessen, nicht geschätzt)."""
import argparse, datetime, glob, json, os, re, sys
import numpy as np

from .chain import verify


def _utc(ts): return datetime.datetime.fromisoformat(ts).replace(tzinfo=datetime.timezone.utc).timestamp()


def _laden(run):
    rec = [json.loads(l) for l in open(os.path.join(run, "record.jsonl"))]
    for r in rec: r["t"] = _utc(r["ts"])
    sess = {}
    for f in sorted(glob.glob(os.path.join(run, "sessions", "*.jsonl"))):
        items = [json.loads(l) for l in open(f)]; meta = items[0] if items and items[0].get("record_type") == "session_meta" else {}
        sess[os.path.basename(f)[:-6]] = {"meta": meta, "items": [i for i in items if i.get("record_type") == "item"]}
    return rec, sess


def _shell_dauern(items):
    """Shell-Aufrufe einer Session als (Befehl, Intervall). Der Export trägt nur Abschluss-Zeitstempel: das Intervall reicht vom vorigen
    Abschluss bis zu diesem und enthält die LLM-Zeit vor dem Aufruf -> OBERE Schranke der Rechenzeit (untere für die Agentenzeit)."""
    out, seen, t_prev = [], set(), (items[0]["created_at"] if items else 0)
    for it in items:
        if it.get("type") == "function_call" and it.get("name") == "sys_os_shell":
            cmd = json.loads(it.get("arguments") or "{}").get("command", ""); key = (cmd, it["created_at"])
            if key in seen: continue
            seen.add(key); out.append((cmd, it["created_at"] - t_prev)); t_prev = it["created_at"]
        elif it.get("type") == "message": t_prev = it["created_at"]
    return out


def _art(cmd):
    if re.search(r"asd\.cli (pruefe|prüfe|redteam)\b", cmd): return "verifier"
    if re.search(r"asd\.cli experiment\b", cmd): return "experiment"
    if "asd.paper" in cmd: return "paper"
    return "werkzeug"


def _stat(x, B=5000, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0: return {"n": 0}
    rng = np.random.default_rng(seed); med = np.median(x[rng.integers(0, len(x), (B, len(x)))], 1)
    return {"n": int(len(x)), "median": float(np.median(x)), "min": float(x.min()), "max": float(x.max()),
            "ki95_median": [float(np.percentile(med, 2.5)), float(np.percentile(med, 97.5))]}


def messen(run):
    rec, sess = _laden(run)
    lead = next(v for k, v in sess.items() if k.startswith("lead__"))
    # --- menschliche Wartezeit aus Policy-ASK (Lead-Nachrichten des Systems) ---
    ask_von = ask_bis = None
    for it in lead["items"]:
        if it.get("type") == "message" and it.get("role") == "user":
            t = " ".join(x.get("text", "") for x in it.get("content", []) if isinstance(x, dict))
            if "awaiting human approval" in t and ask_von is None: ask_von = it["created_at"]
            if "approval has been resolved" in t: ask_bis = it["created_at"]
    mensch = (ask_bis - ask_von) if ask_von and ask_bis else 0.0
    # --- (a) Latenz Prüfer-Ergebnis -> nächste dokumentierte Entscheidung ---
    entscheidungen = sorted([r["t"] for r in rec if r["befehl"] in ("waehle", "wähle", "reopen", "folgefragen")] +
                            [it["created_at"] for it in lead["items"] if it.get("type") == "function_call" and it.get("name") == "sys_session_send"])
    ergebnisse = [r for r in rec if r["befehl"] == "pruefe"]
    lat = []
    for r in ergebnisse:
        nxt = next((t for t in entscheidungen if t >= r["t"]), None)
        if nxt is not None: lat.append({"ergebnis_ts": r["ts"], "claim": r["ausgabe_ids"].get("claim"), "bestanden": (r.get("ergebnis") or {}).get("bestanden"),
                                        "latenz_s": nxt - r["t"]})
    # --- (b) Frage -> zertifizierter Claim ---
    f2c = []
    for r in ergebnisse:
        e = r.get("ergebnis") or {}
        if not e.get("bestanden"): continue
        q = r["eingabe_ids"].get("frage")
        w = [x["t"] for x in rec if x["befehl"] in ("waehle", "wähle") and x["eingabe_ids"].get("frage") == q and x["t"] <= r["t"]]
        if w: f2c.append({"frage": q, "claim": e.get("claim_id"), "sekunden": r["t"] - min(w)})
    # --- (c) Zerlegung je Runde (Runde = Researcher-Session + Red-Team-Session ihres Claims) ---
    runden = []
    for k, v in sorted(((k, v) for k, v in sess.items() if k.startswith("researcher-")), key=lambda kv: kv[1]["items"][0]["created_at"]):
        its = v["items"]; t0, t1 = its[0]["created_at"], its[-1]["created_at"]
        d = {"verifier": 0.0, "experiment": 0.0, "werkzeug": 0.0, "paper": 0.0}
        for cmd, dt in _shell_dauern(its): d[_art(cmd)] += dt
        claim = next((r["ausgabe_ids"].get("claim") for r in ergebnisse if r["ausgabe_ids"].get("claim") and t0 <= r["t"] <= t1 + 2), None)
        rt = next((vv for kk, vv in sess.items() if kk.startswith("redteam-") and claim and claim.split("-")[-1] in kk), None)
        rt_s = 0.0
        if rt:
            for cmd, dt in _shell_dauern(rt["items"]): d[_art(cmd)] += dt
            rt_s = rt["items"][-1]["created_at"] - rt["items"][0]["created_at"]
        wand = (t1 - t0); agent = max(0.0, wand + rt_s - d["verifier"] - d["experiment"] - d["werkzeug"])
        runden.append({"runde": len(runden) + 1, "session": k, "claim": claim, "wanduhr_s": wand, "redteam_s": rt_s,
                       "agenten_llm_s": agent, "verifier_s": d["verifier"], "experiment_s": d["experiment"], "werkzeug_s": d["werkzeug"], "mensch_s": 0.0})
    # --- (d) Durchsatz und Kosten ---
    t_start, t_ende = lead["items"][0]["created_at"], lead["items"][-1]["created_at"]
    maschine_h = max(1e-9, (t_ende - t_start - mensch) / 3600)
    n_ok = sum(1 for r in ergebnisse if (r.get("ergebnis") or {}).get("bestanden")); n_ab = len(ergebnisse) - n_ok
    kosten = lead["meta"].get("total_cost_usd")
    res = {"lauf": run, "kette": verify(run)[1], "domain_projekt": rec[0].get("ergebnis") and None,
           "laufzeit_gesamt_s": t_ende - t_start, "mensch_warten_s": mensch, "maschinenzeit_h": maschine_h,
           "latenz_ergebnis_entscheidung": {"einzeln": lat, "alle": _stat([x["latenz_s"] for x in lat]),
                                             "ohne_kaltstart": _stat([x["latenz_s"] for x in lat[1:]]), "kaltstart_s": lat[0]["latenz_s"] if lat else None},
           "frage_zu_zertifikat": {"einzeln": f2c, "alle": _stat([x["sekunden"] for x in f2c]),
                                   "ohne_kaltstart": _stat([x["sekunden"] for x in f2c[1:]]), "kaltstart_s": f2c[0]["sekunden"] if f2c else None},
           "runden": runden,
           "zerlegung_summe_s": {k: float(sum(r[k] for r in runden)) for k in ("agenten_llm_s", "verifier_s", "experiment_s", "werkzeug_s")} | {"mensch_s": mensch},
           "durchsatz": {"zertifizierte_claims": n_ok, "abgelehnte_behauptungen": n_ab, "zertifiziert_pro_h": n_ok / maschine_h,
                         "abgelehnt_pro_h": n_ab / maschine_h, "kosten_usd_gesamt": kosten, "kosten_usd_pro_zertifikat": (kosten / n_ok) if kosten and n_ok else None},
           "hinweis": "Messung aus einem einzigen aufgezeichneten Lauf; Zeitstempel mit Sekundenauflösung; n jeweils angegeben; Kaltstart (erste Runde) getrennt. "
                      "Zerlegung: Verifier-/Experiment-Zeiten sind obere Schranken (Export kennt nur Abschluss-Zeitstempel), Agenten-/LLM-Zeit entsprechend untere Schranke."}
    return res


def baseline(path="baselines/manual.jsonl"):
    rows = [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []
    out = {}
    for r in rows: out.setdefault(r["schritt"], []).append(float(r["sekunden"]))
    return {k: {**_stat(v), "personen": len({r.get("person") for r in rows if r["schritt"] == k})} for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("domain"); ap.add_argument("--run", default="")
    a = ap.parse_args()
    run = a.run or sorted(d for d in glob.glob("runs/omnigent/*") if os.path.isdir(d) and json.load(open(os.path.join(d, "state.json"))).get("domain") == a.domain)[-1]
    ok, grund = verify(run)
    if ok is False: sys.exit(f"ABBRUCH: Hash-Kette des Laufs {run} gebrochen: {grund}")
    m = messen(run); m["domain"] = a.domain
    b = baseline(); m["manuelle_baseline"] = b
    lab_med = m["latenz_ergebnis_entscheidung"]["alle"].get("median")
    bl = b.get("ergebnis_zu_entscheidung")
    m["speedup_ergebnis_zu_entscheidung"] = ({"manuell_median_s": bl["median"], "labor_median_s": lab_med, "speedup": bl["median"] / lab_med,
                                               "einschraenkung": f"gemessen, n={bl['n']}, {bl['personen']} Person(en); ein Lauf; kein Vergleich mit einem echten Forschungslabor"}
                                              if bl and bl["n"] >= 3 and lab_med else {"status": "ausstehend: mindestens 3 Stoppuhr-Messungen in baselines/manual.jsonl nötig"})
    os.makedirs("results", exist_ok=True)
    json.dump(m, open(f"results/metrics_{a.domain}.json", "w"), indent=1, ensure_ascii=False, default=str)
    abbildung(m, f"results/metrics_{a.domain}.png"); open(f"results/metrics_{a.domain}.md", "w").write(tabelle(m)); print(tabelle(m))


def tabelle(m):
    L = m["latenz_ergebnis_entscheidung"]; F = m["frage_zu_zertifikat"]; D = m["durchsatz"]; Z = m["zerlegung_summe_s"]
    f = lambda s: f"{s['median']:.0f} s (range {s['min']:.0f}–{s['max']:.0f}, 95 % CI of median {s['ki95_median'][0]:.0f}–{s['ki95_median'][1]:.0f}, n = {s['n']})" if s.get("n") else "–"
    sp = m["speedup_ergebnis_zu_entscheidung"]
    rows = [("Verifier result → next documented decision", f(L["alle"])), ("  same, without cold start (round 1)", f(L["ohne_kaltstart"])),
            ("Question → certified claim", f(F["alle"])),
            ("Certified claims / rejected claims", f"{D['zertifizierte_claims']} / {D['abgelehnte_behauptungen']}"),
            ("Certified claims per machine hour", f"{D['zertifiziert_pro_h']:.1f}"),
            ("Cost per certified claim", f"{D['kosten_usd_pro_zertifikat']:.2f} USD" if D.get("kosten_usd_pro_zertifikat") else "–"),
            ("Time split over all rounds (agents·LLM ≥ / verifier ≤ / experiments ≤ / tooling ≤ / human wait)",
             f"{Z['agenten_llm_s']:.0f} / {Z['verifier_s']:.0f} / {Z['experiment_s']:.0f} / {Z['werkzeug_s']:.0f} / {Z['mensch_s']:.0f} s"),
            ("Manual baseline (stopwatch, same step)", f"{sp['manuell_median_s']:.0f} s → speedup {sp['speedup']:.1f}× ({sp['einschraenkung']})" if "speedup" in sp else sp["status"])]
    return "| Measure (one recorded Omnigent run) | Value |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in rows) + "\n"


def abbildung(m, fn):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    L = m["latenz_ergebnis_entscheidung"]["einzeln"]; R = m["runden"]
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.2))
    ax[0].bar(range(1, len(L) + 1), [x["latenz_s"] for x in L], color=["C2" if x["bestanden"] else "C3" for x in L])
    bl = m["manuelle_baseline"].get("ergebnis_zu_entscheidung")
    if bl and bl.get("n"): ax[0].axhspan(bl["min"], bl["max"], color="grey", alpha=0.25, label=f"manual (n={bl['n']})"); ax[0].legend(fontsize=7)
    ax[0].set_xlabel("verifier result #"); ax[0].set_ylabel("seconds to next decision"); ax[0].set_title("Result → decision latency", fontsize=9)
    keys = [("agenten_llm_s", "agents/LLM"), ("verifier_s", "verifier"), ("experiment_s", "experiments"), ("werkzeug_s", "tooling")]
    bottom = np.zeros(len(R))
    for k, lab in keys:
        v = np.array([r[k] for r in R]); ax[1].bar(range(1, len(R) + 1), v, bottom=bottom, label=lab); bottom += v
    ax[1].set_xlabel("round"); ax[1].set_ylabel("seconds"); ax[1].set_title("Where the time goes (per round)", fontsize=9); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(fn, dpi=150)


if __name__ == "__main__":
    main()
