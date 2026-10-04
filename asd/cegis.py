"""CEGIS-Kennzahl: Anteil der Runden mit Gegenbeispiel-Rückmeldung, in denen eine VERFEINERTE Vermutung bestand (die ursprüngliche nicht).
  python -m asd.cegis <projekt>"""
import json, sys


def quote(state):
    r = [x.get("cegis") for x in state.get("runden", []) if (x.get("cegis") or {}).get("verfeinerungen")]
    n = len(r); k = sum(1 for x in r if x.get("verfeinert_bestanden"))
    return {"runden_mit_gegenbeispiel": n, "verfeinert_bestanden": k, "anteil": (k / n) if n else None}


if __name__ == "__main__":
    print(json.dumps(quote(json.load(open(f"projects/{sys.argv[1]}/state.json"))), ensure_ascii=False))
