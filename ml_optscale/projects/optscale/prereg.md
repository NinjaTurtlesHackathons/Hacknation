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

## Runde 1 (2026-10-03 23:22:38), vor dem Experiment
- Frage [F3]: Folgen Ridge-Regression (über N) und das lineare Random-Feature-Modell (über P) denselben Exponenten wie das Abschneiden auf P Eigenrichtungen, oder gibt es Regime (a, b), in denen sie abweichen?
- Begründung: F3 hat den besten erwarteten Erkenntnisgewinn (Neuheit 0,6 x Machbarkeit 0,7) bei großer Lücke zum Bekannten. F1 und F9 sind weitgehend analytisch bekannt: L(t) ~ t^-(b-1)/a und die Grenze 2/lr, daher kaum neue Erkenntnis. F2 folgt zum großen Teil aus F1 plus Trunkierung. F4 bis F8 hängen stark von Tuning, Seeds und Architektur ab, sind schwerer unabhängig nachzurechnen und haben teils bereits Literaturanker (EoS, μP). F3 ist rein numerisch und billig, mit exakter Referenz (Trunkierung auf P Eigenrichtungen, Verlust ~ P^-(b-1)). Zugleich ist es nicht trivial, weil Ridge mit endlichem N und Random Features mit Gauß-Projektionen zusätzliche Varianz- und Bias-Terme erzeugen, die je nach (a, b) das Regime ändern können, etwa durch Sättigung der Ridge-Regularisierung, Überparametrisierung oder eine Verschiebung des Exponenten für b nahe 1 oder große a. Ein unabhängiger Prüfer kann das mit eigenen Seeds und eigener Auflösung nachrechnen, weil keine Lernratenabstimmung nötig ist.
- Erfolg: Für mindestens fünf (a, b)-Paare, die Regime mit b nahe 1 und b deutlich größer als 1 sowie kleines und großes a abdecken, werden die Exponenten von Ridge (über N, mit optimal gewähltem Lambda und mit fixem Lambda) und Random Features (über P) per Log-Log-Fit über mindestens eine Dekade mit Unsicherheit aus mindestens 5 Seeds bestimmt. Sie werden mit dem Trunkierungs-Exponenten (b-1)/a-Referenz verglichen. Ein Ergebnis zählt als Erfolg, wenn entweder (i) Übereinstimmung innerhalb von 10 % für alle Paare gezeigt wird, mit einer klar benannten Regelgrenze, oder (ii) mindestens ein Regime mit signifikanter Abweichung (über 3 Standardfehler und über 10 %) gefunden wird, das ein unabhängiger Prüfer mit eigenen Seeds und eigener Auflösung (andere Dimension und N-/P-Gitter) reproduziert.
- Abbruch: Abbruch, wenn bei der maximal rechenbaren Dimension (z. B. d etwa 10^4) die Fit-Fenster weniger als eine Dekade im sauberen Potenzbereich liefern, oder wenn die Exponenten sich bei Verdopplung der Dimension um mehr als 20 % verschieben (Finite-Size-Artefakt). Ebenfalls Abbruch, wenn der Prüfer die Exponenten nicht innerhalb der Fit-Unsicherheit reproduziert. In dem Fall wird auf F2 gewechselt, das mit demselben Code mitgeprüft werden kann.
- Erwartung: Erwartet wird, dass Ridge mit optimal gewähltem Lambda und Random Features im Regime b > 1 mit moderatem a dem Trunkierungs-Exponenten (b-1)/a folgen, bis auf Vorfaktoren. Abweichungen werden bei fixem Lambda (Sättigung des Exponenten) und nahe b = 1 oder bei sehr großem a erwartet, wo Random Features durch das Sampling-Rauschen der Projektion das Plateau früher erreichen oder der Exponent durch die Varianz begrenzt wird. Konfidenz für Übereinstimmung im Standardregime etwa 70 %, für mindestens ein klar abweichendes Regime etwa 50 %.
