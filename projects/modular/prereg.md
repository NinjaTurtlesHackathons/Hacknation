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

## Runde 1 (2026-10-04 04:17:37), vor dem Experiment
- Frage [F2]: Wie viele unabhängige rationale lineare Relationen bestehen zwischen allen C(a,b,c) vom Gewicht w, E(w) und zeta(w) für w = 3, 5, 7, 9? Bestimme den Relationsraum je Gewicht vollständig (mgf_relationsraum).
- Begründung: F2 enthält F1 als Spezialfall (Gewicht 9) und liefert zusätzlich die Relationsräume für w = 3, 5, 7, 9. So entsteht ein vollständiges Muster, das sich auch auf Gewicht 11 (F3) extrapolieren lässt. Der Gewinn an Information ist deshalb größer als bei F1, F3, F4 oder den Anker-Fragen. Die Frage geht eine offene Literaturfrage an: Die Struktur der Relationen zwischen dihedralen Modulgraphfunktionen und E(w), zeta(w) ist über die Eigenwertzerlegung nach D'Hoker-Green-Vanhove und D'Hoker-Kaidi nur teilweise bekannt. Die Gewichte 3 und 5 liefern bekannte Kontrollfälle (C(1,1,1) = E(3) + zeta(3), C(2,2,1) = 2/5 E(5) + zeta(5)/30), die das Verfahren validieren. Die Prüfung läuft mit mgf_relationsraum über eigene Zufallspunkte des Prüfers, ist also unabhängig. Die Anker F6 und F7 sind noch nicht validiert. Sie sind aber nur Absicherung und haben geringen Neuheitswert. F3 braucht sehr hohe Präzision (Machbarkeit 0.5), und F4 betrifft nur einen einzelnen Fall.
- Erfolg: Für jedes Gewicht w in {3, 5, 7, 9} ist der rationale Relationsraum (Dimension und explizite Basis ganzzahliger Relationen) bestimmt. Er ist über mehrere unabhängige Zufallspunkte mit mindestens 25 stabilen Stellen verifiziert und stimmt mit den bekannten Fällen w = 3 und w = 5 überein. Für w = 9 ist die Frage F1 (existiert eine Relation, und wenn ja welche) eindeutig beantwortet. Der Rang des numerischen Gleichungssystems ist stabil gegenüber Variation von Präzision und Punktezahl (Überbestimmung mit mehr Punkten als Unbekannten, LLL/PSLQ-Ergebnis reproduzierbar).
- Abbruch: Abbruch, wenn die numerische Auswertung der C(a,b,c) nicht auf mindestens 30 Stellen konvergiert, oder wenn die Rangbestimmung für w = 7 und w = 9 auch nach Erhöhung von Präzision und Punktezahl instabil bleibt (kein klarer Spalt der Singulärwerte). Ebenso, wenn die Kontrollfälle w = 3 und w = 5 nicht reproduziert werden, was auf einen Fehler in Methode oder Implementierung hindeuten würde. In diesem Fall werden w = 3 und w = 5 gesichert, und die Ressourcen gehen an F7 (Anker) oder F4.
- Erwartung: w = 3: genau 1 Relation (C(1,1,1) = E(3) + zeta(3)). w = 5: genau 1 Relation (C(2,2,1) = 2/5 E(5) + zeta(5)/30). Für w = 7 und w = 9 erwarte ich wenige Relationen (Dimension 0 bis 2). Dass F1 für die sieben Funktionen genau eine Relation hat, halte ich für eher unwahrscheinlich. Bei fehlender Relation sind die Gewicht-9-Funktionen mit E(9) und zeta(9) rational unabhängig, was die erwartete Struktur der Eigenräume stützt.

## Runde 2 (2026-10-04 05:28:01), vor dem Experiment
- Frage [F4]: Gibt es bei Gewicht 6 rationale lineare Relationen zwischen C(4,1,1), C(3,2,1), C(2,2,2), E(6), E(2)*E(4), E(3)^2, E(2)^3, zeta(3)*E(3), zeta(3)^2? Bestimme die Dimension des Relationsraums (auch 0 ist ein Ergebnis).
- Begründung: Kein Anker (F6, F7) ist bisher validiert, aber F6 und F7 haben geringen Informationsgewinn. F6 folgt fast direkt aus der bekannten Relation C(3,1,1) = 2/5 E(5) + ζ(5)/30. F7 ist eine reine Routineprüfung. F4 geht dagegen eine offene Literaturfrage an: die Struktur der Relationen bei Gewicht 6, wo erstmals Produkte E*E und ζ(3)*E(3) als Quellen auftreten. Die Dimension des Relationsraums ist unabhängig vom Ergebnis informativ, auch bei 0. Sie testet die Zählung der Laplace-Eigenräume (Eigenwerte s(s-1) mit s = 4, 2) und baut direkt auf modular-R1 (Gewicht 3) auf. F1 ist plausibel ebenfalls offen, hat aber wahrscheinlich nur den Relationsraum 0, ist also weniger aufschlussreich. F3 braucht sehr hohe Präzision bei schlechter Machbarkeit (0.5). F4 ist mit 9 Funktionen und ~30 Stellen gut machbar (0.7).
- Erfolg: Die Dimension des rationalen Relationsraums der 9 Funktionen C(4,1,1), C(3,2,1), C(2,2,2), E(6), E(2)E(4), E(3)^2, E(2)^3, ζ(3)E(3), ζ(3)^2 ist eindeutig bestimmt. Dafür gibt es einen klaren Singulärwertabstand (kleine Werte < 1e-24, größter kleiner Wert > 1e-8) bei einer Wertematrix mit deutlich mehr Zeilen als Spalten (z. B. 20 Zufallspunkte, ≥ 30 Stellen). Jede gefundene Basisrelation hat kleine ganzzahlige oder rationale Koeffizienten, wird einzeln von mgf_relation an unabhängigen Prüferpunkten bestätigt und stimmt, wenn möglich, mit den Laplace-Gleichungen überein.
- Abbruch: Abbruch, wenn bei 30 Stellen und mindestens 20 Punkten kein klarer Singulärwertabstand entsteht (nur Werte im Bereich 1e-12 bis 1e-6). Ebenso, wenn die rationale Rekonstruktion keine Koeffizienten mit Nenner < 1e6 liefert oder die Relation die Prüfung an neuen Punkten nicht besteht. Dann wird nur 'Dimension ≥ 0, unentschieden' gemeldet und die Präzision für einen zweiten Versuch erhöht. Insgesamt höchstens zwei Versuche.
- Erwartung: Wahrscheinlich 1 bis 2 Relationen. Die Literatur (D'Hoker–Green–Vanhove, Basu) legt nahe, dass C(2,2,2) und C(3,2,1) über Laplace-Gleichungen mit E(6), E(2)E(4), E(3)^2, E(2)^3 und ζ(3)E(3) zusammenhängen, während C(4,1,1) einen Eigenwert 20 (s = 5) und eine Quelle E(2)E(4)-artig hat. Ob daraus eine rein lineare Relation ohne Laplace-Operator folgt, ist offen. Die Dimension ist vermutlich klein (0 bis 2), mit Wahrscheinlichkeit ~50 % für mindestens eine nichttriviale Relation.
