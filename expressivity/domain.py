"""Domain `expressivity`: which finite-state tasks (word problems of finite groups) can one layer of a linear RNN track exactly?

Agents see experiments that work in floating point (numerical eigenvalues, numerical closures, quick training runs). The
verifier recomputes independently and exactly (Q and real cyclotomic fields, exact closures, exact character-table margins,
GAP with exact cyclotomics when available). Tolerances and search limits belong to the verifier; claims may not carry them.
"""
import json, os, re
import numpy as np

from asd.domains.base import Domain
from .groups import get_group, alphabet
from .algebra import porder, cycle_type, Field, mat
from .realisation import verify as verify_realisation
from . import reps as REPS

FORBIDDEN_PREFIXES = ("tol", "genau", "prec", "eps", "cap", "seed", "margin", "max", "limit", "timeout", "budget")
GROUP_RE = re.compile(r"^(Z([2-9]|[1-9]\d{1,2})|Z2\^[1-6]|Z([2-9]|1\d)xZ([2-9]|1\d)|S[3-5]|A[3-5]|D([3-9]|1\d)|Q8|SG\d{1,3}_\d{1,4})$")
ALPH_RE = re.compile(r"^(all|involutions|transpositions|cycles3|cycles5|tn|c3c5)$")   # "gens" removed: depends on the stored permutation generators (red team)
CONSTRUCTIONS = ("perm", "so3", "planar", "count")      # search order: cheap first; count covers can be large
TWISTS = ("none", "involutions", "all")
FAMILIES = ("diag_pos", "diag_pm", "cdiag")


def strict_int(x, lo=0, hi=64):
    if isinstance(x, bool) or not isinstance(x, int): raise ValueError(f"expected an integer, got {x!r}")
    if not lo <= x <= hi: raise ValueError(f"integer {x} outside [{lo}, {hi}]")
    return x


def strict_bool(x):
    if not isinstance(x, bool): raise ValueError(f"expected true/false, got {x!r}")
    return x


def group_and_alphabet(p):
    g, a = p.get("group"), p.get("alphabet", "all")
    if not isinstance(g, str) or not GROUP_RE.match(g): raise ValueError(f"unknown group name {g!r}")
    if not isinstance(a, str) or not ALPH_RE.match(a): raise ValueError(f"unknown alphabet {a!r}")
    G = get_group(g); S = alphabet(G, a)
    return G, S


def lower_bound(G, S):
    """Certified lower bound on h*(G, Sigma) and its reason (lemmas L4 and nontriviality)."""
    if G.order == 1: return 0, "trivial group"
    if any(porder(s) >= 3 for s in S):
        return 2, "Lemma L4: a letter of order >= 3 cannot lift to a reflection (a rank-1 finite-order real deviation from I has order 2)"
    return 1, "nontrivial group: k = 0 means constant state"


def search_upper(G, S, max_k=8, stop_at=None):
    """The verifier's own search over its construction library; returns (best k, construction, twist, evidence).
    Cheap constructions first; stops as soon as a certificate reaches stop_at (the certified lower bound), since no better exists."""
    best = (None, None, None, None)
    for rep in CONSTRUCTIONS:
        if rep == "so3" and G.name not in ("A4", "S4", "A5"): continue
        if rep == "planar" and not (G.name.startswith("Z") and "^" not in G.name and "x" not in G.name or G.name.startswith("D")): continue
        if rep == "count" and not G.is_abelian(): continue
        for tw in TWISTS:
            try:
                R = REPS.construct(G, S, rep, tw)
            except (ValueError, OverflowError):
                continue
            ok, why, ev = verify_realisation(G, S, R, max_k)
            if ok and (best[0] is None or ev["max_rank"] < best[0]):
                best = (ev["max_rank"], rep, tw, ev)
            if best[0] is not None and stop_at is not None and best[0] <= stop_at: return best
    return best


def gap_codim_table(G):
    """Exact codimension table and kernels from GAP (independent oracle). None if GAP is unavailable."""
    from .gap_oracle import codim_table_gap
    return codim_table_gap(G)          # GAP is mandatory for h_faithful (red team: no silent fallback to numerics alone)
    # any other GAP failure is an error of the oracle and must not pass silently


class ExpressivityDomain(Domain):
    name = "expressivity"
    recherche_ziel = ("Which finite automata and group word problems (state tracking) can transformers, state-space models (Mamba), "
                      "and linear RNNs with diagonal or Householder (DeltaNet, DeltaProduct) transitions express, in one layer or several, "
                      "with exact constructions and impossibility results (circuit complexity TC0/NC1, Krohn-Rhodes, reflection groups)?")
    recherche_sperre = []          # no hidden answer key: truth comes from the exact verifier (assumptions A7)
    kontext = """Field: expressivity of one-layer linear recurrent networks on state-tracking tasks.
Task (word problem): a finite group G and an input alphabet Sigma (a generating subset of G). The network reads letters s_1, s_2, ...
and must output g_t = s_t * ... * s_1 at every position, for inputs of EVERY length.
One layer: state h_t (vector or matrix), h_t = A(s_t) h_{t-1} + B(s_t), output = arbitrary function of h_t. The transition A(s) depends
only on the current letter. Transition families: diag_pos (diagonal, entries in [0,1], like Mamba), diag_pm (diagonal, entries in
[-1,1]), cdiag (complex diagonal), HH_k (product of k generalized Householder matrices I - beta u u^T with beta in [0,2], like
DeltaNet for k = 1 and DeltaProduct for k > 1).
Key quantity: h*(G, Sigma) = the least k such that a finite group H, a surjection pi: H -> G, lifts t_s of the letters generating H,
and a faithful real representation rho of H exist with rank(rho(t_s) - I) <= k for every letter. An exact finite-state HH_k
realisation exists iff k >= h*(G, Sigma) (necessity via compression of the transition monoid; sufficiency via an invariant inner
product and the Cartan–Dieudonné theorem). h(G, Sigma) is the same minimum restricted to H = G (faithful representations of G).
Known anchors: a single reflection has order 2; rank(M - I) of a product of k reflections is at most k; rank(M - I) of a
permutation matrix is n minus its number of cycles; finite subgroups of SO(3) are cyclic, dihedral, A4, S4, A5.
Groups: Z<n>, Z2^<k>, Z<a>xZ<b>, S<n> (n <= 5), A<n> (n <= 5), D<n> (dihedral of order 2n), Q8. Alphabets: all, involutions,
transpositions (S<n> only), cycles3, cycles5 (A<n>, S<n> only),
tn (S<n>: the transposition (1 2) and the n-cycle (1 ... n)), c3c5 (A5: the 3-cycle (1 2 3) and the 5-cycle (1 2 3 4 5))."""
    primitive_doc = """Available experiments (JSON {"op": ..., "args": {...}}); all are floating-point explorations, not proofs:
- group_info {group}: order, abelian, solvable, derived series, exponent, center size, element orders per conjugacy class.
- alphabet_info {group, alphabet}: number of letters, orders and cycle types of the letters.
- real_irreps {group}: real irreducible representations (degree, Frobenius-Schur indicator) and, per conjugacy class, the codimension
  of the fixed space and the multiplicity of eigenvalue -1 (from a numerical character table).
- faithful_h {group, alphabet}: numerical h(G, Sigma) and the chosen irreducibles.
- numeric_construction {group, alphabet, construction: perm|so3|planar|count, twist: none|involutions|all}: builds the matrices in
  floating point and reports, per letter class, the numerical rank of (M - I), and the size of a numerical closure (capped).
- train_quick {arch: diag_pos|diag_pm|hh1|hh2|hh3|hh4|lstm, group, alphabet, steps <= 1500}: one small training run (1 seed,
  train length 32), reports accuracy at length 32 and 128 (observed, noisy)."""
    claim_doc = """Check types (the verifier recomputes exactly; it never takes tolerances or limits from the claim):
- {"typ": "realisation", "group": G, "alphabet": A, "k": int, "construction": "perm"|"so3"|"planar"|"count", "twist": "none"|"involutions"|"all"}:
  the construction (letters multiplied by -1 for the twisted letters) is an exact HH_k realisation: finite group H, consistent onto
  readout H -> G, invariant inner product, rank(M - I) <= k with explicit reflection factorisation. Certifies h*(G, A) <= k.
- {"typ": "realisation_matrices", "group": G, "alphabet": A, "k": int, "matrices": [one rational matrix per letter, letters in the
  verifier's alphabet order, entries as strings like "1/2"]}: same certificate for explicitly given rational matrices.
- {"typ": "hstar_lower", "group": G, "alphabet": A, "k": int}: h*(G, A) >= k, certified by a lemma the verifier can apply (k <= 2).
- {"typ": "hstar_value", "group": G, "alphabet": A, "value": int}: the verifier certifies a matching lower bound and finds a
  realisation with k = value itself.
- {"typ": "h_faithful", "group": G, "alphabet": A, "value": int}: h(G, A) (faithful representations of G only) equals value.
- {"typ": "diag_realisable", "family": "diag_pos"|"diag_pm"|"cdiag", "group": G, "alphabet": A, "value": true|false}: whether an
  exact finite-state one-layer realisation with that diagonal family exists."""

    # ------------------------------------------------------------------ experiments (floating point)
    def run_op(self, op, args):
        try:
            if op == "group_info":
                G = get_group(str(args["group"]))
                cls = G.classes()
                return {"order": G.order, "abelian": G.is_abelian(), "solvable": G.is_solvable(), "perfect": G.is_perfect(),
                        "derived_series_orders": G.derived_series(), "exponent": G.exponent(), "center_size": len(G.center()),
                        "classes": [{"size": len(c), "element_order": porder(c[0]), "cycle_type": list(cycle_type(c[0]))} for c in cls]}
            if op == "alphabet_info":
                G, S = group_and_alphabet(args)
                from collections import Counter
                return {"letters": len(S), "orders": dict(Counter(porder(s) for s in S)),
                        "cycle_types": dict(Counter(str(cycle_type(s)) for s in S))}
            if op == "real_irreps":
                from .chartab import codim_table
                G = get_group(str(args["group"])); T = codim_table(G)
                return {"irreps": T["irreps"], "class_orders": [porder(c[0]) for c in T["classes"]],
                        "class_sizes": T["class_sizes"], "codim_fix": T["codim"], "mult_minus_one": T["minus"],
                        "hinweis": "numerical character table"}
            if op == "faithful_h":
                from .chartab import faithful_h
                G, S = group_and_alphabet(args); v, sel, T = faithful_h(G, S)
                return {"h_numerical": v, "chosen_irreps": [T["irreps"][i] for i in sel], "hinweis": "numerical"}
            if op == "numeric_construction":
                G, S = group_and_alphabet(args)
                R = REPS.construct(G, S, args.get("construction", "perm"), args.get("twist", "none"))
                Ms = {s: np.array([[float(x) for x in r] for r in M]) for s, M in R.items()}
                ranks = {}
                for s, M in Ms.items():
                    sv = np.linalg.svd(M - np.eye(len(M)), compute_uv=False)
                    ranks.setdefault(str(porder(s)), set()).add(int((sv > 1e-8).sum()))
                # numerical closure (capped at 2000)
                seen = [np.eye(len(next(iter(Ms.values()))))]; frontier = list(seen)
                while frontier and len(seen) < 2000:
                    nxt = []
                    for X in frontier:
                        for M in Ms.values():
                            Y = M @ X
                            if not any(np.allclose(Y, Z, atol=1e-8) for Z in seen): seen.append(Y); nxt.append(Y)
                    frontier = nxt
                return {"dim": len(next(iter(Ms.values()))), "numerical_rank_M_minus_I_by_letter_order": {k: sorted(v) for k, v in ranks.items()},
                        "numerical_closure_size": len(seen), "closure_capped": len(seen) >= 2000, "hinweis": "floating point, not a certificate"}
            if op == "train_quick":
                from .train import train_quick
                G, S = group_and_alphabet(args)
                steps = min(int(args.get("steps", 800)), 1500)
                return train_quick(str(args["arch"]), G, S, steps)
            return {"fehler": f"unknown op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    # ------------------------------------------------------------------ verifier (exact)
    def check(self, p, timeout=240):
        """Exact verification in a child process with a wall-clock limit (red team: unbounded searches/denominators)."""
        import multiprocessing as mp
        ctx = mp.get_context("fork"); q = ctx.Queue()
        proc = ctx.Process(target=lambda: q.put(self._check(p))); proc.start(); proc.join(timeout)
        if proc.is_alive():
            proc.terminate(); proc.join()
            return False, f"verifier time limit ({timeout} s) exceeded: not certified", {}
        try: return q.get(timeout=5)
        except Exception: return False, "verifier child process failed", {}

    def _check(self, p):
        try:
            if not isinstance(p, dict): return False, "claim must be a JSON object", {}
            bad = [k for k in p if k.lower().startswith(FORBIDDEN_PREFIXES)]
            if bad: return False, f"rule violation: the claim may not set {sorted(bad)} (tolerances and limits belong to the verifier)", {}
            t = p.get("typ")
            if t == "realisation":
                G, S = group_and_alphabet(p); k = strict_int(p.get("k"), 0, 16)
                rep, tw = p.get("construction"), p.get("twist", "none")
                if rep not in CONSTRUCTIONS or tw not in TWISTS: return False, "unknown construction or twist", {}
                try: R = REPS.construct(G, S, rep, tw)
                except (ValueError, OverflowError) as e: return False, f"construction not available: {e}"[:200], {}
                return verify_realisation(G, S, R, k)
            if t == "realisation_matrices":
                G, S = group_and_alphabet(p); k = strict_int(p.get("k"), 0, 16)
                Ms = p.get("matrices")
                if not isinstance(Ms, list) or len(Ms) != len(S): return False, "need one rational matrix per letter (alphabet order)", {}
                from fractions import Fraction
                F = Field(1)
                R = {s: mat(F, [[Fraction(str(x)) for x in row] for row in M]) for s, M in zip(S, Ms)}
                return verify_realisation(G, S, R, k)
            if t == "hstar_lower":
                G, S = group_and_alphabet(p); k = strict_int(p.get("k"), 0, 16)
                lb, why = lower_bound(G, S)
                return k <= lb, f"certified lower bound h* >= {lb} ({why}); claimed >= {k}", {"lower": lb}
            if t == "hstar_value":
                G, S = group_and_alphabet(p); v = strict_int(p.get("value"), 0, 16)
                lb, why = lower_bound(G, S); ub, rep, tw, ev = search_upper(G, S, stop_at=lb)
                if ub is None: return False, f"no realisation found in the verifier's library; lower bound {lb}", {"lower": lb}
                ok = lb == ub == v
                return ok, (f"lower bound {lb} ({why}); verifier's own certificate: construction {rep}, twist {tw}, k = {ub} "
                            f"(|H| = {ev['H_order']}, dim {ev['dim']}); " + ("exact" if lb == ub else "bounds do not meet")), {"lower": lb, "upper": ub, "construction": rep, "twist": tw, "evidence": ev}
            if t == "h_faithful":
                G, S = group_and_alphabet(p); v = strict_int(p.get("value"), 0, 64)
                from .chartab import faithful_h, minimise
                own, sel, T = faithful_h(G, S)
                gap = gap_codim_table(G); gv = None
                if gap is not None:
                    sc = sorted({gap["class_of"](s) for s in S})
                    gv, _ = minimise(gap["codim"], gap["kernels"], sc, gap["n_classes"], gap["class_of"](G.e))
                agree = gv == own
                if not agree: return False, f"own numerical value {own} disagrees with GAP {gv}", {"own": own, "gap": gv}
                return own == v, f"h(G, Sigma) = {own} (own character table" + f", GAP exact: {gv})", {"own": own, "gap": gv}
            if t == "diag_realisable":
                fam = p.get("family"); G, S = group_and_alphabet(p); v = strict_bool(p.get("value"))
                if fam not in FAMILIES: return False, f"unknown family {fam!r}", {}
                if fam == "diag_pos": truth, why = G.order == 1, "only the trivial group (Lemma L5: nonnegative real diagonal of finite order is I)"
                elif fam == "diag_pm": truth, why = G.is_abelian() and G.exponent() <= 2, "iff G is an elementary abelian 2-group (Lemma L5)"
                else: truth, why = G.is_abelian(), "iff G is abelian (Lemma L5)"
                return truth == v, f"{fam} realises {G.name}: {truth} ({why})", {"truth": truth}
            return False, f"unknown check type {t!r}", {}
        except Exception as e:
            return False, f"check not executable: {type(e).__name__}: {e}"[:300], {}

    def selftest(self):
        R = lambda g, a, k, c, tw="none": {"typ": "realisation", "group": g, "alphabet": a, "k": k, "construction": c, "twist": tw}
        return [
            # realisation certificates: true and near-boundary false
            (R("A5", "involutions", 1, "so3", "involutions"), True),
            (R("A5", "involutions", 1, "so3"), False),                # same matrices without the -1 lift: rank 2
            (R("A5", "all", 2, "so3"), True), (R("A5", "all", 1, "so3"), False),
            (R("S5", "transpositions", 1, "perm"), True), (R("S5", "all", 4, "perm"), True), (R("S5", "all", 3, "perm"), False),
            (R("S4", "all", 2, "so3"), True), (R("Z3", "all", 2, "planar"), True), (R("Z3", "all", 1, "planar"), False),
            (R("Z2^3", "all", 1, "count"), True), (R("Z2^3", "all", 1, "perm"), False),
            (R("S3", "all", 2, "count"), False),                        # count cover needs an abelian group
            # explicit matrices: a consistent one and an inconsistent one (two transpositions sharing a matrix)
            ({"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["-1"]]]}, True),
            ({"typ": "realisation_matrices", "group": "S3", "alphabet": "transpositions", "k": 1,
              "matrices": [[["-1", "0"], ["0", "1"]]] * 3}, False),
            # lower bounds
            ({"typ": "hstar_lower", "group": "A5", "alphabet": "all", "k": 2}, True),
            ({"typ": "hstar_lower", "group": "A5", "alphabet": "involutions", "k": 2}, False),
            ({"typ": "hstar_lower", "group": "S5", "alphabet": "all", "k": 3}, False),   # true or not, not certifiable here
            # exact values
            ({"typ": "hstar_value", "group": "A5", "alphabet": "involutions", "value": 1}, True),
            ({"typ": "hstar_value", "group": "A5", "alphabet": "all", "value": 2}, True),
            ({"typ": "hstar_value", "group": "A5", "alphabet": "all", "value": 1}, False),
            ({"typ": "hstar_value", "group": "Z2^3", "alphabet": "all", "value": 1}, True),
            ({"typ": "hstar_value", "group": "Z2^3", "alphabet": "all", "value": 3}, False),
            ({"typ": "hstar_value", "group": "S5", "alphabet": "all", "value": 4}, False),  # bounds 2 and 4 do not meet
            # faithful h (own character table, GAP cross-check)
            ({"typ": "h_faithful", "group": "S5", "alphabet": "all", "value": 4}, True),
            ({"typ": "h_faithful", "group": "S5", "alphabet": "all", "value": 3}, False),
            ({"typ": "h_faithful", "group": "Z2^3", "alphabet": "all", "value": 3}, True),
            ({"typ": "h_faithful", "group": "A5", "alphabet": "involutions", "value": 1}, False),
            ({"typ": "h_faithful", "group": "Q8", "alphabet": "all", "value": 4}, True),
            # diagonal families
            ({"typ": "diag_realisable", "family": "diag_pm", "group": "Z2^3", "alphabet": "all", "value": True}, True),
            ({"typ": "diag_realisable", "family": "diag_pm", "group": "Z3", "alphabet": "all", "value": True}, False),
            ({"typ": "diag_realisable", "family": "cdiag", "group": "Z3", "alphabet": "all", "value": True}, True),
            ({"typ": "diag_realisable", "family": "cdiag", "group": "S3", "alphabet": "all", "value": True}, False),
            ({"typ": "diag_realisable", "family": "diag_pos", "group": "Z2", "alphabet": "all", "value": False}, True),
            # rule violations and malformed claims
            ({**R("A5", "all", 2, "so3"), "tolerance": 0.1}, False),
            (R("A5", "all", 2.0, "so3"), False), (R("A5", "all", True, "so3"), False),
            ({"typ": "diag_realisable", "family": "diag_pm", "group": "Z2", "alphabet": "all", "value": "true"}, False),
            (R("A6", "all", 2, "perm"), False),                          # group outside the verifier's range
            # red-team regressions (analysis/redteam.md): wrong group names, prefix-matched forbidden keys, non-finite matrices
            ({"typ": "hstar_value", "group": "S1", "alphabet": "all", "value": 1}, False),
            ({"typ": "h_faithful", "group": "D2", "alphabet": "all", "value": 1}, False),
            ({"typ": "h_faithful", "group": "Z2xZ2", "alphabet": "all", "value": 2}, True),
            ({**R("A5", "all", 2, "so3"), "tol_rel": 0.1}, False),
            ({"typ": "realisation_matrices", "group": "Z2", "alphabet": "all", "k": 1, "matrices": [[["1/2"]]]}, False),
            ({"typ": "hstar_value", "group": "Z2xZ2", "alphabet": "transpositions", "value": 1}, False),   # alphabet only for S<n>
            ({"typ": "hstar_value", "group": "S3", "alphabet": "cycles3", "value": 2}, False),   # alphabet does not generate S3
        ]

    def consistent(self, antwort, p):
        """The answer must match what the checks certify (lab round 1 loophole EX10, red-team bug 3):
        - 'unknown'/empty answers never count; 'zahl' must be a real number (not a boolean) if given;
        - every integer in the answer text (group names such as A5, Z2^3 removed) and the 'zahl' must be certified by a check:
          hstar_value values, realisation k (only as upper bound wording is not parsed, so k counts), hstar_lower k >= 1, and
          h_faithful values only if the answer does not speak about h*;
        - a negative / impossibility answer needs a nontrivial impossibility certificate: hstar_lower or hstar_value with value >= 2,
          or diag_realisable with value false."""
        t = str(antwort.get("antwort", "")).strip().lower()
        if t in ("", "unbekannt", "unknown", "none", "null", "n/a"): return False
        ps = [q for q in (antwort.get("pruefungen") or [antwort.get("pruefung")]) if isinstance(q, dict)] or [p]
        star = "h*" in t or "hstar" in t or "h^*" in t
        cert = set()
        for q in ps:
            if q.get("typ") == "hstar_value": cert.add(q.get("value"))
            if q.get("typ") in ("realisation", "realisation_matrices"): cert.add(q.get("k"))
            if q.get("typ") == "hstar_lower" and isinstance(q.get("k"), int) and q["k"] >= 1: cert.add(q.get("k"))
            if q.get("typ") == "h_faithful" and not star: cert.add(q.get("value"))
        words = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "single": 1, "eins": 1, "zwei": 2, "drei": 3, "vier": 4}
        body = re.sub(r"\b(sg\d+_\d+|z\d+x?z?\d*(\^\d+)?|[sad]\d+|q8|so\(\d\)|o\(\d\)|h3|nc1|tc0|ac0)\b", " ", t)
        nums = {int(x) for x in re.findall(r"(?<![\w.])\d+(?![\w.])", body)} | {v for w, v in words.items() if re.search(rf"\b{w}\b", body)}
        negative = bool(re.match(r"^(nein|no|not|false|falsch|impossible|unm\u00f6glich|cannot|kann nicht|nicht)\b", t)) or \
            any(w in t for w in (" not ", "not enough", "cannot", "impossible", " nicht ", "reicht nicht", "does not", "insufficient", "fails"))
        lower = max([q["k"] for q in ps if q.get("typ") == "hstar_lower" and isinstance(q.get("k"), int)] +
                    [q["value"] for q in ps if q.get("typ") == "hstar_value" and isinstance(q.get("value"), int)] + [0])
        allowed = cert | (set(range(lower)) if negative else set())       # a negative answer may name the values it rules out
        if nums - allowed: return False
        z = antwort.get("zahl")
        if z is not None:
            if isinstance(z, bool): return False
            try: zf = float(z)
            except (TypeError, ValueError): return False
            if not any(isinstance(c, (int, float)) and not isinstance(c, bool) and float(c) == zf for c in cert): return False
        strong = any((q.get("typ") == "hstar_lower" and isinstance(q.get("k"), int) and q["k"] >= 2) or
                     (q.get("typ") == "hstar_value" and isinstance(q.get("value"), int) and q["value"] >= 2) or
                     (q.get("typ") == "diag_realisable" and q.get("value") is False) for q in ps)
        if negative and not strong: return False
        return True

    def level(self, p):
        return "computed_rigorous"

    def describe(self, p):
        t = p.get("typ"); g, a = p.get("group"), p.get("alphabet", "all")
        if t == "realisation":
            tw = {"none": "", "involutions": " with every involution letter lifted to its negative", "all": " with every letter negated"}[p.get("twist", "none")]
            return (f"The {p.get('construction')} construction{tw} is an exact one-layer realisation of the word problem of {g} with alphabet "
                    f"'{a}' using at most {p.get('k')} Householder reflections per token (certified); hence h*({g}, {a}) <= {p.get('k')}.")
        if t == "realisation_matrices":
            return f"The given rational matrices are an exact one-layer realisation of {g} with alphabet '{a}' using at most {p.get('k')} reflections per token (certified)."
        if t == "hstar_lower":
            k = p.get("k"); why = {0: "trivial", 1: "G is nontrivial", 2: "a letter of order >= 3; Lemma L4, Lean-checked"}.get(k, "")
            return f"h*({g}, {a}) >= {k} ({why}); by Lemma L2 every finite-state one-layer realisation of this word problem needs at least {k} Householder factors per token."
        if t == "hstar_value":
            v = p.get("value"); low = "G is nontrivial" if v == 1 else "Lemma L4 (Lean-checked) and Lemma L2 (hand proof)"
            return (f"h*({g}, {a}) = {v}: for finite-state one-layer realisations, exactly {v} Householder factors per token are necessary "
                    f"(lower bound: {low}) and sufficient (exact certificate).")
        if t == "h_faithful": return f"h({g}, {a}) = {p.get('value')} over faithful real representations of {g} (own numerical character table and GAP exact agree)."
        if t == "diag_realisable":
            return f"A one-layer {p.get('family')} recurrence {'can' if p.get('value') else 'cannot'} realise the word problem of {g} exactly (finite-state)."
        return "Check passed: " + json.dumps(p)


DOMAIN = ExpressivityDomain()
