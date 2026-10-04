# Verifier-Gated Discovery Lab

**Agents propose, Omnigent orchestrates, only a code verifier accepts.** Our lab turns the scientific method into an executable loop: a
planner chooses between rival experiments under a budget, researchers run them, and a domain verifier (exact rational certificates,
symbolic proofs, fixed tolerances) is the only authority that confirms a claim. A red team on a different model attacks every confirmed
claim; surprises reopen assumptions; humans approve publication through Omnigent policies. Every action is logged with input and output
ids and sealed in a hash chain.

**Result.** In one recorded Omnigent run (19 min, 1.29 USD) the lab produced 3 certified
claims and rejected 1, and found 8 new exactly certified violations of the kinetic-proofreading
bound. The 88-topology family now reads 50 proved / 11 violated / 27 open.

**Measured acceleration.** Verifier result to next decision: median 10 s (n = 4); question to certified claim:
median 63 s. Replay benchmark (10 seeds): 4.6x fewer verifier calls than random search
(95% CI 2.6 to 7.5, p = 0.003); versus attempts without feedback 1.2x, not significant.

**Trust.** On 36 answers each: Claude alone 36.1% false, Claude with Python 22.2% false, the lab
0.0% false (95% CI 0.0 to 9.7%). Blind stress test: 0 of 20 random claims accepted.

The same lab runs as an MCP server inside anyone's own Claude.
