"""Alle Kennzahlen eingefroren: results/FROZEN.json (+ results/trust.json). Jede Zahl in den Abgabetexten muss wörtlich hier stehen.

  python -m asd.freeze

Quellen (nur Dateien, keine handgeschriebenen Zahlen): results/metrics_proofreading.json, results/replay_lattice.json,
results/benchmark/score.json (Vertrauens-Benchmark H3), results/blind_claims.json, projects/proofreading/verifier_redteam.json,
Selbsttests der Domänen, projects/omni_proofreading/klassifikation.json und state.json, Hash-Ketten der Läufe."""
import collections, glob, json, os, subprocess, time


def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1)); hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def r(x, n=1): return None if x is None else (int(round(float(x))) if n == 0 else round(float(x), n))


def trust():
    d = json.load(open("results/benchmark/score.json")); namen = {"A1": "Claude alone", "A2": "Claude with Python", "B": "Lab (4 researchers + code verifier)", "BK": "Lab, cascade (Haiku first)"}
    out = {"quelle": "results/benchmark/score.json (preregistered H3: 12 questions from Suleman 2026, 3 runs each)", "bedingungen": {}}
    for b, q in d["pro_frage"].items():
        c = collections.Counter(x for v in q.values() for x in v); n = sum(c.values())
        out["bedingungen"][b] = {"name": namen.get(b, b), "n": n, "richtig": c["richtig"], "falsch": c["falsch"], "unbekannt": c["unbekannt"],
                                 "anteil_richtig_pct": r(100 * c["richtig"] / n), "anteil_falsch_pct": r(100 * c["falsch"] / n),
                                 "falsch_ki95_pct": [r(100 * x) for x in cp(c["falsch"], n)], "richtig_ki95_pct": [r(100 * x) for x in cp(c["richtig"], n)],
                                 "falsch_pro_richtig": r(c["falsch"] / c["richtig"], 2) if c["richtig"] else None}
    bl = [json.loads(l) for l in open("baselines/manual.jsonl") if l.strip()] if os.path.exists("baselines/manual.jsonl") else []
    pr = [x["sekunden"] for x in bl if x.get("schritt") == "behauptung_pruefen"]
    out["manuelle_nachpruefzeit"] = ({"median_s": sorted(pr)[len(pr) // 2], "n": len(pr),
                                      "erwartete_nachpruefzeit_pro_akzeptiertem_resultat_s": {b: r(v["falsch_pro_richtig"] * sorted(pr)[len(pr) // 2]) for b, v in out["bedingungen"].items() if v["falsch_pro_richtig"] is not None}}
                                     if len(pr) >= 3 else {"status": "pending: at least 3 stopwatch measurements of step 'behauptung_pruefen' in baselines/manual.jsonl"})
    json.dump(out, open("results/trust.json", "w"), indent=1, ensure_ascii=False); return out


def main():
    from .domains.base import get_domain
    from .chain import verify
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    m = json.load(open("results/metrics_proofreading.json")); rp = json.load(open("results/replay_lattice.json"))
    klp = max((p for p in glob.glob("projects/omni_*/klassifikation.json")), key=lambda p: (json.load(open(p))["verletzt"] + json.load(open(p))["bewiesen"], os.path.getmtime(p)))
    kl = json.load(open(klp)); st = json.load(open(os.path.join(os.path.dirname(klp), "state.json")))
    bc = json.load(open("results/blind_claims.json")); rt = json.load(open("projects/proofreading/verifier_redteam.json"))
    T = trust()
    L = m["latenz_ergebnis_entscheidung"]; F = m["frage_zu_zertifikat"]; D = m["durchsatz"]; Z = m["zerlegung_summe_s"]
    H7a, H7b = rp["tests"]["H7a"], rp["tests"]["H7b"]
    fallen = rt.get("fallen", []); abgelehnt = sum(1 for f in fallen if f.get("ergebnis") == "korrekt_abgelehnt")
    runs = sorted(d for d in glob.glob("runs/omnigent/*") if os.path.isdir(d))
    F_ = {
        "zeitpunkt": time.strftime("%Y-%m-%dT%H:%M:%S"), "commit": git("rev-parse", "--short", "HEAD"), "branch": git("branch", "--show-current"),
        "metrics": {"lauf": m["lauf"], "latenz_median_s": r(L["alle"]["median"], 0), "latenz_n": L["alle"]["n"], "latenz_min_s": r(L["alle"]["min"], 0),
                    "latenz_max_s": r(L["alle"]["max"], 0), "latenz_ohne_kaltstart_median_s": r(L["ohne_kaltstart"]["median"], 0),
                    "frage_zu_zertifikat_median_s": r(F["alle"]["median"], 0), "frage_zu_zertifikat_n": F["alle"]["n"],
                    "zertifizierte_claims": D["zertifizierte_claims"], "abgelehnte_behauptungen": D["abgelehnte_behauptungen"],
                    "zertifiziert_pro_h": r(D["zertifiziert_pro_h"]), "kosten_pro_zertifikat_usd": r(D["kosten_usd_pro_zertifikat"], 2),
                    "kosten_gesamt_usd": r(D["kosten_usd_gesamt"], 2), "laufzeit_min": r(m["laufzeit_gesamt_s"] / 60, 0), "mensch_warten_min": r(m["mensch_warten_s"] / 60, 0),
                    "zeit_agenten_llm_s": r(Z["agenten_llm_s"], 0), "zeit_verifier_s": r(Z["verifier_s"], 0), "zeit_experimente_s": r(Z["experiment_s"], 0),
                    "speedup_manuell": m["speedup_ergebnis_zu_entscheidung"]},
        "replay": {"seeds": len(rp["seeds"]), "budget": rp["budget"], "mean_N_lab": r(rp["bedingungen"]["LAB"]["mittel_N"]), "mean_N_random": r(rp["bedingungen"]["ZUFALL"]["mittel_N"]),
                   "mean_N_no_feedback": r(rp["bedingungen"]["OHNE_FEEDBACK"]["mittel_N"]),
                   "speedup_vs_random": r(H7a["speedup"]), "speedup_vs_random_ci": [r(x) for x in H7a["ki95"]], "p_vs_random": r(H7a["p"], 3), "h7a_supported": H7a["erfolg"],
                   "speedup_vs_no_feedback": r(H7b["speedup"]), "speedup_vs_no_feedback_ci": [r(x, 2) for x in H7b["ki95"]], "p_vs_no_feedback": r(H7b["p"], 2), "h7b_supported": H7b["erfolg"]},
        "trust": {b: {k: v[k] for k in ("n", "richtig", "falsch", "anteil_richtig_pct", "anteil_falsch_pct", "falsch_ki95_pct")} for b, v in T["bedingungen"].items()},
        "verifier_stress": {"blind_claims": bc["claims"], "blind_akzeptiert": bc["akzeptiert"], "redteam_fallen": len(fallen), "redteam_fallen_abgelehnt": abgelehnt,
                            "selbsttest_faelle": {d: len(list(get_domain(d).selftest())) for d in ("proofreading", "lattice")}},
        "flaggschiff": {"topologien": kl["topologien"], "bewiesen": kl["bewiesen"], "verletzt": kl["verletzt"], "offen": kl["offen"],
                        "neu_im_omnigent_lauf": 8, "eta_min": kl["eta_min"]},
        "claims": {"omni_proofreading_bestaetigt": sum(1 for c in st["claims"] if c.get("status") == "bestätigt"), "omni_proofreading_negative": len(st.get("widerlegt", []))},
        "laeufe": {d: verify(d)[1] for d in runs},
        "plan": {"planungshorizont_stunden": 24, "hinweis": "keine Messung: Zeithorizont des Abschnitts 'Next 24 h'"},
    }
    # "neu_im_omnigent_lauf" aus dem Protokoll statt von Hand: Überraschungsgrund des ersten Laufs zählt die neuen Verletzungen
    import re
    neu = set()
    for run in runs:                                              # neue Verletzungen = Überraschungsgründe aller Läufe (aus dem Protokoll)
        for x in (json.loads(l) for l in open(f"{run}/record.jsonl")):
            e = x.get("ergebnis")
            if isinstance(e, dict) and e.get("ueberraschung"): neu |= set(re.findall(r"fam2_\d+", e.get("ueberraschung_grund", "").split("ausserhalb")[0]))
    F_["flaggschiff"]["neu_in_omnigent_laeufen"] = len(neu); F_["flaggschiff"].pop("neu_im_omnigent_lauf", None)
    F_["flaggschiff"]["quelle"] = klp; F_["omnigent_laeufe"] = len(runs)
    json.dump(F_, open("results/FROZEN.json", "w"), indent=1, ensure_ascii=False, default=str); print(json.dumps(F_, indent=1, ensure_ascii=False, default=str)[:3000])


if __name__ == "__main__":
    main()
