"""Schemas für Experiment-Specs und Claims je Domäne (MCP-Server). Unbekannte Felder werden abgelehnt; Toleranz-Felder gehören dem
Prüfer und werden entfernt (nicht abgelehnt), damit der Nutzer sieht, dass sie ignoriert wurden. Kein Feld wird als Code/Pfad ausgeführt."""
import inspect

TOLERANZ_FELDER = {"toleranz", "tolerance", "tol", "genauigkeit", "accuracy", "precision", "rtol", "atol"}
NUM, INT, STR, LIST, DICT, ANY = "number", "integer", "string", "array", "object", "any"

# ---- Claims: typ -> {feld: (typ, pflicht)} -----------------------------------------------------------------------------------
CLAIMS = {
    "lattice": {
        "argmin2d": {"nu": (NUM, True), "erwartet": (STR, True), "y": (NUM, False)},
        "argmin3d": {"nu": (NUM, True), "erwartet": (STR, True)},
        "vorzeichenwechsel": {"groesse": (STR, True), "nu_lo": (NUM, True), "nu_hi": (NUM, True)},
        "koexistenz": {"nu": (NUM, True)},
        "grenzwert": {"groesse": (STR, True), "erwartet": (NUM, True)},
        "vergleich_nd": {"nu": (NUM, True), "gitter": (STR, True), "gegen": (LIST, False)},
        "argmin_nd": {"d": (INT, True), "nu": (NUM, True), "erwartet": (STR, True)},
    },
    "proofreading": {
        "erreichbar": {"topologie": (ANY, True), "params": (DICT, True), "eta_max": (NUM, True), "sigma_max": (NUM, False), "v_min": (NUM, False)},
        "untere_schranke": {"topologie": (ANY, True), "c": (ANY, False), "k": (INT, False), "ausdruck": (STR, False)},
        "optimum": {"topologie": (ANY, True), "eta_min": (NUM, True), "sigma_max": (NUM, False), "v_min": (NUM, False), "fest": (DICT, False)},
        "erreichbar_liste": {"faelle": (LIST, True)},
        "schranke_familie": {"familie": (STR, True), "ausdruck": (STR, True), "mitglieder": (LIST, False)},
    },
}
FALL = {"topologie": (ANY, True), "params": (DICT, True), "eta_max": (NUM, True), "sigma_max": (NUM, False), "v_min": (NUM, False)}

# ---- Experimente: op -> {arg: (typ, pflicht)} ----------------------------------------------------------------------------------
OPS = {
    "proofreading": {
        "param_names": {"topologie": (ANY, True)},
        "evaluate": {"topologie": (ANY, True), "params": (DICT, True)},
        "optimize": {"topologie": (ANY, True), "sigma_max": (NUM, False), "v_min": (NUM, False), "starts": (INT, False), "seed": (INT, False), "fest": (DICT, False)},
        "front": {"topologie": (ANY, True), "sigmas": (LIST, True), "starts": (INT, False), "seed": (INT, False)},
        "search_counterexamples": {"names": (LIST, True), "eta_max": (NUM, False)},
        "classify_family": {"k": (INT, True), "ausdruck": (STR, False)},
        "family": {"k": (INT, True)},
        "identify": {"punkte": (LIST, True), "holdout": (INT, False)},
    },
}


def _lattice_ops():
    from .domains import lattice as L
    out = {}
    for op, fn in L.PRIMITIVES.items():
        sig = inspect.signature(fn)
        out[op] = {n: (ANY, p.default is inspect.Parameter.empty) for n, p in sig.parameters.items() if p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}
    return out


def ops(domain):
    if domain == "lattice": return _lattice_ops()
    return OPS.get(domain, {})


def _typ_ok(v, t):
    if t == ANY: return isinstance(v, (str, int, float, list, dict)) and not isinstance(v, bool)
    if t == NUM: return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == INT: return isinstance(v, int) and not isinstance(v, bool)
    if t == STR: return isinstance(v, str)
    if t == LIST: return isinstance(v, list)
    if t == DICT: return isinstance(v, dict)
    return False


def _felder(obj, schema, wo):
    fehler = [f"{wo}: unbekanntes Feld '{k}'" for k in obj if k not in schema]
    fehler += [f"{wo}: Pflichtfeld '{k}' fehlt" for k, (t, req) in schema.items() if req and k not in obj]
    fehler += [f"{wo}: Feld '{k}' hat falschen Typ (erwartet {t})" for k, (t, req) in schema.items() if k in obj and obj[k] is not None and not _typ_ok(obj[k], t)]
    return fehler


def validate_claim(domain, claim):
    """-> (bereinigter_claim, ignorierte_toleranzen, fehler). Toleranz-Felder werden entfernt (auch in Unterfällen)."""
    if not isinstance(claim, dict): return None, [], ["Claim muss ein JSON-Objekt sein"]
    S = CLAIMS.get(domain)
    if S is None: return None, [], [f"Domäne {domain} hat kein Claim-Schema"]
    c = dict(claim); ign = sorted(k for k in c if k in TOLERANZ_FELDER)
    for k in ign: c.pop(k)
    t = c.get("typ")
    if t not in S: return None, ign, [f"unbekannter Claim-Typ {t!r}; erlaubt: {sorted(S)}"]
    fehler = _felder({k: v for k, v in c.items() if k != "typ"}, S[t], f"Claim {t}")
    if t == "erreichbar_liste" and isinstance(c.get("faelle"), list):
        neu = []
        for i, f in enumerate(c["faelle"]):
            if not isinstance(f, dict): fehler.append(f"faelle[{i}] muss ein Objekt sein"); continue
            f = dict(f); ign += [f"faelle[{i}].{k}" for k in f if k in TOLERANZ_FELDER]
            for k in TOLERANZ_FELDER: f.pop(k, None)
            fehler += _felder(f, FALL, f"faelle[{i}]"); neu.append(f)
        c["faelle"] = neu
        if not neu: fehler.append("faelle ist leer")
    return (c if not fehler else None), ign, fehler


def validate_spec(domain, spec):
    """spec = {"op": ..., "args": {...}} -> (spec, fehler)."""
    if not isinstance(spec, dict): return None, ["Spec muss ein JSON-Objekt {op, args} sein"]
    extra = [k for k in spec if k not in ("op", "args")]
    if extra: return None, [f"unbekannte Felder in der Spec: {extra} (erlaubt: op, args)"]
    O = ops(domain); op = spec.get("op"); args = spec.get("args") or {}
    if op not in O: return None, [f"unbekanntes Experiment {op!r}; erlaubt: {sorted(O)}"]
    if not isinstance(args, dict): return None, ["args muss ein Objekt sein"]
    fehler = _felder(args, O[op], f"Experiment {op}")
    return ({"op": op, "args": args} if not fehler else None), fehler
