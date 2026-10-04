# Example session: Claude Code + probatum (unedited)

Real run on 2026-10-04: `claude -p ... --mcp-config mcp.json --allowedTools "mcp__probatum__*" --model sonnet`, server started via
`uvx --from git+https://github.com/alizema700/Daddys-Project probatum-mcp`. Raw stream: [`examples/probatum_session.jsonl`](examples/probatum_session.jsonl).

**User:** Use the probatum tools (domain proofreading). Question: can the single-stage Hopfield proofreading network (topology hopfield_n1) reach an error rate eta <= 1e-6? Follow the research_round procedure ... Report rejected claims openly with the verifier's reason.

What happens: Claude proposes two rival experiments and picks one; the verifier **confirms** the certified bound η ≥ e^(−2Δ) (symbolic proof, `computed_rigorous`) and **rejects** the counter-claim η ≤ 10⁻⁶ (exact rational evaluation gives η = 1.001688·10⁻⁴).

**Claude calls** `list_domains` {}

**probatum →**
```json
{
  "lattice": {
    "beschreibung": "Three-body power-law energy of Bravais lattices (2D/3D/4D): minimisers, sign changes, asymptotics. Numerical verifier with fixed tolerances.",
    "experimente": [
      "asymptote",
      "bain_curvature",
      "compare2d",
      "crossing2d",
      "energy2d",
      "energy3d",
      "energy_nd",
      "hessian2d",
      "minimize2d",
      "minimize_nd",
      "rect_optimum"
    ],
    "claim_typen": [
      "argmin2d",
      "argmin3d",
      "argmin_nd",
      "grenzwert",
      "koexistenz",
      "vergleich_nd",
      "vorzeichenwechsel"
    ],
    "selbsttest_bestanden": false
  },
  "proofreading": {
    "beschreibung": "Kinetic proofreading networks (Hopfield): error rate eta, dissipation sigma, speed v. Exact rational certificates and symbolic proofs.",
    "experimente": [
      "classify_family",
      "evaluate",
      "family",
      "front",
      "optimize",
      "param_names",
      "search_counterexamples"
    ],
    "claim_typen": [
      "erreichbar",
      "erreichbar_liste",
      "optimum",
      "schranke_familie",
      "untere_schranke"
    ],
    "selbsttest_bestanden": false
  }
}
```

**Claude calls** `selftest` {"domain": "proofreading"}

**Claude calls** `describe` {"domain": "proofreading"}

**probatum →**
```json
{
  "ergebnis": "PASS",
  "wahre_faelle": 7,
  "falsche_faelle": 11,
  "korrekt": 18,
  "fehlklassifiziert": []
}
```

**probatum →**
```json
{
  "kontext": "Ein Enzym unterscheidet ein richtiges Substrat R von einem falschen W. Beide durchlaufen dasselbe Markov-Netzwerk; W dissoziiert aus gebundenen Zuständen um den Faktor e^Delta schneller (Delta = ln 100, also e^-Delta = 0,01). Kennzahlen: Fehlerrate eta = J_W/J_R, Dissipation sigma = Entropieproduktion pro Produkt (kT), Geschwindigkeit v = J_R. Modellregeln: jede Kante hat eine Rückkante; lokale detaillierte Bilanz, Zyklus-Affinität nur durch Treibstoff mu je Aktivierung und mu_P je Produkt; log-Raten in [-10, 10]. Topologien: 'hopfield_n0', 'hopfield_n1', 'hopfield_n2' (lineare Kette mit n Proofreading-Stufen) oder eine eigene JSON-Spec {ungebunden: [...], gebunden: [...], kanten: [{id, von, nach, diskriminierend, fuel, produkt}]}. Bekannter Anker (Hopfield 1974): eta >= e^-(n+1)Delta im Limes unendlicher Energie und verschwindender Geschwindigkeit.",
  "experimente_doku": "Verfügbare Experimente (JSON {\"op\": ..., \"args\": {...}}):\n- param_names {topologie}: Namen der freien Parameter (log-Raten \"kante+\"/\"kante-\", dazu \"mu\", \"muP\").\n- evaluate {topologie, params: {name: log-Rate}}: eta, sigma, v numerisch.\n- optimize {topologie, sigma_max?, v_min?, starts?, seed?}: minimale Fehlerrate unter den Nebenbedingungen (Multi-Start, Kandidat, ~5-30 s).\n- front {topologie, sigmas: [...]}: optimize für mehrere sigma_max (Pareto-Front, Kandidat; teuer).\n- search_counterexamples {names: [...], eta_max}: numerische Suche nach eta < eta_max für jede genannte …
```

**Claude calls** `run_experiment` {"domain": "proofreading", "spec": {"op": "optimize", "args": {"topologie": "hopfield_n1", "starts": 24, "seed": 1}}}

**probatum →**
```json
{
  "experiment_id": "E1",
  "ergebnis": {
    "params": {
      "bind+": 5.344828547440981,
      "bind-": 9.248030416269675,
      "akt0+": -1.0382595058139483,
      "verw1+": 3.298578254045906,
      "verw1-": 5.856745430044623,
      "prod+": -7.902090479128881,
      "mu": 10.212481398007368,
      "muP": 0.0
    },
    "eta": 0.00010016883444024716,
    "sigma": 754763.539030034,
    "v": 3.702032475693331e-6,
    "feasible": true,
    "hinweis": "numerisch (Kandidat), nicht zertifiziert"
  }
}
```

**Claude:** The optimizer's minimum is eta ≈ 1.0017e-4, just above the Hopfield floor of 1e-4. Next I'll submit a certified lower bound.

**Claude calls** `submit_claim` {"domain": "proofreading", "claim": {"typ": "untere_schranke", "topologie": "hopfield_n1", "c": 1, "k": 2}, "frage": "Can hopfield_n1 reach eta <= 1e-6?"}

**probatum →**
```json
{
  "bestanden": true,
  "level": "computed_rigorous",
  "grund": "Zertifikat (b) symbolisch: eta - (1*e^(-2*Delta)) = N/D mit 90 bzw. 167 Termen, alle Koeffizienten nichtnegativ: True (0.5 s)",
  "claim_id": "proofreading-C1",
  "aussage": "Für hopfield_n1 gilt eta >= 1 * e^(-2 Delta) (D = e^Delta, G = e^mu) für alle positiven Raten und alle Treibstoff-Potentiale mu, mu_P >= 0 (Zertifikat (b): symbolischer Positivitätsbeweis, unabhängig vom Ratenbereich)."
}
```

**Claude:** Confirmed. Now I'll try to refute it with a counter-claim: that eta ≤ 1e-6 is reachable. I'll reuse the optimizer's parameters, which should fail.

**Claude calls** `challenge_claim` {"domain": "proofreading", "claim_id": "proofreading-C1", "counter_claim": {"typ": "erreichbar", "topologie": "hopfield_n1", "params": {"bind+": 5.344828547440981, "bind-": 9.248030416269675, "akt0+": -1.0382595058139483, "verw1+": 3.298578254045906, "verw1-": 5.856745430044623, "prod+": -7.902090479128881, "mu": 10.212481398007368, "muP": 0}, "eta_max": 1e-06}}

**probatum →**
```json
{
  "claim_id": "proofreading-C1",
  "status": "bestätigt",
  "gegenpruefung_bestanden": false,
  "widerspruch": false,
  "grund": "Zertifikat (a): eta = 1.001688e-04 (exakt rational); sigma in [754763.536455, 754763.536455] kT; v = 3.7020e-06"
}
```

**Claude:** **Answer: No.** The single-stage network `hopfield_n1` cannot reach eta ≤ 1e-6, and the verifier certified a lower bound of 1e-4.

1. **Selftest:** PASS (18/18 cases classified correctly).
2. **Describe:** Δ = ln 100. The Hopfield anchor for n=1 is eta ≥ e^(−2Δ) = 1e-4, which is 100 times above the 1e-6 target.
3. **Rival experiments:**
   - A was `optimize` on `hopfield_n1`.
   - B was `search_counterexamples` with `eta_max=1e-6`.
   - I chose A because it is fast and locates the floor. B's failure to find a violation would prove nothing.
4. **Run (E1):** The best numerical eta was 1.0017e-4. That used sigma ≈ 7.5e5 kT and v ≈ 3.7e-6, a very slow and very dissipative operating point. This is a candidate only, not certified.
5. **Claim `proofreading-C1`:** I claimed eta ≥ 1·e^(−2Δ) for `hopfield_n1`. The verifier accepted it (level `computed_rigorous`). Its symbolic proof shows all polynomial coefficients are non-negative. It holds for all positive rates, any fuel potential, and any rate range.
6. **Challenge:** I tried the optimizer's parameters as a counter-claim that eta ≤ 1e-6 is reachable. It failed (`gegenpruefung_bestanden: false`, no contradiction). The exact eta was 1.001688e-4, so the claim stays confirmed.
7. **Rejected claims:** None. The only failure was my own counter-claim, which was meant to fail.

**Next question:** What is the cheapest topology that gets to 1e-6? Hopfield's bound suggests n=2 (floor 1e-6), but the log-rate range [−10, 10] may keep eta above that. I would run `optimize` on `hopfield_n2`, then test whether branching topologies from `family`, such as k=2, can beat the e^(−(n+1)Δ) floor.
