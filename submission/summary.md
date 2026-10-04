# Verifier-Gated Discovery Lab

**Agents propose, Omnigent orchestrates, only a code verifier accepts.** Our lab turns the scientific method into an executable loop: a
planner chooses between rival experiments under a budget, researchers run them, and a domain verifier (exact rational certificates,
symbolic proofs, fixed tolerances) is the only authority that confirms a claim. A red team on a different model attacks every confirmed
claim; surprises reopen assumptions; humans approve publication through Omnigent policies. Every action is logged with input and output
ids and sealed in a hash chain.

**Result.** In the first recorded Omnigent run (6 min, 1.01 USD) the lab produced 3 certified
claims and rejected 2. Across 2 recorded runs the lab found 11 new exactly
certified violations of the kinetic-proofreading bound. The 88-topology family now reads 50 proved / 14 violated / 24 open.

**Measured acceleration.** Verifier result to next decision: median 24 s (n = 4); question to certified claim:
median 234 s (one run, small n). Preregistered replay (16 paired seeds):
the lab needs 2.38 verifier calls on average, a hand-written heuristic 7.94, random proposals 11.31.
That is 3.34x fewer calls than the strong heuristic (95% CI 2.81 to 4.16, p = 1.5e-05) and 4.76x fewer than random (95% CI 2.92 to 7.23, p = 0.00017);
versus the same agents without verifier feedback 1.13x, not significant.

**Trust.** On 36 answers each: Claude alone 36.1% false, Claude with Python 22.2% false, the lab
0.0% false (95% CI 0.0 to 9.7%). Caveat: 12 questions from one paper, a small home-field sample. Blind stress test: 0 of 20 random claims accepted.

The same lab runs as an MCP server inside anyone's own Claude.
