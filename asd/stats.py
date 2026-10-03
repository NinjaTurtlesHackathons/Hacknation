"""Pflicht-Prüfungen 1 und 4: gepaarter Permutationstest, Bootstrap-KI, Benjamini-Hochberg."""
import numpy as np


def perm_test(a, b, B=20000, seed=1):
    """Gepaart (gleiche Seeds), einseitig: H1 'a braucht weniger Experimente als b'. Vorzeichen-Flip-Test."""
    d = np.asarray(b, float) - np.asarray(a, float); obs = d.mean()
    flips = np.random.default_rng(seed).choice([-1, 1], (B, len(d)))
    return float(((flips * d).mean(1) >= obs).mean())


def ratio_ci(num, den, B=5000, seed=0, paired=True):
    """Effekt E[num]/E[den] mit Bootstrap-95%-KI (gepaart: gleiche Seeds werden gemeinsam gezogen)."""
    num = np.asarray(num, float); den = np.asarray(den, float); rng = np.random.default_rng(seed)
    if paired:
        I = rng.integers(0, len(num), (B, len(num))); r = num[I].mean(1) / den[I].mean(1)
    else:
        r = num[rng.integers(0, len(num), (B, len(num)))].mean(1) / den[rng.integers(0, len(den), (B, len(den)))].mean(1)
    return float(num.mean() / den.mean()), [float(x) for x in np.percentile(r, [2.5, 97.5])]


def median_ci(a, B=5000, seed=0):
    a = np.asarray(a, float); rng = np.random.default_rng(seed)
    m = np.median(a[rng.integers(0, len(a), (B, len(a)))], 1)
    return float(np.median(a)), [float(x) for x in np.percentile(m, [2.5, 97.5])]


def bh(pvals, q=0.1):
    """Benjamini-Hochberg. Gibt (abgelehnt[bool], adjustierte p) zurück; m = Zahl aller übergebenen Tests."""
    p = np.asarray(pvals, float); m = len(p)
    if m == 0: return np.array([], bool), np.array([])
    o = np.argsort(p); adj = np.empty(m)
    adj[o] = np.minimum.accumulate((p[o] * m / np.arange(1, m + 1))[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    return adj <= q, adj


def first_hit_moments(n, k):
    """Exakte Momente der Position des ersten Treffers beim Ziehen ohne Zurücklegen."""
    mean = (n + 1) / (k + 1); var = k * (n + 1) * (n - k) / ((k + 1) ** 2 * (k + 2))
    return mean, var
