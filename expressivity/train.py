"""One-layer recurrent models trained on group word problems (empirical validation, module B).

Architectures (one layer, transitions depend on the current token only, readout = MLP of the full state):
  diag_pos  h_t = a_t * h_{t-1} + b_t, a_t = sigmoid(.) in (0, 1)            (Mamba-like, 64-dim state)
  diag_pm   same with a_t = tanh(.) in (-1, 1)                               (negative eigenvalues allowed)
  hhK       DeltaNet / DeltaProduct: S <- S (I - beta k k^T) + beta v k^T, K times per token with separate (k, beta, v);
            beta = 2 sigmoid(.) in (0, 2), ||k|| = 1; S in R^{dv x dk}, dk = dv = 8 (64-dim state)
  lstm      LSTM with 64 hidden units (nonlinear positive control)
An ensemble of E independent members (one per seed) is trained in one process: every parameter has a leading member axis, each
member has its own initialisation (torch generator seeded with the seed) and its own data stream (numpy generator seeded with the
seed); Adam is elementwise and gradient clipping is per member, so members do not interact.
Evaluation uses fresh sequences from generators seeded with 900000 + seed (never used in training).
"""
import argparse, json, math, os, time
import numpy as np
import torch
import torch.nn.functional as Fnn


def task_tables(G, S):
    idx = {g: i for i, g in enumerate(G.elements)}
    L = np.array([[idx[tuple(s[x] for x in g)] for g in G.elements] for s in S], dtype=np.int64)   # L[letter, g] = index of s*g
    return L, idx[G.e]


def make_batch(rng, L, e, B, T):
    tok = rng.integers(0, L.shape[0], size=(B, T))
    tgt = np.empty((B, T), dtype=np.int64); g = np.full(B, e, dtype=np.int64)
    for t in range(T):
        g = L[tok[:, t], g]; tgt[:, t] = g
    return tok, tgt


def _p(E, *shape, gen, scale):
    return torch.nn.Parameter(torch.randn(E, *shape, generator=gen) * scale)


class Ensemble(torch.nn.Module):
    def __init__(self, arch, E, V, C, seeds, D=64, dk=8, dv=8, hid=128, beta_bias=0.0, beta_mode="sigmoid"):
        super().__init__()
        self.arch, self.E, self.V, self.C, self.beta_mode = arch, E, V, C, beta_mode
        gens = [torch.Generator().manual_seed(int(s)) for s in seeds]
        def P(*shape, scale):                                  # per-member initialisation from the member's own generator
            return torch.nn.Parameter(torch.stack([torch.randn(*shape, generator=g) * scale for g in gens]))
        self.emb = P(V, D, scale=1.0)
        if arch.startswith("hh"):
            K = int(arch[2:]); self.K, self.dk, self.dv = K, dk, dv
            self.Wk = P(K, D, dk, scale=D ** -0.5); self.Wv = P(K, D, dv, scale=D ** -0.5)
            self.wb = P(K, D, scale=D ** -0.5); self.bb = P(K, scale=0.0)
            with torch.no_grad(): self.bb += beta_bias              # beta_bias > 0 starts near reflections (beta -> 2) instead of projections (beta = 1)
            sdim = dk * dv
        elif arch in ("diag_pos", "diag_pm"):
            self.Wa = P(D, 64, scale=D ** -0.5); self.ba = P(64, scale=0.0); self.Wb = P(D, 64, scale=D ** -0.5)
            if arch == "diag_pos":
                with torch.no_grad(): self.ba += 2.0                # start near memory (a ~ 0.88)
            sdim = 64
        elif arch == "lstm":
            self.Wx = P(D, 256, scale=D ** -0.5); self.Wh = P(64, 256, scale=64 ** -0.5); self.bl = P(256, scale=0.0)
            with torch.no_grad(): self.bl[:, 64:128] += 1.0         # forget-gate bias
            sdim = 64
        else:
            raise ValueError(arch)
        self.W1 = P(sdim, hid, scale=sdim ** -0.5); self.b1 = P(hid, scale=0.0)
        self.W2 = P(hid, C, scale=hid ** -0.5); self.b2 = P(C, scale=0.0)

    def readout(self, s):                                      # s: (E, B, sdim)
        h = torch.relu(torch.einsum("ebi,eih->ebh", s, self.W1) + self.b1[:, None])
        return torch.einsum("ebh,ehc->ebc", h, self.W2) + self.b2[:, None]

    def forward(self, tok, keep_logits=True):
        """tok: (E, B, T) long. Returns logits (E, B, T, C)."""
        E, B, T = tok.shape
        x = torch.gather(self.emb, 1, tok.reshape(E, B * T, 1).expand(E, B * T, self.emb.shape[-1])).reshape(E, B, T, -1)
        outs = []
        if self.arch.startswith("hh"):
            k = Fnn.normalize(torch.einsum("ebtd,ejdk->ebtjk", x, self.Wk), dim=-1)
            v = torch.einsum("ebtd,ejdv->ebtjv", x, self.Wv)
            z = torch.einsum("ebtd,ejd->ebtj", x, self.wb) + self.bb[:, None, None]
            # sigmoid: beta in (0, 2), never an exact reflection; clamp: beta = 2 min(1, 1.25 sigmoid(z)) reaches exactly 2
            if self.beta_mode == "sigmoid": beta = 2 * torch.sigmoid(z)
            elif self.beta_mode == "clamp": beta = 2 * torch.clamp(1.25 * torch.sigmoid(z), max=1.0)
            else: beta = 2 * torch.clamp(1.5 * torch.sigmoid(z) - 0.25, 0.0, 1.0)     # "clamp2": reaches exactly 0 (identity) and exactly 2 (reflection)
            S = x.new_zeros(E, B, self.dv, self.dk)
            for t in range(T):
                for j in range(self.K):
                    kk = k[:, :, t, j]; Sk = torch.einsum("ebvk,ebk->ebv", S, kk)
                    S = S - beta[:, :, t, j, None, None] * (Sk - v[:, :, t, j])[..., None] * kk[:, :, None, :]
                outs.append(self.readout(S.reshape(E, B, -1)))
        elif self.arch in ("diag_pos", "diag_pm"):
            pre = torch.einsum("ebtd,edh->ebth", x, self.Wa) + self.ba[:, None, None]
            a = torch.sigmoid(pre) if self.arch == "diag_pos" else torch.tanh(pre)
            b = torch.einsum("ebtd,edh->ebth", x, self.Wb)
            h = x.new_zeros(E, B, 64)
            for t in range(T):
                h = a[:, :, t] * h + b[:, :, t]; outs.append(self.readout(h))
        else:
            gx = torch.einsum("ebtd,edg->ebtg", x, self.Wx) + self.bl[:, None, None]
            h = x.new_zeros(E, B, 64); c = x.new_zeros(E, B, 64)
            for t in range(T):
                g = gx[:, :, t] + torch.einsum("ebh,ehg->ebg", h, self.Wh)
                i, f, o, u = g.split(64, dim=-1)
                c = torch.sigmoid(f) * c + torch.sigmoid(i) * torch.tanh(u); h = torch.sigmoid(o) * torch.tanh(c)
                outs.append(self.readout(h))
        return torch.stack(outs, dim=2)


def clip_per_member(model, max_norm=1.0):
    sq = None
    for p in model.parameters():
        if p.grad is None: continue
        s = p.grad.reshape(p.shape[0], -1).pow(2).sum(1); sq = s if sq is None else sq + s
    scale = (max_norm / (sq.sqrt() + 1e-6)).clamp(max=1.0)
    for p in model.parameters():
        if p.grad is not None: p.grad.mul_(scale.view(-1, *([1] * (p.grad.dim() - 1))))


@torch.no_grad()
def evaluate(model, L, e, seeds, T, n=512, window=None, bs=256, device="cpu"):
    """Mean token accuracy per member on positions window = (lo, hi) (1-based, inclusive) of fresh length-T sequences."""
    lo, hi = window or (1, T); E = len(seeds); correct = np.zeros(E); total = 0
    rngs = [np.random.default_rng(900000 + int(s)) for s in seeds]
    for start in range(0, n, bs):
        b = min(bs, n - start)
        batch = [make_batch(r, L, e, b, T) for r in rngs]
        tok = torch.as_tensor(np.stack([x[0] for x in batch])).to(device); tgt = torch.as_tensor(np.stack([x[1] for x in batch])).to(device)
        pred = model(tok).argmax(-1)
        correct += (pred[:, :, lo - 1:hi] == tgt[:, :, lo - 1:hi]).float().mean(dim=(1, 2)).cpu().numpy() * b
        total += b
    return (correct / total).tolist()


def train_ensemble(arch, G, S, seeds, steps=4000, T=64, B=64, lr=2e-3, log=None, evals=((64, (1, 64)), (256, (129, 256)), (512, (449, 512))),
                   beta_bias=0.0, curriculum=False, beta_mode="sigmoid", T_final=None, device="cpu"):
    torch.manual_seed(0)
    L, e = task_tables(G, S); E = len(seeds)
    model = Ensemble(arch, E, len(S), G.order, seeds, beta_bias=beta_bias, beta_mode=beta_mode).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    warm = 200
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda i: min(1.0, (i + 1) / warm) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * min(i, steps) / steps))))
    rngs = [np.random.default_rng(int(s)) for s in seeds]; t0 = time.time(); losses = []
    for it in range(steps):
        Tc = min(T, 8 * 2 ** int(4 * it / steps)) if curriculum else T     # curriculum: 8, 16, 32, 64 in quarters
        if T_final and it >= int(0.85 * steps): Tc = T_final                # optional final stage at a longer length
        batch = [make_batch(r, L, e, B, Tc) for r in rngs]
        tok = torch.as_tensor(np.stack([x[0] for x in batch])).to(device); tgt = torch.as_tensor(np.stack([x[1] for x in batch])).to(device)
        logits = model(tok)
        loss_m = Fnn.cross_entropy(logits.reshape(-1, G.order), tgt.reshape(-1), reduction="none").reshape(E, -1).mean(1)
        opt.zero_grad(); loss_m.sum().backward(); clip_per_member(model); opt.step(); sched.step()
        if it % 500 == 0 or it == steps - 1:
            losses.append([round(float(x), 4) for x in loss_m.detach().cpu()])
            if log: log(f"{arch} {G.name} it {it} loss median {np.median(losses[-1]):.4f} ({time.time() - t0:.0f}s)")
    res = {"arch": arch, "group": G.name, "seeds": [int(s) for s in seeds], "steps": steps, "train_T": T, "batch": B, "lr": lr,
           "beta_bias": beta_bias, "curriculum": curriculum, "beta_mode": beta_mode, "T_final": T_final,
           "loss_trace": losses, "sec": round(time.time() - t0, 1)}
    for Tm, w in evals:
        res[f"acc_T{Tm}_pos{w[0]}-{w[1]}"] = [round(a, 5) for a in evaluate(model, L, e, seeds, Tm, window=w, device=device)]
    res["device"] = device
    return res


def train_quick(arch, G, S, steps=800):
    """For the lab's agents: one member, train length 32, eval at 32 and 128 (observed only)."""
    r = train_ensemble(arch, G, S, [int(time.time()) % 100000 + 500000], steps=steps, T=32, B=64,
                       evals=((32, (1, 32)), (128, (65, 128))))
    return {"acc_len32": r["acc_T32_pos1-32"][0], "acc_len128_pos65-128": r["acc_T128_pos65-128"][0], "steps": steps,
            "hinweis": "single seed, observed, noisy"}


if __name__ == "__main__":
    from .groups import get_group, alphabet
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", required=True); ap.add_argument("--group", required=True); ap.add_argument("--alphabet", default="all")
    ap.add_argument("--seeds", default="1000-1019"); ap.add_argument("--steps", type=int, default=4000); ap.add_argument("--out", required=True)
    ap.add_argument("--random-targets", action="store_true", help="negative control: targets are replaced by i.i.d. uniform labels")
    ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--beta-bias", type=float, default=0.0); ap.add_argument("--curriculum", action="store_true")
    ap.add_argument("--beta-mode", default="sigmoid", choices=["sigmoid", "clamp", "clamp2"]); ap.add_argument("--T-final", type=int, default=None)
    a = ap.parse_args()
    torch.set_num_threads(1)
    lo, hi = map(int, a.seeds.split("-")); seeds = list(range(lo, hi + 1))
    G = get_group(a.group); S = alphabet(G, a.alphabet)
    if a.random_targets:
        _orig = make_batch
        def make_batch(rng, L, e, B, T):                        # noqa: F811  (negative control)
            tok, _ = _orig(rng, L, e, B, T); return tok, rng.integers(0, L.shape[1], size=(B, T))
        globals()["make_batch"] = make_batch
    r = train_ensemble(a.arch, G, S, seeds, steps=a.steps, lr=a.lr, beta_bias=a.beta_bias, curriculum=a.curriculum, beta_mode=a.beta_mode, T_final=a.T_final, log=lambda m: print(m, flush=True))
    r.update(alphabet=a.alphabet, random_targets=a.random_targets)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); json.dump(r, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in r.items() if k.startswith("acc")}))
