"""Domain "algo_efficiency": algorithms and efficiency of transformer inference, as a verifier-gated lab domain.

Scope (and nothing else): (1) attention in subquadratic time via the polynomial method and its limits, low-rank structure;
(2) speculative decoding with exact optimality certificates; (3) KV-cache compression.
Verifiers: exact rational arithmetic (speculative decoding), interval arithmetic with Remez / de la Vallee Poussin certificates
(polynomial method), paired permutation tests on fixed seeds (KV-cache, synthetic model). Experiments use different methods
(floating-point LP, Monte Carlo, Chebyshev interpolation, simulation), so a check is never the experiment re-run.
Interface names (kontext, primitive_doc, claim_doc, recherche_ziel, recherche_sperre, widerspricht) are fixed by asd/domains/base.py.
"""
import json
import math
from fractions import Fraction

from asd.domains.base import Domain
from . import kv, polyexp as PE, spec as S

FORBIDDEN_KEYS = {"tolerance", "toleranz", "tol", "precision", "genauigkeit", "dps", "seeds", "alpha_level", "margin"}
RULES = ("standard", "scaled", "rrs_iid", "rrs_wor")


def _num(x, name, lo=None, hi=None):
    v = S.frac(x)
    if (lo is not None and v < lo) or (hi is not None and v > hi): raise ValueError(f"{name}={x} outside [{lo}, {hi}]")
    return v


def _exp_args(p):
    B = _num(p["B"], "B", Fraction(1, 100), PE.B_MAX); eps = _num(p["eps"], "eps", Fraction(1, 10 ** 30), Fraction(1, 2))
    kind = p.get("error", "relative")
    if kind not in ("relative", "absolute"): raise ValueError("error must be 'relative' or 'absolute'")
    return B, eps, kind


def _degree(d):
    d = int(d)
    if not 0 <= d <= PE.D_MAX: raise ValueError(f"degree must be in [0, {PE.D_MAX}]")
    return d


def check_min_degree(B, eps, kind, d):
    up, iu = PE.certify_upper(B, eps, d, kind)
    if not up: return False, f"upper certificate failed at degree {d}: {iu}", {"upper": iu}
    if d == 0: return True, f"degree 0 suffices (rigorous sup error <= {iu['upper_bound']:.6e})", {"upper": iu}
    lo, il = PE.certify_lower(B, eps, d - 1, kind)
    if not lo: return False, f"lower certificate failed at degree {d - 1}: {il}", {"upper": iu, "lower": il}
    return True, (f"min degree = {d}: degree {d} achieves rigorous sup error <= {iu['upper_bound']:.6e} <= eps; every degree-{d - 1} "
                  f"polynomial has sup error >= {il['lower_bound']:.6e} > eps (de la Vallee Poussin)"), {"upper": iu, "lower": il}


class AlgoEfficiencyDomain(Domain):
    name = "algo_efficiency"
    recherche_ziel = ("Algorithms and efficiency of transformer inference: subquadratic attention (polynomial method, low-rank and "
                      "sketching approximations with error bounds, fine-grained complexity lower bounds under SETH such as Alman and Song), "
                      "speculative decoding (lossless speculative sampling, acceptance rate, multi-draft and tree verification, optimal "
                      "transport couplings, optimality proofs), and KV-cache compression (eviction, attention sinks, heavy hitters, quantization).")
    recherche_sperre = []
    kontext = (
        "Research area: efficiency of transformer inference. Three sub-problems.\n"
        "(A) Subquadratic attention via the polynomial method. If all logits satisfy |<q_i,k_j>| <= B and a polynomial P of degree d "
        "satisfies sup_{x in [-B,B]} |e^x - P(x)| / e^x <= eps (relative error; 'absolute' drops the division), then exp(QK^T) is "
        "approximated entrywise by a matrix of rank C(h+d, d) (h = head dimension), giving attention in about n*C(h+d,d) time instead "
        "of n^2. d*(B, eps) denotes the minimal such degree. Known anchors: the Taylor polynomial needs degree growing linearly in B; "
        "fine-grained complexity (SETH) rules out truly subquadratic exact-enough attention once B grows like sqrt(log n) (Alman and Song 2023), "
        "while B = o(sqrt(log n)) admits n^(1+o(1)) algorithms.\n"
        "(B) Speculative decoding on a finite vocabulary (V <= 8 tokens). Target distribution p, draft distribution q. A verification rule "
        "is lossless if the emitted token is distributed exactly as p. Standard speculative sampling (one draft) accepts with probability "
        "min(1, p(x)/q(x)) and resamples from the normalised residual max(0, p - q); it is lossless and its acceptance is sum_x min(p(x), q(x)). "
        "Rules available: 'standard'; 'scaled' (acceptance min(1, lambda*p/q), residual max(0, p - q*a)); 'rrs_iid' (recursive rejection "
        "sampling with k i.i.d. drafts from q); 'rrs_wor' (k drafts without replacement: each draft from q restricted to unused tokens, renormalised, "
        "residual taken w.r.t. the distribution actually drafted from). The optimal acceptance for k drafts is the maximum, over all lossless "
        "couplings between the k drafts and the output, of P(output is one of the drafts). Draft length: with i.i.d. acceptance alpha and cost "
        "ratio c (draft call / target call), the expected walltime speedup of drafting g tokens is (1 - alpha^(g+1)) / ((1 - alpha)(g c + 1)).\n"
        "(C) KV-cache compression on an explicit synthetic attention model (attention sinks, heavy hitters, locality; NOT a language model). "
        "Policies keep a budget of cached tokens: recent, sink_recent, h2o, random, oracle (oracle uses future queries: a lower bound).\n"
        "Probabilities must be given as exact decimals or fractions 'a/b' summing exactly to 1. Exact values should be stated as 'a/b'.")
    primitive_doc = """Available experiments (JSON {"op": ..., "args": {...}}):
- random_instance {V, seed, family: "dirichlet"|"zipf", conc}: random (p, q) with exact rational entries (denominator 1000).
- acceptance_mc {p, q, rule, k?, lambda?, samples?, seed?}: Monte Carlo simulation of a verification rule: acceptance estimate +- stderr and TV(empirical output, p). Statistical estimate only.
- multidraft_lp {p, q, k, mode: "iid"|"wor"}: floating-point LP for the optimal k-draft acceptance (candidate, not exact).
- speedup_curve {alpha, c, gmax?}: expected speedup for draft lengths 0..gmax (floating point).
- minimax_estimate {B, d, error: "relative"|"absolute"}: weighted max error of Chebyshev interpolation of exp on [-B,B] at degree d (~1 s). Near-minimax for absolute error; for relative error it can overestimate the minimax error by orders of magnitude.
- degree_scan {B, eps, error, dmax?}: smallest d whose Chebyshev-interpolation error estimate is <= eps (estimate; the true minimax degree can be smaller).
- taylor_degree {B, eps, error}: degree the Taylor polynomial at 0 needs (grid estimate), as a baseline.
- rank {h, d}: C(h+d, d), the rank of the degree-d polynomial-method factorisation for head dimension h.
- attention_spectrum {n, h, B, seed, ranks: [...]}: best rank-r relative Frobenius error of exp(B * cos-similarity matrix) for random unit vectors (numerical).
- kv_evaluate {policy, n, budget, seed}: mean relative output error of a KV eviction policy on the synthetic model (one seed)."""
    claim_doc = """Check types (the verifier recomputes independently; tolerances, precision and seeds are set by the verifier only):
- {"typ": "acceptance_rate", "p": [...], "q": [...], "value": "a/b"}: single-draft standard acceptance equals value exactly.
- {"typ": "scheme_acceptance", "p", "q", "rule": "standard"|"scaled"|"rrs_iid"|"rrs_wor", "k": int, "lambda": num (scaled only), "value": "a/b"}: exact acceptance of the rule.
- {"typ": "unbiased", "p", "q", "rule", "k"?, "lambda"?, "unbiased": true|false}: the rule's exact output distribution equals p (true) or differs from p (false).
- {"typ": "multidraft_optimal", "p", "q", "k": 1..4, "mode": "iid"|"wor", "value": "a/b"}: optimal lossless acceptance with k drafts equals value (exact max-flow = min-cut certificate).
- {"typ": "scheme_optimal", "p", "q", "k", "rule": "rrs_iid"|"rrs_wor", "optimal": true|false}: the rule attains (true) or misses (false) the optimal acceptance for its draft mode (rrs_iid ~ iid, rrs_wor ~ wor), exactly.
- {"typ": "optimal_gamma", "alpha": "a/b", "c": "a/b", "gamma": int}: gamma maximises the expected speedup over all draft lengths g >= 0 (exact, with tail certificate).
- {"typ": "exp_degree", "B": num, "eps": num, "error": "relative"|"absolute", "bound": "upper"|"lower", "d": int}: upper = some polynomial of degree <= d reaches sup error <= eps on [-B,B]; lower = every polynomial of degree <= d has sup error > eps. Rigorous (interval arithmetic). B <= 32, d <= 48.
- {"typ": "exp_min_degree", "B", "eps", "error", "d"}: d*(B, eps) = d exactly (upper certificate at d, lower certificate at d-1).
- {"typ": "polymethod_rank", "h": int, "B", "eps", "error", "rank": int}: rank = C(h+d*, d*) with d* the certified minimal degree.
- {"typ": "kv_compare", "policy_a", "policy_b", "n": int, "budget": int, "better": "a"}: policy_a has lower mean error than policy_b on the synthetic model over the verifier's 20 fixed seeds (paired permutation test p < 0.05 and bootstrap 95% CI of err_b/err_a above 1). Statistical."""

    # ---------- experiments ----------
    def run_op(self, op, args):
        try:
            a = dict(args or {})
            if op == "random_instance": return S.random_instance(**a)
            if op == "acceptance_mc":
                p, q = S.parse_pair(a.pop("p"), a.pop("q")); lam = a.pop("lambda", 1.0)
                return S.mc_scheme(p, q, a.pop("rule", "standard"), k=int(a.pop("k", 1)), lam=float(S.frac(lam)),
                                   samples=min(int(a.pop("samples", 100000)), 400000), seed=int(a.pop("seed", 0)))
            if op == "multidraft_lp":
                p, q = S.parse_pair(a["p"], a["q"]); return S.lp_multidraft(p, q, int(a["k"]), a.get("mode", "iid"))
            if op == "speedup_curve":
                al, c = float(S.frac(a["alpha"])), float(S.frac(a["c"])); g = min(int(a.get("gmax", 30)), 200)
                return {"speedup": [round((1 - al ** (i + 1)) / ((1 - al) * (i * c + 1)), 6) for i in range(g + 1)], "note": "floating point"}
            if op == "minimax_estimate":
                B, d = float(S.frac(a["B"])), int(a["d"])
                if not (0 < B <= PE.B_MAX and 0 <= d <= PE.D_MAX): return {"fehler": "B or d out of range"}
                return {"error_estimate": PE.cheb_interp_error(B, d, a.get("error", "relative")), "note": "Chebyshev interpolation (upper estimate of the minimax error)"}
            if op == "degree_scan":
                B, eps = float(S.frac(a["B"])), float(S.frac(a["eps"])); kind = a.get("error", "relative")
                for d in range(0, min(int(a.get("dmax", PE.D_MAX)), PE.D_MAX) + 1):
                    e = PE.cheb_interp_error(B, d, kind, grid=600)
                    if e <= eps: return {"d_estimate": d, "error_estimate": e, "note": "interpolation estimate; minimax degree may be smaller"}
                return {"d_estimate": None, "note": "not reached within dmax"}
            if op == "taylor_degree": return {"d": PE.taylor_degree(float(S.frac(a["B"])), float(S.frac(a["eps"])), a.get("error", "relative")), "note": "grid estimate"}
            if op == "rank": return {"rank": PE.polymethod_rank(a["h"], a["d"])}
            if op == "attention_spectrum":
                return kv.attention_spectrum(n=min(int(a.get("n", 256)), 1024), h=int(a.get("h", 16)), B=float(S.frac(a.get("B", 4))),
                                             seed=int(a.get("seed", 0)), ranks=tuple(int(r) for r in a.get("ranks", (1, 4, 16, 64))))
            if op == "kv_evaluate":
                return kv.evaluate(a["policy"], n=min(int(a.get("n", 512)), 2048), budget=int(a.get("budget", 64)), seed=int(a.get("seed", 0)))
            return {"fehler": f"unknown op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    # ---------- verifier ----------
    def check(self, p):
        try:
            bad = FORBIDDEN_KEYS & set(map(str.lower, p))
            if bad: return False, f"rule violation: the claim may not set {sorted(bad)} (verifier-owned)", {}
            t = p.get("typ")
            if t in ("acceptance_rate", "scheme_acceptance", "unbiased", "multidraft_optimal", "scheme_optimal"):
                P, Q = S.parse_pair(p["p"], p["q"])
            if t == "acceptance_rate":
                a = S.accept_standard(P, Q); ok = a == S.frac(p["value"])
                return ok, f"exact acceptance sum min(p,q) = {S.fstr(a)}", {"acceptance": S.fstr(a)}
            if t in ("scheme_acceptance", "unbiased"):
                rule = p.get("rule", "standard")
                if rule not in RULES: return False, f"unknown rule {rule}", {}
                out, a = S.step_output(P, Q, rule, k=int(p.get("k", 1)), lam=p.get("lambda", 1))
                if t == "scheme_acceptance":
                    return a == S.frac(p["value"]), f"exact acceptance of {rule} = {S.fstr(a)}", {"acceptance": S.fstr(a)}
                is_unb = out == P; tv = sum(abs(x - y) for x, y in zip(out, P)) / 2
                return is_unb == bool(p["unbiased"]), f"exact output distribution of {rule}: TV to p = {S.fstr(tv)}", {"output": [S.fstr(x) for x in out]}
            if t == "multidraft_optimal":
                mode = p.get("mode", "iid"); v, cert = S.optimal_multidraft(P, Q, int(p["k"]), mode)
                if not cert["certified"]: return False, f"internal: flow {cert['flow']} != cut {cert['cut']}", {}
                return v == S.frac(p["value"]), f"optimal acceptance = {S.fstr(v)} (exact max-flow = min-cut, cut set {cert['cut_set']})", {"value": S.fstr(v)}
            if t == "scheme_optimal":
                rule = p["rule"]; mode = {"rrs_iid": "iid", "rrs_wor": "wor"}.get(rule)
                if mode is None: return False, "rule must be rrs_iid or rrs_wor", {}
                k = int(p["k"]); v, cert = S.optimal_multidraft(P, Q, k, mode); _, a = S.step_output(P, Q, rule, k=k)
                return (a == v) == bool(p["optimal"]), f"{rule} acceptance {S.fstr(a)} vs optimal {S.fstr(v)} (certified)", {"scheme": S.fstr(a), "optimal": S.fstr(v)}
            if t == "optimal_gamma":
                arg, best, G = S.optimal_gamma(p["alpha"], p["c"])
                if arg is None: return False, "not certified: tail bound not reached", {}
                return int(p["gamma"]) in arg, f"argmax g = {arg}, speedup {float(best):.6f} (exact; no g > {G} can do better)", {"argmax": arg}
            if t in ("exp_degree", "exp_min_degree", "polymethod_rank"):
                B, eps, kind = _exp_args(p)
            if t == "exp_degree":
                d = _degree(p["d"])
                if p.get("bound") == "upper":
                    ok, info = PE.certify_upper(B, eps, d, kind); return ok, f"upper certificate (degree {d}): {info}", info
                if p.get("bound") == "lower":
                    ok, info = PE.certify_lower(B, eps, d, kind); return ok, f"lower certificate (degree {d}): {info}", info
                return False, "bound must be 'upper' or 'lower'", {}
            if t == "exp_min_degree":
                return check_min_degree(B, eps, kind, _degree(p["d"]))
            if t == "polymethod_rank":
                h = int(p["h"]); r = int(p["rank"])
                if not 1 <= h <= 512: return False, "h must be in [1, 512]", {}
                d = next((d for d in range(PE.D_MAX + 1) if math.comb(h + d, d) == r), None)
                if d is None: return False, f"{r} is not C({h}+d, d) for any d <= {PE.D_MAX}", {}
                ok, why, ev = check_min_degree(B, eps, kind, d)
                return ok, f"rank {r} = C({h}+{d},{d}); " + why, ev
            if t == "kv_compare":
                a, b = p["policy_a"], p["policy_b"]; n, bud = int(p["n"]), int(p["budget"])
                if a not in kv.POLICIES or b not in kv.POLICIES or a == b: return False, "unknown or identical policies", {}
                if not (64 <= n <= 1024 and 8 <= bud < n): return False, "need 64 <= n <= 1024 and 8 <= budget < n", {}
                if p.get("better") != "a": return False, "state the claim with the better policy as policy_a and better = 'a'", {}
                r = kv.compare(a, b, n, bud); ok = r["p_a_better"] < 0.05 and r["ci95"][0] > 1
                return ok, (f"20 fixed seeds: mean error {a} {r['err_a']:.4f} vs {b} {r['err_b']:.4f}, ratio {r['ratio_b_over_a']:.3f} "
                            f"(95% CI {r['ci95'][0]:.3f}-{r['ci95'][1]:.3f}), paired permutation p = {r['p_a_better']:.4f}"), r
            return False, f"unknown check type {t}", {}
        except Exception as e:
            return False, f"check not executable: {type(e).__name__}: {e}"[:300], {}

    def level(self, p): return "statistical" if p.get("typ") == "kv_compare" else "computed_rigorous"

    def consistent(self, antwort, p):
        z = antwort.get("zahl")
        if z is None: return True
        try:
            z = float(z)
            if "value" in p: v = float(S.frac(p["value"])); return abs(z - v) <= 1e-6 * max(1.0, abs(v))
            if p.get("typ") in ("exp_min_degree", "exp_degree"): return int(round(z)) == int(p["d"])
            if p.get("typ") == "optimal_gamma": return int(round(z)) == int(p["gamma"])
            if p.get("typ") == "polymethod_rank": return int(round(z)) == int(p["rank"])
        except (TypeError, ValueError): return True
        return True

    def describe(self, p):
        t = p.get("typ"); inst = lambda: f"p = {json.dumps(p.get('p'))}, q = {json.dumps(p.get('q'))}"
        err = lambda: f"{p.get('error', 'relative')} error"
        if t == "acceptance_rate": return f"For {inst()}, single-draft speculative sampling accepts with probability exactly {p['value']} (exact rational arithmetic)."
        if t == "scheme_acceptance":
            extra = f", lambda = {p['lambda']}" if p.get("rule") == "scaled" else ""
            return f"For {inst()}, rule {p['rule']} with k = {p.get('k', 1)}{extra} accepts with probability exactly {p['value']} (exact)."
        if t == "unbiased":
            return (f"For {inst()}, rule {p['rule']} (k = {p.get('k', 1)}{', lambda = ' + str(p['lambda']) if 'lambda' in p else ''}) is "
                    f"{'lossless: its output distribution equals p' if p['unbiased'] else 'NOT lossless: its output distribution differs from p'} (exact).")
        if t == "multidraft_optimal":
            return (f"For {inst()} and k = {p['k']} drafts ({p.get('mode', 'iid')}), the optimal acceptance probability over all lossless couplings is "
                    f"exactly {p['value']} (certified by an exact max-flow equal to an exact min-cut).")
        if t == "scheme_optimal":
            return (f"For {inst()} and k = {p['k']}, {p['rule']} {'attains' if p['optimal'] else 'does not attain'} the optimal lossless "
                    f"acceptance for its draft mode (exact comparison with the certified optimum).")
        if t == "optimal_gamma":
            return f"With i.i.d. acceptance alpha = {p['alpha']} and cost ratio c = {p['c']}, draft length {p['gamma']} maximises the expected speedup over all g >= 0 (exact, tail-certified)."
        if t == "exp_degree":
            if p["bound"] == "upper": return f"Some polynomial of degree {p['d']} approximates e^x on [-{p['B']}, {p['B']}] with {err()} at most {p['eps']} (rigorous interval bound)."
            return f"No polynomial of degree {p['d']} approximates e^x on [-{p['B']}, {p['B']}] with {err()} at most {p['eps']} (de la Vallee Poussin certificate, interval arithmetic)."
        if t == "exp_min_degree":
            return f"The minimal degree of a polynomial approximating e^x on [-{p['B']}, {p['B']}] with {err()} at most {p['eps']} is exactly {p['d']} (rigorous upper and lower certificates)."
        if t == "polymethod_rank":
            return (f"For head dimension h = {p['h']}, logits bounded by {p['B']} and entrywise {err()} {p['eps']}, the polynomial-method factorisation built "
                    f"from the minimal-degree approximation of e^x has rank exactly {p['rank']} (certified minimal degree).")
        if t == "kv_compare":
            return (f"On the synthetic attention model (n = {p['n']}, budget = {p['budget']}, 20 fixed seeds), KV policy {p['policy_a']} has lower mean "
                    f"relative output error than {p['policy_b']} (paired permutation test p < 0.05, bootstrap CI of the error ratio above 1).")
        return super().describe(p)

    def widerspricht(self, p, q):
        """Two passed checks that cannot both be true."""
        if not (isinstance(p, dict) and isinstance(q, dict)): return False
        same = lambda *ks: all(json.dumps(p.get(k)) == json.dumps(q.get(k)) for k in ks)
        tp, tq = p.get("typ"), q.get("typ")
        if tp == tq and "value" in p and "value" in q and same("p", "q", "rule", "k", "mode", "lambda"):
            try: return S.frac(p["value"]) != S.frac(q["value"])
            except ValueError: return False
        if tp == tq == "unbiased" and same("p", "q", "rule", "k", "lambda"): return bool(p["unbiased"]) != bool(q["unbiased"])
        if tp == tq == "scheme_optimal" and same("p", "q", "rule", "k"): return bool(p["optimal"]) != bool(q["optimal"])
        if tp == tq == "exp_min_degree" and same("B", "eps", "error"): return int(p["d"]) != int(q["d"])
        if tp == tq == "exp_degree" and same("B", "eps", "error") and p.get("bound") != q.get("bound"):
            up, lo = (p, q) if p.get("bound") == "upper" else (q, p)
            return int(lo["d"]) >= int(up["d"])
        if {tp, tq} == {"exp_min_degree", "exp_degree"} and same("B", "eps", "error"):
            m, e = (p, q) if tp == "exp_min_degree" else (q, p)
            return (e["bound"] == "upper" and int(e["d"]) < int(m["d"])) or (e["bound"] == "lower" and int(e["d"]) >= int(m["d"]))
        if tp == tq == "kv_compare" and same("n", "budget"):
            return p["policy_a"] == q["policy_b"] and p["policy_b"] == q["policy_a"]
        return False

    def selftest(self):
        p3, q3 = ["1/2", "1/4", "1/4"], ["1/5", "3/5", "1/5"]
        return [
            ({"typ": "acceptance_rate", "p": p3, "q": q3, "value": "13/20"}, True),
            ({"typ": "acceptance_rate", "p": p3, "q": q3, "value": "33/50"}, False),
            ({"typ": "acceptance_rate", "p": p3, "q": q3, "value": "13/20", "tolerance": 0.01}, False),          # rule violation
            ({"typ": "acceptance_rate", "p": ["0.5", "0.25", "0.2"], "q": q3, "value": "0.6"}, False),              # p does not sum to 1
            ({"typ": "unbiased", "p": p3, "q": q3, "rule": "standard", "unbiased": True}, True),
            ({"typ": "unbiased", "p": p3, "q": q3, "rule": "scaled", "lambda": 2, "unbiased": True}, False),
            ({"typ": "unbiased", "p": p3, "q": q3, "rule": "rrs_wor", "k": 2, "unbiased": True}, True),
            ({"typ": "scheme_acceptance", "p": p3, "q": q3, "rule": "rrs_iid", "k": 2, "value": "77/100"}, True),
            ({"typ": "multidraft_optimal", "p": p3, "q": q3, "k": 2, "mode": "iid", "value": "43/50"}, True),
            ({"typ": "multidraft_optimal", "p": p3, "q": q3, "k": 2, "mode": "iid", "value": "77/100"}, False),    # RRS value is not optimal
            ({"typ": "scheme_optimal", "p": p3, "q": q3, "k": 2, "rule": "rrs_iid", "optimal": True}, False),
            ({"typ": "optimal_gamma", "alpha": "4/5", "c": "1/20", "gamma": 8}, True),
            ({"typ": "optimal_gamma", "alpha": "4/5", "c": "1/20", "gamma": 7}, False),
            ({"typ": "exp_min_degree", "B": 1, "eps": "5.1e-4", "error": "relative", "d": 4}, True),                # E_4 = 5.030e-4
            ({"typ": "exp_min_degree", "B": 1, "eps": "4.9e-4", "error": "relative", "d": 4}, False),               # true d* = 5
            ({"typ": "exp_degree", "B": 4, "eps": "7.62e-5", "error": "relative", "bound": "upper", "d": 10}, True),   # E_10 = 7.5395e-5
            ({"typ": "exp_degree", "B": 4, "eps": "7.46e-5", "error": "relative", "bound": "upper", "d": 10}, False),
            ({"typ": "exp_degree", "B": 4, "eps": "7.46e-5", "error": "relative", "bound": "lower", "d": 10}, True),
            ({"typ": "exp_degree", "B": 4, "eps": "7.62e-5", "error": "relative", "bound": "lower", "d": 10}, False),
            # regression case for AE4 (coefficients re-rounded to 15 digits made this certificate fail): must pass
            ({"typ": "exp_degree", "B": 16, "eps": "3.32e-7", "error": "relative", "bound": "upper", "d": 30}, True),   # E_30 = 3.2847e-7
            ({"typ": "polymethod_rank", "h": 8, "B": 1, "eps": "1e-3", "error": "relative", "rank": math.comb(12, 4)}, True),
            ({"typ": "polymethod_rank", "h": 8, "B": 1, "eps": "1e-3", "error": "relative", "rank": math.comb(13, 5)}, False),
            ({"typ": "kv_compare", "policy_a": "oracle", "policy_b": "random", "n": 256, "budget": 32, "better": "a"}, True),
            ({"typ": "kv_compare", "policy_a": "random", "policy_b": "oracle", "n": 256, "budget": 32, "better": "a"}, False),
        ]


DOMAIN = AlgoEfficiencyDomain()
