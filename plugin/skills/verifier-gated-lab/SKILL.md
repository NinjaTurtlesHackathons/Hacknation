---
name: verifier-gated-lab
description: "Use the probatum MCP tools to do verifier-gated research: propose experiments and typed claims, let probatum's code verifier decide, red-team confirmed claims, and write up only what was confirmed. Use when the user wants to find, test or verify a quantitative scientific statement in a probatum domain (lattice energies, kinetic proofreading), or asks to check their own result."
---

# Verifier-gated research with probatum

You are the researcher; **probatum is the only authority that accepts a result.** Never present a statement as a result unless
`submit_claim` returned `"bestanden": true`. A rejected claim is a result too: report it with the verifier's reason.

## Workflow (one round)
1. `list_domains`, then `selftest(domain)` once per session (all other tools refuse until it passes), then `describe(domain)`.
2. Propose **two rival experiments** (e.g. broad scan vs. few precise points), with cost (time / verifier calls) and expected information
   gain. Choose one and say why.
3. `run_experiment(domain, {"op": ..., "args": {...}})`. Quote the experiment id with every number you use.
4. Write ONE typed claim exactly as strong as the evidence (field names from `describe`). `submit_claim(domain, claim, frage=...)`.
   - Do not add tolerance fields: tolerances belong to the verifier and are removed (`toleranz_ignoriert`).
   - Unknown fields are rejected. Numerical claims are "observed"; only `computed_rigorous` / `proved_lean` may be called a theorem.
5. Try to break it: `challenge_claim(domain, claim_id, counter_claim)` with a claim that would pass if the original were false.
6. Name the next question and why.

## Writing up
`build_paper(domain, title, authors)` returns the confirmed claims, rejected attempts and rules. Every number must come from a listed
claim (cite its claim_id); report rejected and contested claims in a "Negative results" section. Use the prompt `research_round` for a
guided round and `verify_my_result` to check a user's own statement.
