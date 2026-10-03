# Präregistrierung: Domäne optscale (Optimierung und Skalierungsgesetze)

Festgelegt vor dem ersten Laborlauf. Kriterien des Prüfers (`asd/domains/optscale_domain.py`) werden nach dem Lauf nicht geändert;
Abweichungen kommen als datierter Nachtrag ans Ende dieser Datei.

## Feste Prüfer-Kriterien
- **exponent:** Prüfer rechnet die Kurve in zwei Fenstern mit höherer Auflösung nach (gf: t in [1e3,1e5] und [1e4,1e6], M = 1e6 plus Restintegral;
  param: P ebenso; compute: C in [1e5,1e7] und [1e6,1e8]; ridge/rf: Monte Carlo, 8 Seeds 500ff./600ff., M = 3000 bzw. 4000).
  Besteht, wenn beide Fits innerhalb 0,03 (deterministisch) bzw. 0,10 (Monte Carlo) am behaupteten Exponenten liegen.
- **vergleich:** LR-Tuning des Prüfers auf 2^-16..2^4 (Faktor 2), Tuning-Seeds 100–102, Bewertung auf 10 frischen Seeds 200–209.
  Besteht bei gepaartem einseitigem Permutationstest p < 0,01 UND geometrischem Verlust-Verhältnis < 0,9. Optimum am Gitterrand: nicht entscheidbar.
- **eos:** voller Hesse-Eigenwert bei 80 % und 100 % der Schritte, Seeds 300–304; eos: lr*lambda_max/2 in [0,85; 1,25], stabil: < 0,8, je in >= 4/5 Seeds.
- **lr_transfer:** Prüfer-Tuning Faktor 2 (Adam 2^-14..2^-2, SGD 2^-10..2^2), 300 Schritte, Seeds 400–401;
  Transfer: |Verschiebung| <= 1 Oktave und Spannweite <= 1; kein Transfer: |Verschiebung| >= 2.
- **stabilitaet:** exakt (rationale Arithmetik, Sylvester-Kriterium).

## Multiples Testen
Alle `vergleich`-Prüfungen (inkl. Red-Team) werden am Ende gemeinsam mit Benjamini-Hochberg (q = 0,1, m = Zahl aller durchgeführten Vergleiche) berichtet.

## Leck- und Kontextregel
Der Agenten-Kontext enthält keine erwarteten Exponenten oder Ergebnisse. Literatur nur mit per Code bestätigtem Wortzitat (Scout).
Die Theorie-Resultate zu linearen Modellen sind in der Literatur bekannt; sie gelten als Reproduktion (Anker), nicht als neuer Befund.
