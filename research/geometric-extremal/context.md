# Geometric Extremal Lab

Started 2026-10-04, Europe/Zurich. Human research director: Laurenz Thümmler (scope and ambition); autonomous execution: Codex and delegated agents. No expert endorsement is implied.

## Repository audit and scope

Main at c622004 contains the original chemistry lab only. The existing domain framework lives on `origin/algo-efficiency` at dff8d99. This isolated branch, `research/geometric-extremal`, inherits that framework; unrelated domains are not modified. No AGENTS.md is present in the checkout. Read: CLAUDE.md, README.md, docs/FRAMEWORK.md, both .claude/skills/*/SKILL.md, domain/base, selftest, new_domain, lab_loop, paper and writer. Earlier local skill copy was read to locate missing main-branch infrastructure; the remote framework is the implementation source.

Full rigorous-innovation workflow; Quant/Science audience. The user explicitly authorizes autonomous gate decisions, broad initial literature research and no cost optimization. Those instructions supersede skill defaults to ask for mode and human gate decisions and to use a cheapest-model cascade. Four concurrent slots: director plus three workers. Agents write separate owned paths, followed by waves for discovery, certification, attack and presentation.

## Mathematical model

For a closed region D and distinct points P={p_1,...,p_n}, define a(P)=min_{i<j<k}|det(p_j-p_i,p_k-p_i)|/2. Heilbronn construction questions maximize a(P), with square [0,1]^2, radius-one disk, or reference triangle x>=0,y>=0,x+y<=1. Triangle unit-area normalization is 2a(P). Free-convex normalization is a(P)/area(conv(P)). The coordinate unit, area normalization and n must accompany every comparison. A witness proves only a lower bound. Global optimality needs a separate exclusion proof.

Additional portfolio targets have their own exact model in literature/*.md. Rigid motions preserve distances and triangle areas; an affine map multiplies both triangle and hull area by |det|, preserving the convex ratio. Rational points permit exact integer determinants and domain tests. Noncollinearity is required for positive min area; duplicate points are inadmissible.

## Acceptance

Fast numeric search -> independent exact rational checker -> adversarial source/normalization audit -> published claim. Numerical tolerances never certify existence. A baseline from truncated source digits is a bracket, not an exact record. Current author repositories and recent preprints are checked before novelty claims. No statistical speedup claim is planned; chemistry-specific statistical gates are not geometric existence certificates.

## Pipeline and restart

Use existing Domain interface and asd.selftest. Source claims reside in projects/geometric_extremal/state.json; experiments/claims/gates tables feed the demo. All scripts, seeds, commands and negative attempts remain under this research directory. `STATUS.md` records next actions and owned jobs. Discovery state is saved after batches, never only at the end. No contacts or messages to external researchers are authorized.

## Initial candidate gates

18 questions (three scouts, six each); choose 4–8 based on current baseline, witness margin, evaluation speed, significance and family prospects. Reject known solutions and unverified supposed conjectures. Search success requires a certified improvement larger than source precision and numerical noise; novelty remains separately audited. Stop unchanged stagnant methods and adopt a different structure, representation or problem.
