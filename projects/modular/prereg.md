# Präregistrierung: Modulformen und Stringtheorie-Identitäten (Phase 4)

Festgelegt am 2026-10-04, vor dem ersten Laborlauf. Prüfer und Toleranzen: `asd/domains/modular_domain.py` (Selbsttest 23/23,
Prüfer-Red-Team 12/12 Fallen korrekt abgelehnt). Kriterien werden nach dem Lauf nicht geändert; Abweichungen nur als datierter Nachtrag.

## Feste Prüfparameter (für alle Ziele)
- MGF-Relationen: exakter Laurent-Leitkoeffizient muss verschwinden; dann 4 Prüfer-Punkte (Seed 4711, |tau1| <= 1/2, 1 <= tau2 <= 2,5),
  32 Stellen, max. relatives Residuum <= 1e-24 (mit Laplace-Term: <= 1e-14). Stufe: numerisch (observed), nie „Theorem“.
- Relationsraum: jede Relation wie oben; Vollständigkeit: genau dim Singulärwerte < 1e-24 und alle übrigen > 1e-8 (n+3 Punkte, Seed 4712).
- Holomorph: Sturm-Zertifikat (exakt), Stufe computed_rigorous.

## H1 (L1): Gewicht-9-Identität
Hypothese: Zwischen den sieben C_{a,b,c} vom Gewicht 9, E_9 und zeta(9) besteht mindestens eine rationale lineare Relation.
Prüfung: mgf_relation. Erfolg: eine Relation besteht. Abbruch: PSLQ mit 50 Stellen und Koeffizienten bis 1e12 findet keine Relation.
Erwartung: genau eine Relation (Analogie zu w = 3, 5, 7).

## H2 (L3): Zählung pro ungeradem Gewicht
Hypothese: Für w = 3, 5, 7, 9 hat der Raum der Relationen zwischen {C_{a,b,c}: a+b+c = w}, E_w und zeta(w) die Dimension genau 1.
Prüfung: mgf_relationsraum je Gewicht. Erfolg: dim = 1 bestätigt. Gegenteil wird genauso berichtet.

## H3 (L2): Gewicht 11
Wie H1 für w = 11 (zehn Funktionen). Abbruch nach 2 Runden ohne geprüfte Relation (Rechenzeit).

## H4 (L4): Gewicht 6
Hypothese (Nullhypothese des Negativbefunds): Der Relationsraum der in fragen.json genannten Basis hat Dimension 0.

## H5 (L6): Eta-Quotienten, Gewicht 4
Exakte Tabelle für N <= 30. Erfolg: eta_span_tabelle besteht. Keine Erwartung vorab.

## Anker (L5, L7)
Laplace-Gleichung von C_{3,1,1} und holomorphe Stringidentitäten (Jacobi, E8+E8 = D16+, Delta). Nur Validierung, als Reproduktion berichtet.

## Lauf
`python -m asd.lab_loop --domain modular --fragen projects/modular/fragen.json --runden 8 --gezielt`
Mehrfachtests: Es werden keine p-Werte gebildet (deterministische Prüfungen), daher keine BH-Korrektur.
