"""Qualitätskriterium für den Dauerbetrieb: Wann ist ein Projekt publikationsreif?"""
import json, os, re

RIGOROS = ("computed_rigorous", "proved_lean")
NEU = ("offen_laut_literatur", "nicht_gefunden")


def _referee(referee_report):
    """referee_report: Pfad zu referee.json/referee_report.md, dict oder None -> Liste der Schwächen."""
    if isinstance(referee_report, dict): return referee_report.get("weaknesses", [])
    if not referee_report: return None
    if str(referee_report).endswith(".md"):
        j = str(referee_report)[:-len("referee_report.md")] + "referee.json"
        if os.path.exists(j): referee_report = j
        else:                                                   # Altbestand: Markdown parsen
            t = open(referee_report).read(); W = []
            for blk in re.split(r"^## \d+\. ", t, flags=re.M)[1:]:
                W.append({"title": blk.split("\n")[0], "severity": (re.search(r"Severity: (\w+)", blk) or [None, "major"])[1],
                          "fixable_by_rewriting": "Fixable by rewriting: True" in blk, "status": (re.search(r"Status: (.*)", blk) or [None, "open"])[1]})
            return W
    if not os.path.exists(referee_report): return None
    return json.load(open(referee_report)).get("weaknesses", [])


def publikationsreif(state, referee_report, protokoll=None, domain=None):
    """-> (bool, grund). Stopp nur, wenn ALLES gilt:
    1. >= 1 Claim mit relevanz=hauptresultat, level computed_rigorous/proved_lean, Status bestätigt (nicht angefochten);
    2. dessen Neuheit in {offen_laut_literatur, nicht_gefunden};
    3. writer.check() und Scope-Check des letzten Papers: 0 Verstöße (pruefprotokoll.json);
    4. Referee meldet keine schwere (major) Schwäche, die mit vorhandenen Claims behebbar wäre und offen ist."""
    claims = state.get("claims", [])
    def rel(c):
        if c.get("relevanz"): return c["relevanz"]
        if domain is not None and c.get("pruefung") and hasattr(domain, "relevanz"): return domain.relevanz(c["pruefung"])
        return None
    haupt = [c for c in claims if rel(c) == "hauptresultat" and c.get("level") in RIGOROS and c.get("status") == "bestätigt"]
    if not haupt: return False, "kein bestätigtes, rigoros geprüftes Hauptresultat"
    neu = [c for c in haupt if (c.get("neuheit") or {}).get("status") in NEU]
    if not neu: return False, f"{len(haupt)} Hauptresultat(e), aber keines neu laut Literatur (Status: " + \
                           ", ".join(sorted({str((c.get('neuheit') or {}).get('status')) for c in haupt})) + ")"
    if protokoll is None: return False, "kein Prüfprotokoll des Papers (pruefprotokoll.json fehlt)"
    if isinstance(protokoll, str): protokoll = json.load(open(protokoll)) if os.path.exists(protokoll) else None
    if protokoll is None: return False, "kein Prüfprotokoll des Papers (pruefprotokoll.json fehlt)"
    v = protokoll.get("verbleibende_verstoesse", [])
    if v: return False, f"Paper hat {len(v)} Verstöße (writer.check/Scope-Check), z. B. {str(v[0])[:120]}"
    W = _referee(referee_report)
    if W is None: return False, "kein Referee-Bericht"
    schwer = [w for w in W if str(w.get("severity", "major")).lower() == "major" and w.get("fixable_by_rewriting")
              and not str(w.get("status", "open")).startswith("addressed")]
    if schwer: return False, f"Referee: {len(schwer)} schwere, mit vorhandenen Claims behebbare Schwäche(n): " + "; ".join(str(w.get("title"))[:80] for w in schwer)
    return True, f"publikationsreif: Hauptresultat {neu[0]['id']} ({neu[0]['level']}, Neuheit {neu[0]['neuheit']['status']}), 0 Verstöße, keine schwere behebbare Referee-Schwäche"
