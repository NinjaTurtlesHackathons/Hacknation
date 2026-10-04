# Präregistrierung: Köcher-Domäne (`quivers`)

Stand: 2026-10-04, vor jedem Lauf von `projects/quivers/run_lab.py`. Prüfer: `asd/domains/quivers_domain.py`,
Selbsttest `python -m asd.selftest quivers` (34/34 bestanden vor dieser Präregistrierung).
Alle Prüfungen sind exakt (rationale Arithmetik, F_p, symbolische Elimination). Es gibt keine Toleranzen und keine
statistischen Tests; Benjamini-Hochberg entfällt deshalb. Jede Aussage ist entweder exakt bestätigt oder nicht.

Bewusste Annahmen, die die Resultate tragen:
- Grundkörper der „Klassifikation“ ist algebraisch abgeschlossen; geprüft wird über Q (Unzerlegbarkeit über Q̄ via Spurform)
  und über F_p (Zählung). Für unteilbare Dimensionsvektoren ist „unzerlegbar über F_q“ gleich „absolut unzerlegbar“.
- Kac-Polynome: Polynomialität und Grad 1 - q(alpha) werden aus der Literatur übernommen (Kac 1983); geprüft wird die
  Übereinstimmung an deg + 2 Primzahlen (eine Stützstelle mehr als nötig).

| Frage | Hypothese (erwartet) | Prüfungstyp | Erfolg | Abbruch |
|---|---|---|---|---|
| F1 Gabriel | A2, A3, star3 = D4 endlich; star4 zahm; star5..star7 wild; Zykel und Kronecker zahm; D4 hat 12 positive Wurzeln; über F_2, F_3 gibt es für D4 genau eine Unzerlegbare je positiver Wurzel und keine sonst | `tits_typ`, `wurzelzahl`, `kac_box` | alle bestätigt | ein Widerspruch zu Gabriel: Prüfer anhalten, Code-Fehler suchen |
| F2 Vier-Unterraum (star4 = D~4) | delta = (2;1,1,1,1); A_delta(q) = q + 4; die Familie V_t (Geraden (1,0), (0,1), (1,1), (1,t)) besteht aus paarweise nicht isomorphen Ziegeln; über F_p ist {V_t : t ≠ 0, 1} ∪ {6 Darstellungen mit genau einem zusammenfallenden Geradenpaar} vollständig (p = 2, 3, 5); reelle Wurzeln haben genau eine Unzerlegbare | `radikal`, `kac_polynom`, `familie`, `klassifikation`, `kac_box`, `unzerlegbar` | alle bestätigt | Liste unvollständig: Normalformen-Experiment auswerten, Hypothese verwerfen (negatives Ergebnis) |
| F3 Wilde Sterne (star n, n ≥ 5) | Tits-Form indefinit; alpha_n = (2;1^n) hat 1 - q = n - 3 Parameter; Kac-Polynome von alpha_n für n = 5, 6, 7 haben Grad n - 3 und Leitkoeffizient 1; für (2k; k^5) wächst die Parameterzahl wie 1 + k^2 | `tits_typ`, `parameter`, `kac_polynom` | alle bestätigt | Grad ≠ n - 3: negatives Ergebnis |
| F4 Zykel (3- und 4-Zykel) | delta = (1,...,1); A_delta(q) = q + n - 1 für alle Orientierungen (orientiert und azyklisch); orientierter Zykel: Anzahl Unzerlegbarer = Strings + Monodromie-Moduln für alle beta <= (2,2,2) bzw. (2,2,2,2) über F_2, F_3; vollständige Listen für delta über F_3 | `radikal`, `kac_polynom`, `zykel_box`, `klassifikation`, `unzerlegbar`, `familie` | alle bestätigt | Abweichung von der Vorhersage: negatives Ergebnis, Vorhersage-Formel prüfen |
| F5 Vielfache von delta | I_{2 delta}(q) = (q + n - 1) + (q^2 - q)/2 für Ã2 (n = 3) und D~4 (n = 5), d. h. A_{2 delta}(q) = A_delta(q) | `anzahl` | bestätigt für q = 2, 3 (Ã2 auch 5) | Abweichung: negatives Ergebnis |

Budget: keine LLM-Kosten im Labor (Fragen aus dieser Präregistrierung, Prüfer exakt); Paper-Schreiber: höchstens 3 USD.
