# Quiver representations beyond Dynkin type (domain `quivers`)

This paper was produced with the Verifier-Gated Discovery Lab
([alizema700/Daddys-Project](https://github.com/alizema700/Daddys-Project) at `7fe7dbe`; the framework core is copied into `asd/`).
Agents may only propose. A statement counts as true only after `domain.check()` confirms it in exact arithmetic.

| File | Contents |
|---|---|
| `results.tex` / `results.pdf` | **Results ledger, written before the paper writer ran and without it**: definitions, Gabriel, Kac, all theorems and propositions with proofs and/or verification, plus an appendix listing every checked claim (statement, verifier reason, red team) |
| `results.json` | the same claims as raw data (verifier input `pruefung`, reason, red team), plus literature |
| `paper.md` / `paper.tex` / `paper.pdf` | paper from `asd.paper` (LLM writer with hallucination gate; result: 0 violations, 0 sentences removed) |
| `state.json`, `runde1..6.json`, `lab_report.md`, `decisions.md` | lab state, rounds, report, decisions (including what was not computed) |
| `prereg.md` | preregistration F1–F5 plus dated addendum F6 (committed before each run) |
| `run_lab.py`, `make_results.py`, `paper_hinweise.md` | lab run, ledger generator, outline notes for the paper writer |
| `../../asd/domains/quivers.py`, `quivers_domain.py` | computation core and verifier (self-test 39/39) |

## Reproducing

```bash
pip install sympy                                  # everything else is the Python standard library
python -m asd.selftest quivers                     # verifier self-test: 39/39
python projects/quivers/run_lab.py                 # 6 rounds, 82 claims (~15 min, Crossref access needed for the literature)
python projects/quivers/make_results.py            # results.tex / results.json
python -m asd.recheck quivers                      # recheck every claim
python -m asd.paper --domain quivers --sprache en --hinweise projects/quivers/paper_hinweise.md \
  --titel "Indecomposable representations of non-Dynkin quivers: stars, cycles and Kac polynomials" \
  --autoren "Verifier-Gated Discovery Lab" --affiliation "Hack-Nation, Challenge 3"   # needs `claude` CLI; responses are cached in cache/llm (not committed)
```

## Main results

- **Stars $S_n$, dimension vector $(2;1^n)$.** A representation is indecomposable iff all $n$ vectors are non-zero and span at least 3 distinct lines.
  Isoclasses are $\mathrm{PGL}_2$-orbits of point configurations in $\mathbb P^1$, and
  $A_{(2;1^n)}(q)=\frac{(q+1)^{n-1}-1-(2^{n-1}-1)q}{q(q-1)}$, for example $q+4$, $q^2+5q+11$, $q^3+6q^2+16q+26$.
  The proof is in `results.tex`. The criterion was checked exhaustively for $(n,p)$ = (4,2), (4,3), (5,2), (5,3), (6,2), (7,2), and the polynomial for $n=4..8$ at deg+2 primes.
- **Four subspace problem ($\widetilde D_4$).** $\delta=(2;1,1,1,1)$. The family $V_t$ of lines $(1,0),(0,1),(1,1),(1,t)$ consists of pairwise
  non-isomorphic bricks. Together with 6 configurations having exactly one coinciding pair of lines, this gives complete lists over $\mathbb F_2,\mathbb F_3,\mathbb F_5$; $A_\delta=q+4$.
- **Wild stars.** $1-q(2k;k^5)=1+k^2$, so the number of parameters is unbounded.
- **3- and 4-cycles.** For the oriented cycle the indecomposables are strings plus bands; this was checked exhaustively for $\beta\le(2,2,2)$ and $\beta\le(2,2,2,2)$.
  $A_\delta=q+n-1$ for every orientation. The counts for $2\delta$ are consistent with $A_{2\delta}=A_\delta$.

All results are reproductions of classical theory (Gabriel, Kac, Nazarova, Ringel). No novelty is claimed.
