# Lean-Beweis: E[N_random] = (n+1)/(k+1)

Bewiesen (nur Lean-4-Core, ohne Mathlib, kein `sorry`/`axiom`): eigene Binomialfunktion `choose` (Pascal-Rekursion), die Hockey-Stick-Identität `Σ_{m=0}^{n} choose m k = choose (n+1) (k+1)` (`hockey_stick`), die Absorptionsidentität `(k+1)·choose (n+1) (k+1) = (n+1)·choose n k` (`absorption`) und der Hauptsatz `expected_first_hit_cross`: für `k ≤ n` gilt `(k+1) · Σ_{t=1}^{n-k+1} choose (n-t+1) k = (n+1) · choose n k`.

Zuordnung zur Behauptung: Bei `n` Items mit `k` Treffern (Ziehen ohne Zurücklegen) ist `N` die Position des ersten Treffers. `N ≥ t` heißt „die ersten t−1 Züge sind Nieten“, also `#{N ≥ t} = choose (n-t+1) k` und `P(N ≥ t) = choose (n-t+1) k / choose n k`. Mit `E[N] = Σ_{t=1}^{n-k+1} P(N ≥ t)` und `choose n k > 0` (`choose_pos`) ist der Hauptsatz genau die kreuzmultiplizierte Form von `E[N] = (n+1)/(k+1)`. Der Fall n = 4132, k = 41 ist als `example` direkt abgeleitet.

Prüfen: `lean lean/ENRandom.lean` (getestet mit Lean 4.34.1, Installation via elan). Exit-Code 0; die einzige Ausgabe ist `#print axioms`, die nur die Standardaxiome `propext` und `Quot.sound` zeigt.
