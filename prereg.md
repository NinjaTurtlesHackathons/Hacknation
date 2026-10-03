# Präregistrierung (vor dem ersten Hybrid-Lauf committen; der Commit-Hash dient als Zeitstempel)

**H1 (primär):** Policy „hybrid“ (KI-Hypothesen als Vorwissen für GP + EI) braucht weniger Experimente bis zum Top-1 % als „gp_ei“.
- Metrik: $N_\pi$ (siehe `CLAUDE.md`), Datensatz `rxnpredict`, $n=4132$, $k=41$
- Seeds 1000–1019, Budget 400, Start mit 5 zufälligen Experimenten wie bei gp_ei
- Test: gepaarter Permutationstest, einseitig, 20.000 Permutationen; Effekt als Verhältnis der Mittelwerte mit Bootstrap-95 %-KI
- Erfolg: $p<0{,}05$ und KI-Untergrenze $>1$
- Abbruch: Hybrid ist bei 06:35 nicht signifikant → Fallback laut `CLAUDE.md`

**H2 (Kontamination):** Der Gewinn von Hybrid bleibt bestehen, wenn Namen und SMILES durch neutrale Codes und Deskriptoren ersetzt werden.
- Gleiches Design wie H1 und gleicher Test, verglichen wird hybrid_neutral mit gp_ei
- Ergebnis wird berichtet, egal wie es ausfällt

**Negativkontrolle:** vertauschte Ausbeuten (Seed 7). Erwartung: kein Speedup, $p>0{,}05$.

**Mehrfachtests:** Alle Hypothesen der KI laufen gemeinsam durch Benjamini-Hochberg mit $q=0{,}1$.

Änderungen an dieser Datei nach dem ersten Lauf nur als neuer Abschnitt mit Datum und Grund.
