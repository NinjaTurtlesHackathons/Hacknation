"""Topologie-Familien für Kinetic Proofreading. Der PRÜFER erzeugt die Familie selbst (Grundgesetz G3: der Agent bestimmt
nicht, welche Topologien zählen). Familie 'gebunden<=k': alle zusammenhängenden Netzwerke mit einem ungebundenen Zustand E
und k gebundenen Zuständen C0..C{k-1}, deren Kanten aus folgendem Katalog stammen:
  E-Ci  Bindung/Abdissoziation (diskriminierend, ohne Treibstoff) | Ci->E mit Treibstoff (Verwerfen, diskriminierend, fuel 1)
  Ci->E Produktbildung (nicht diskriminierend) | Ci->Cj Umwandlung (fuel 0 oder 1)
Bedingungen: mindestens eine Bindungskante, genau eine Produktkante, höchstens eine Kante je (Typ, Paar), Modellregeln (validate_spec).
"""
import itertools, json
from . import proofreading as P


def family(k):
    B = [f"C{i}" for i in range(k)]; specs = []
    cand = []
    for c in B:
        cand.append(("bind", c, "E", True, 0, 0))
        cand.append(("verw", c, "E", True, 1, 0))
    for a, b in itertools.permutations(B, 2):
        if a < b: cand.append(("umw0", a, b, False, 0, 0)); cand.append(("umw1", a, b, False, 1, 0)); cand.append(("umw1r", b, a, False, 1, 0))
    for p in B:                                                    # genau eine Produktkante
        for mask in itertools.product([0, 1], repeat=len(cand)):
            sel = [c for c, m in zip(cand, mask) if m]
            if not any(c[0] == "bind" for c in sel): continue
            pairs = [(frozenset((c[1], c[2])), c[0][:3]) for c in sel if c[0].startswith("umw")]
            if len(pairs) != len(set(pairs)): continue          # höchstens eine Umwandlungskante je Paar
            kanten = [{"id": f"{c[0]}_{c[1]}_{c[2]}", "von": c[1], "nach": c[2], "diskriminierend": c[3], "fuel": c[4], "produkt": 0} for c in sel]
            kanten.append({"id": f"prod_{p}", "von": p, "nach": "E", "diskriminierend": False, "fuel": 0, "produkt": 1})
            spec = {"name": f"fam{k}_{len(specs)}", "ungebunden": ["E"], "gebunden": B, "kanten": kanten}
            if not P.validate_spec(spec): specs.append(spec)
    return specs


if __name__ == "__main__":
    for k in (1, 2):
        f = family(k); print(k, len(f))


def _prove_one(args):
    k, name, ausdruck = args
    from .proofreading_symbolic import prove_lower_bound
    spec = next(x for x in family(k) if x["name"] == name)
    return name, bool(prove_lower_bound(spec, "1", 0, ausdruck)["bewiesen"])


def prove_family(k, names, ausdruck, workers=4, timeout=1800):
    """Beweist eta >= ausdruck für jedes genannte Mitglied (parallel). Gibt {name: bewiesen} zurück; Zeitüberschreitung = nicht bewiesen."""
    from concurrent.futures import ProcessPoolExecutor, TimeoutError as TE
    out = {n: False for n in names}
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(_prove_one, (k, n, ausdruck)): n for n in names}
        try:
            for f in __import__("concurrent.futures").futures.as_completed(futs, timeout=timeout):
                n, b = f.result(); out[n] = b
        except TE:
            pass
    return out
