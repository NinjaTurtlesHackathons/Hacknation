"""KV-cache compression on a synthetic attention model (statistical evidence only; the model is an explicit assumption).

Generator (all parameters explicit, no hidden data): a sequence of n tokens with head dimension h. Keys and values are Gaussian;
the first `sinks` tokens get an extra key component along a shared direction u (attention sinks); a fraction `heavy` of tokens
are heavy hitters with the same extra component of half the size; queries carry a component along u plus a recency
term (each query is correlated with the most recent keys). This mimics the qualitative patterns reported for LLM attention
(sinks, heavy hitters, locality) but is NOT a language model.

Policies keep `budget` of the first n tokens for the next m queries:
  recent       sliding window of the last `budget` tokens
  sink_recent  first 4 tokens + the last budget - 4 (StreamingLLM pattern)
  h2o          tokens with the largest accumulated attention from the n prefix queries (heavy-hitter oracle pattern),
               half of the budget reserved for the most recent tokens
  random       uniform random subset (seeded)
  oracle       top tokens by attention mass of the evaluated queries themselves (lower bound; uses future information)
Metric: mean relative L2 error of the attention output of the next m queries versus the full cache.
"""
import numpy as np

POLICIES = ("recent", "sink_recent", "h2o", "random", "oracle")
VERIFIER_SEEDS = tuple(range(1000, 1020))


def instance(n=512, h=32, m=32, sinks=4, heavy=0.03, locality=1.0, sharp=6.0, seed=0, structured=True):
    """structured=False is the negative control: no sinks, no heavy hitters, no locality, no shared query direction."""
    if not structured: sinks, heavy, locality = 0, 0.0, 0.0
    rng = np.random.default_rng(seed); N = n + m
    u = rng.normal(size=h); u /= np.linalg.norm(u)
    K = rng.normal(size=(N, h)); Vv = rng.normal(size=(N, h))
    K[:sinks] += 4.0 * u
    hh = rng.random(N) < heavy; hh[:sinks] = False; K[hh] += 2.0 * u
    Q = rng.normal(size=(N, h)) * 0.5 + (1.0 * u if structured else 0.0)
    for i in range(1, N):                                    # locality: query i leans towards the last few keys
        Q[i] += locality * K[max(0, i - 4):i].mean(0)
    return sharp * Q / np.sqrt(h), K, Vv


def _attn(q, K, V):
    z = K @ q; z -= z.max(); a = np.exp(z); a /= a.sum(); return a @ V, a


def evaluate(policy, n=512, h=32, m=32, budget=64, seed=0, **gen):
    if policy not in POLICIES: return {"fehler": f"unknown policy {policy}"}
    if not 8 <= budget < n: return {"fehler": "need 8 <= budget < n"}
    Q, K, V = instance(n, h, m, seed=seed, **gen); rng = np.random.default_rng(seed + 7)
    if policy == "recent": keep = np.arange(n - budget, n)
    elif policy == "sink_recent": keep = np.r_[np.arange(4), np.arange(n - budget + 4, n)]
    elif policy == "random": keep = np.sort(rng.choice(n, budget, replace=False))
    elif policy == "h2o":
        acc = np.zeros(n)
        for i in range(n): acc[:i + 1] += _attn(Q[i], K[:i + 1], V[:i + 1])[1]
        r = budget // 2; recent = np.arange(n - r, n); score = acc.copy(); score[recent] = -np.inf
        keep = np.sort(np.r_[np.argsort(score)[::-1][:budget - r], recent])
    else:
        mass = sum(_attn(Q[n + j], K[:n], V[:n])[1] for j in range(m)); keep = np.sort(np.argsort(mass)[::-1][:budget])
    errs = []
    for j in range(m):
        q = Q[n + j]
        full, _ = _attn(q, np.r_[K[:n], K[n:n + j + 1]], np.r_[V[:n], V[n:n + j + 1]])
        comp, _ = _attn(q, np.r_[K[keep], K[n:n + j + 1]], np.r_[V[keep], V[n:n + j + 1]])
        errs.append(np.linalg.norm(full - comp) / np.linalg.norm(full))
    return {"rel_error": float(np.mean(errs)), "kept": int(len(keep)), "note": "synthetic attention model (statistical, not an LLM)"}


def compare(policy_a, policy_b, n, budget, seeds=VERIFIER_SEEDS, structured=True):
    """Paired comparison over fixed seeds: errors of a and b, one-sided paired permutation p-value for 'a has lower error',
    and the bootstrap CI of the error ratio b/a (>1 means a is better)."""
    from asd.stats import perm_test, ratio_ci
    ea = [evaluate(policy_a, n=n, budget=budget, seed=s, structured=structured)["rel_error"] for s in seeds]
    eb = [evaluate(policy_b, n=n, budget=budget, seed=s, structured=structured)["rel_error"] for s in seeds]
    ratio, ci = ratio_ci(eb, ea)
    return {"err_a": float(np.mean(ea)), "err_b": float(np.mean(eb)), "raw_a": ea, "raw_b": eb, "p_a_better": perm_test(ea, eb), "ratio_b_over_a": ratio, "ci95": ci}


def attention_spectrum(n=256, h=16, B=4.0, seed=0, ranks=(1, 4, 16, 64)):
    """Numerical experiment: singular values of exp(Q K^T) with logits scaled to |<q,k>| <= B; relative Frobenius error of the
    best rank-r approximation (Eckart-Young) for the given ranks. Floating point (observed)."""
    rng = np.random.default_rng(seed); Q = rng.normal(size=(n, h)); K = rng.normal(size=(n, h))
    Q /= np.linalg.norm(Q, axis=1, keepdims=True); K /= np.linalg.norm(K, axis=1, keepdims=True)
    A = np.exp(B * Q @ K.T); s = np.linalg.svd(A, compute_uv=False); tot = np.sqrt((s ** 2).sum())
    return {"rel_frobenius_error": {int(r): float(np.sqrt((s[r:] ** 2).sum()) / tot) for r in ranks if r < n}, "note": "numerical"}
