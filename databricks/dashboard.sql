-- Databricks SQL dashboard over the exported tables (catalog/schema as passed to asd.databricks_export, default main.probatum).

-- 1. Measured acceleration: verifier calls to the first hit, per condition (paired seeds)
SELECT policy AS condition, COUNT(*) AS seeds, AVG(step) AS mean_calls, PERCENTILE(step, 0.5) AS median_calls, AVG(y) AS hit_rate
FROM main.probatum.experiments GROUP BY policy ORDER BY mean_calls;

-- 2. Per-seed comparison lab vs. heuristic (same seed in both columns)
SELECT l.seed, l.step AS lab_calls, h.step AS heuristic_calls
FROM main.probatum.experiments l JOIN main.probatum.experiments h ON l.seed = h.seed AND h.policy = 'HEURISTIK'
WHERE l.policy = 'LAB' ORDER BY l.seed;

-- 3. Claims: every confirmed claim with its effective red-team votes
SELECT claim_id, project, level, status, red_team_effective, red_team_contradictions, text FROM main.probatum.claims ORDER BY claim_id;

-- 4. Policy decisions per run (what the guardrails stopped)
SELECT run, gate, decision, COUNT(*) AS n FROM main.probatum.gates GROUP BY run, gate, decision ORDER BY run, n DESC;

-- 5. Ledger: agent activity over time, with the hash-chain link of every line
SELECT run, ts, agent, command, duration_s, chain_hash FROM main.probatum.ledger ORDER BY run, line;

-- 6. Frozen numbers used in README, paper and video
SELECT key, value FROM main.probatum.frozen WHERE key LIKE 'replay.tests.%' OR key LIKE 'flaggschiff.%' ORDER BY key;
