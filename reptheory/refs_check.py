"""Checks the bibliography against Crossref (tool evidence for every citation, else UNVERIFIED). Writes out/refs.json."""
import json, os, urllib.request

REFS = {"Serre": ("10.1007/978-1-4684-9458-7", "Linear Representations of Finite Groups", "Serre"),
        "FH": ("10.1007/978-1-4612-0979-9", "Representation Theory", "Fulton"),
        "JL": ("10.1017/CBO9780511814532", "Representations and Characters of Groups", "James")}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "refs.json")

res = {}
for key, (doi, title, author) in REFS.items():
    try:
        m = json.load(urllib.request.urlopen(f"https://api.crossref.org/works/{doi}", timeout=30))["message"]
        ok = title in m.get("title", [""])[0] and author in [a.get("family") for a in m.get("author", [])]
        res[key] = {"doi": doi, "status": "verified" if ok else "UNVERIFIED", "crossref_title": m.get("title"),
                    "crossref_authors": [a.get("family") for a in m.get("author", [])], "publisher": m.get("publisher"),
                    "issued": m.get("issued", {}).get("date-parts")}
    except Exception as e:
        res[key] = {"doi": doi, "status": "UNVERIFIED", "error": str(e)}
    print(key, res[key]["status"])
json.dump(res, open(OUT, "w"), indent=1)
