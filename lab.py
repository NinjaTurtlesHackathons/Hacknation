"""Framework-Selbsttest: Labor-API mit versteckter Ground Truth, Strategien, Metrik N_pi, Negativkontrolle.
Aufruf: python lab.py [seeds=20] [budget=400]
"""
import sys, json, time, numpy as np, pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as C
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import norm

FACT = ["base", "ligand", "aryl_halide", "additive"]

def load():
    d = pd.read_csv("rxnpredict/data_table.csv").dropna(subset=FACT)
    d = d.groupby(FACT, as_index=False)["yield"].mean()          # Duplikate mitteln (Leakage-Schutz)
    X = pd.get_dummies(d[FACT]).to_numpy(float)
    return X, d["yield"].to_numpy(float), d

class Lab:
    """Einziger Zugang zu f. Jeder Aufruf wird geloggt (Axiom c: kein Leck)."""
    def __init__(self, y): self._y = y; self.log = []
    def run(self, i): self.log.append(int(i)); return float(self._y[i])

def ei(mu, sd, best, xi=0.01):
    sd = np.maximum(sd, 1e-9); z = (mu - best - xi) / sd
    return (mu - best - xi) * norm.cdf(z) + sd * norm.pdf(z)

def policy_random(X, lab, rng, budget, hit):
    for t, i in enumerate(rng.permutation(len(X))[:budget], 1):
        lab.run(i)
        if hit[i]: return t
    return budget + 1

def policy_model(kind):
    def p(X, lab, rng, budget, hit, n0=5):
        n = len(X); seen = list(rng.choice(n, n0, replace=False)); ys = []
        for t, i in enumerate(seen, 1):
            ys.append(lab.run(i))
            if hit[i]: return t
        mask = np.ones(n, bool); mask[seen] = False; gp = None
        for t in range(n0 + 1, budget + 1):
            Xs, Y = X[seen], np.array(ys); Yn = (Y - Y.mean()) / (Y.std() + 1e-9)
            if kind == "gp":
                if gp is None or t % 10 == 0:
                    gp = GaussianProcessRegressor(C(1.0) * Matern(length_scale=3.0, nu=2.5) + WhiteKernel(0.1),
                                                  normalize_y=False, n_restarts_optimizer=0, random_state=0).fit(Xs, Yn)
                    k = gp.kernel_
                else:
                    gp = GaussianProcessRegressor(k, optimizer=None).fit(Xs, Yn)
                mu, sd = gp.predict(X, return_std=True)
            else:  # rf: Unsicherheit = Streuung der Bäume
                rf = RandomForestRegressor(100, min_samples_leaf=2, random_state=int(rng.integers(1e9)), n_jobs=-1).fit(Xs, Yn)
                P = np.stack([e.predict(X) for e in rf.estimators_]); mu, sd = P.mean(0), P.std(0)
            a = ei(mu, sd, Yn.max()); a[~mask] = -np.inf; i = int(np.argmax(a))
            seen.append(i); mask[i] = False; ys.append(lab.run(i))
            if hit[i]: return t
        return budget + 1
    return p

def experiment(y, policies, seeds, budget, q=0.01):
    k = max(1, int(round(q * len(y)))); thr = np.sort(y)[-k]; hit = y >= thr; k = int(hit.sum())
    res = {name: [] for name in policies}
    for s in range(seeds):
        for name, pol in policies.items():
            lab = Lab(y); rng = np.random.default_rng(1000 + s)
            N = pol(X, lab, rng, budget, hit)
            assert len(lab.log) == min(N, budget) or N == budget + 1   # Leck-Prüfung: N Aufrufe = N Experimente
            res[name].append(N)
    return k, res

def boot_ci(a, b=None, B=5000, rng=np.random.default_rng(0)):
    a = np.asarray(a, float)
    if b is None:
        m = [np.median(rng.choice(a, len(a))) for _ in range(B)]; return np.median(a), np.percentile(m, [2.5, 97.5])
    b = np.asarray(b, float); r = [np.mean(rng.choice(a, len(a))) / np.mean(rng.choice(b, len(b))) for _ in range(B)]
    return np.mean(a) / np.mean(b), np.percentile(r, [2.5, 97.5])

def perm_test(a, b, B=20000, rng=np.random.default_rng(1)):  # gepaart (gleiche Seeds), einseitig: a < b
    d = np.asarray(b, float) - np.asarray(a, float); obs = d.mean()
    flips = rng.choice([-1, 1], (B, len(d))); return float(((flips * d).mean(1) >= obs).mean())

if __name__ == "__main__":
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20; budget = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    X, y, d = load(); n = len(y)
    pols = {"random": policy_random, "rf_ei": policy_model("rf"), "gp_ei": policy_model("gp")}
    out = {"n": n, "seeds": seeds, "budget": budget}
    for label, yy in [("echt", y), ("negativkontrolle_vertauscht", np.random.default_rng(7).permutation(y))]:
        t0 = time.time(); k, res = experiment(yy, pols, seeds, budget)
        theory = (n + 1) / (k + 1)
        summ = {"k": k, "E_random_theorie": round(theory, 1), "sek": round(time.time() - t0)}
        for name, r in res.items():
            med, ci = boot_ci(r); summ[name] = {"mean": round(float(np.mean(r)), 1), "median": float(med), "ci95_median": [float(c) for c in ci], "raw": r}
        for name in ["rf_ei", "gp_ei"]:
            sp, ci = boot_ci(res["random"], res[name]); summ[f"speedup_{name}_vs_random"] = {"wert": round(float(sp), 2), "ci95": [round(float(c), 2) for c in ci],
                                                                                         "p_perm": perm_test(res[name], res["random"])}
        out[label] = summ; print(label, json.dumps({k2: v for k2, v in summ.items() if k2 != "raw"}, default=str)[:900], flush=True)
    json.dump(out, open("results_selftest.json", "w"), indent=1, default=str)
