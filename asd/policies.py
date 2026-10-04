"""Policies: random | gp_ei | hybrid | hybrid_neutral. Schnittstelle: propose(history, rng) -> int.

gp_ei entspricht exakt `lab.py` (gleiche Zufallszahlen, gleicher Kernel, Refit alle 10 Schritte).
hybrid = gp_ei mit KI-Vorwissen als Mittelwertfunktion: mu(x) = a * m(x) + GP(Residuen).
Das Gewicht a wird bei jedem Schritt aus den bisherigen Messungen geschätzt (Ridge zu a = 1 hin),
eine falsche Hypothese verliert also automatisch an Einfluss. Die KI sieht dabei nie Ausbeuten.
"""
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as C

N0 = 5          # zufällige Startexperimente (prereg: wie bei gp_ei)
LAMBDA = 5.0    # Stärke des Vorwissens für a, gemessen in "Pseudo-Experimenten"


def ei(mu, sd, best, xi=0.01):
    sd = np.maximum(sd, 1e-9); z = (mu - best - xi) / sd
    return (mu - best - xi) * norm.cdf(z) + sd * norm.pdf(z)


class Policy:
    name = "base"
    def propose(self, history, rng) -> int: raise NotImplementedError


class RandomPolicy(Policy):
    name = "random"
    def __init__(self, n): self.n = n; self.order = None
    def propose(self, history, rng):
        if self.order is None: self.order = rng.permutation(self.n)
        return int(self.order[len(history)])


class GPEI(Policy):
    name = "gp_ei"
    def __init__(self, X, prior=None, name=None):
        self.X = X; self.n = len(X); self.start = None; self.gp = None; self.kernel = None
        self.alpha_trace = []
        if name: self.name = name
        if prior is None: self.m = None
        else:
            m = np.asarray(prior, float); s = m.std()
            self.m = (m - m.mean()) / s if s > 0 else np.zeros_like(m)

    def propose(self, history, rng):
        if self.start is None: self.start = list(rng.choice(self.n, N0, replace=False))
        t = len(history) + 1
        if t <= N0: return int(self.start[t - 1])
        idx = np.array([i for i, _ in history]); Y = np.array([y for _, y in history])
        Yn = (Y - Y.mean()) / (Y.std() + 1e-9)
        if self.m is None: a = 0.0; prior_all = 0.0
        else:
            ms = self.m[idx]; a = float(np.clip((ms @ Yn + LAMBDA) / (ms @ ms + LAMBDA), 0.0, 3.0))
            prior_all = a * self.m
        self.alpha_trace.append(a)
        R = Yn - (a * self.m[idx] if self.m is not None else 0.0)
        Xs = self.X[idx]
        if self.gp is None or t % 10 == 0:
            self.gp = GaussianProcessRegressor(C(1.0) * Matern(length_scale=3.0, nu=2.5) + WhiteKernel(0.1),
                                               normalize_y=False, n_restarts_optimizer=0, random_state=0).fit(Xs, R)
            self.kernel = self.gp.kernel_
        else:
            self.gp = GaussianProcessRegressor(self.kernel, optimizer=None).fit(Xs, R)
        mu, sd = self.gp.predict(self.X, return_std=True)
        acq = ei(mu + prior_all, sd, Yn.max()); acq[idx] = -np.inf
        return int(np.argmax(acq))


def make_policy(name, ds, hyps=None):
    """hyps: {'named': [...], 'neutral': [...]} aus asd.hypotheses.load_hypotheses."""
    from .data import design_keys
    from .hypotheses import prior_mean
    if name == "random": return RandomPolicy(ds.n)
    if name == "gp_ei": return GPEI(ds.X)
    if name in ("hybrid", "hybrid_neutral", "hybrid_lit"):
        view = {"hybrid": "named", "hybrid_neutral": "neutral", "hybrid_lit": "literature"}[name]
        keys = design_keys(ds, "neutral" if view == "neutral" else "named")
        return GPEI(ds.X, prior=prior_mean(hyps[view], keys), name=name)
    raise ValueError(name)
