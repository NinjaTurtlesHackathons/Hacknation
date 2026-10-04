# Evidence (rigorous-innovation section 8; every status computed by code)

Full scout table with 65 sources: `scout_evidence.md`. Code-computed status of every entry: `results/citations.tsv`
(`scripts/verify_evidence.py`: title similarity >= 0.9 against arXiv/Crossref AND the quote found verbatim in the abstract fetched by
the script). Result: 56 VERIFIED, 7 VERIFIED-ID (Crossref has no abstract; title only, no quote used), 2 VERIFIED-ID with the quote
UNVERIFIED (arXiv:2503.03961, arXiv:2609.12259: the scout's quote was not found verbatim, so it is not used anywhere).
Full-text statements of the closest prior work: `results/body_quotes.json` (`scripts/body_quotes.py`, quote found verbatim in the arXiv
HTML; 6 of 6 verified).

## Key sources

| ID | First author, year | Title | Verbatim quote (abstract unless marked) | Used for | Status |
|---|---|---|---|---|---|
| arXiv:2207.00729 | Merrill, 2022 | The Parallelism Tradeoff: Limitations of Log-Precision Transformers | "We prove that transformers whose arithmetic precision is logarithmic in the number of input tokens (and whose feedforward nets are computable using space linear in their input) can be simulated by constant-depth logspace-uniform threshold circuits." | Transformers in TC0 | VERIFIED |
| arXiv:2404.08819 | Merrill, 2024 | The Illusion of State in State-Space Models | "SSMs cannot express computation outside the complexity class $\mathsf{TC}^0$. In particular, this means they cannot solve simple state-tracking problems like permutation composition." | SSMs in TC0 | VERIFIED |
| doi:10.1016/0022-0000(89)90037-8 | Barrington, 1989 | Bounded-width polynomial-size branching programs recognize exactly those languages in NC1 | (Crossref has no abstract) | non-solvable word problems NC1-complete | VERIFIED-ID |
| arXiv:2411.12537 | Grazzi, 2024 | Unlocking State-Tracking in Linear RNNs Through Negative Eigenvalues | "We prove that finite precision LRNNs with state-transition matrices having only positive eigenvalues cannot solve parity, while non-triangular matrices are needed to count modulo $3$." Full text: "every n × n orthogonal matrix can be written as a product of n reflections, due to the Cartan–Dieudonné Theorem" | negative eigenvalues; constructions only | VERIFIED (+ body quote) |
| arXiv:2502.10297 | Siems, 2025 | DeltaProduct: Improving State-Tracking in Linear RNNs via Householder Products | Full text: "Unexpectedly, S 4 and A 5 can extrapolate robustly using only n h = 2 despite the theorem suggesting 3 and 4, respectively." | the observation our law explains | VERIFIED (+ body quote) |
| arXiv:2503.14456 | Peng, 2025 | RWKV-7 "Goose" with Expressive Dynamic State Evolution | "We show that RWKV-7 can perform state tracking and recognize all regular languages ..." Full text: "RWKV-7 can, by Lemma 2 , solve the problem of tracking swaps on five elements." | S5 with swap inputs in one layer (alphabet dependence) | VERIFIED (+ body quote) |
| arXiv:2405.17394 | Sarrof, 2024 | The Expressive Capacity of State Space Models: A Formal Language Perspective | "In star-free state tracking, SSMs implement straightforward and exact solutions to problems that transformers struggle to represent exactly." | diagonal SSMs, star-free | VERIFIED |
| arXiv:2603.01959 | Shakerinava, 2026 | The Expressive Limits of Diagonal SSMs for State-Tracking | "We show that single-layer DCD SSMs cannot express state-tracking of any non-Abelian group at finite precision." | consistent with our L5 | VERIFIED |
| arXiv:2609.18966 | Howe, 2026 | The Automaton Underneath ... | Full text: "the minimal n h that length-generalizes equals the maximal generator reflection length rank ⁡ ( I − P ) in the representation pinned by the task format (parity 1, S 4 3, A 5 / S 5 4)"; formats: "S 4 (transposition + 4-cycle), A 5 (3-cycle + 5-cycle; all-even)" | closest prior work (empirical law) | VERIFIED (+ body quotes) |
| arXiv:2210.10749 | Liu, 2022 | Transformers Learn Shortcuts to Automata | "We find that polynomial-sized $O(\log T)$-depth solutions always exist; furthermore, $O(1)$-depth simulators are surprisingly common, and can be understood using tools from Krohn-Rhodes theory and circuit complexity." | transformer side | VERIFIED |
| arXiv:2310.07923 | Merrill, 2023 | The Expressive Power of Transformers with Chain of Thought | "We show that the answer is yes, but the amount of increase depends crucially on the amount of intermediate generation." | CoT as depth | VERIFIED |
| arXiv:2402.12875 | Li, 2024 | Chain of Thought Empowers Transformers to Solve Inherently Serial Problems | "We first show an even tighter expressiveness upper bound for constant-depth transformers with constant-bit precision, which can only solve problems in $\mathsf{AC}^0$ ..." | CoT as depth | VERIFIED |
| arXiv:2207.02098 | Deletang, 2022 | Neural Networks and the Chomsky Hierarchy | "... LSTMs can solve regular and counter-language tasks ..." | LSTM positive control | VERIFIED |

## Prior art vs. contribution (honest positioning)
- **Constructions exist; lower bounds did not.** Grazzi et al. and Siems et al. construct realisations (n - 1 Householders for S_n, n for
  O(n), two for SO(3)); RWKV-7 tracks swaps on five elements. The scout found no lower bound on the number of Householder factors per
  token for a given group (scout_evidence.md, "Main gap"). Our L1 + L2 + L4 give the first such lower bound, and Theorem 1 an exact
  characterisation (h*) for finite-state one-layer realisations.
- **DeltaProduct's S4/A5 observation** ("despite the theorem suggesting 3 and 4") was explained post hoc by SO(3); our law predicts it,
  proves that 2 is also necessary (L4), and shows that the relevant minimum is over all representations AND covering groups.
- **Howe 2026** states an empirical, representation-relative law (S4 3, A5 4 in the transposition+4-cycle / 3-cycle+5-cycle formats). We
  certify h* = 2 for exactly these alphabets (Table 1, `S4/tn`, `A5/c3c5`), so with an arbitrary readout 3 and 4 are not expressivity
  requirements; any gap is a matter of readout class, task format or learnability.
- **Diagonal models:** our L5 restates known results (Sarrof et al., Grazzi et al., Shakerinava et al.) in the finite-state setting; no
  novelty claimed there.
- **Circuit complexity** (Merrill & Sabharwal; Merrill, Petty & Sabharwal; Barrington) orders problems for transformers and diagonal
  SSMs; our atlas shows that for Householder-product layers the per-layer cost is not ordered by solvability.
