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

## Nachtrag 2026-10-03: Negativkontrolle je Seed (nach dem ersten vollen Lauf)

**Was:** Zusätzlich zur präregistrierten Negativkontrolle (eine Vertauschung, Seed 7) läuft eine Negativkontrolle mit eigener Vertauschung je Seed (`np.random.default_rng([7, seed])`). Das Gate „Negativkontrolle“ wird auf dieser Variante ausgewertet. Die Seed-7-Variante wird weiter vollständig berichtet (Claims `C-neg-seed7*`), für GP + EI bleibt sie zusätzlich ein Gate.

**Grund:** Hybrid nutzt ein festes KI-Vorwissen. Bei nur einer Vertauschung ordnet es die Kandidaten in allen 20 Seeds gleich. Liegt zufällig ein vertauschter Treffer weit oben im Vorwissen (hier: Rang 17 von 4132), findet Hybrid ihn in jedem Seed nach etwa 17 Schritten. Die 20 Seeds sind dann keine unabhängigen Wiederholungen, und der Test misst nur eine einzige Zufallsziehung. Im ersten Lauf ergab das scheinbar 5,9× Speedup auf Rauschen. Ein Leck ist ausgeschlossen: Der getroffene Kandidat ist in allen Seeds derselbe, und GP + EI ohne Vorwissen zeigt 0,99×.

**Unverändert:** H1, H2, Metrik, Seeds, Budget, Tests, Erfolgskriterien, die Definition von Hybrid und die Hypothesen der KI. H1 und H2 werden nicht neu bewertet.

## H3 (2026-10-03, vor dem ersten Lauf irgendeiner Bedingung): Framework schlägt „Claude pur“

**Aufgabe:** 12 Fragen aus `benchmarks/suleman2026.json` (Suleman 2026, Preprint vom September 2026, also nach dem Trainingsstand der Modelle; die Antworten stehen im Paper und sind für alle Bedingungen verdeckt).

**Bedingungen** (gleiches Modell für alle: Alias `sonnet` über `claude -p`):
- **A1 Claude pur:** ein Prompt pro Frage mit Kontext, ohne Tools (wie Claude im Browser ohne Code).
- **A2 Claude mit Code:** derselbe Prompt; Bash/Python in einem leeren temporären Verzeichnis, eigener Code, höchstens 1 USD pro Frage. Internet- und Dateizugriff außerhalb der Sandbox sind untersagt. Ein Lauf, dessen Transkript solchen Zugriff zeigt, wird verworfen und einmal wiederholt.
- **B Framework:** 4 unabhängige Forscher-Agenten mit verschiedenen Strategien schlagen getypte, ausführbare Behauptungen und Experimentpläne vor. Das Gitter-Lab rechnet die Experimente (validiert gegen Tabelle 2 und ν* des Papers). Nach einer zweiten Runde mit den Ergebnissen prüft ein Code-Prüfer jede Behauptung unabhängig mit eigener Auflösung. Antwort = geprüfte Behauptung mit den meisten Stimmen; ist keine geprüft, lautet die Antwort „unbekannt“. Kein LLM entscheidet über Wahrheit.

**Wiederholungen:** je Bedingung 3 unabhängige Läufe (salt 0, 1, 2).

**Bewertung (Code, gegen den Antwortschlüssel):** richtig / falsch / „unbekannt“; Zahlen innerhalb der Toleranz im Schlüssel. Pro Frage zählt der Mittelwert über 3 Läufe.

**H3a (primär):** Trefferquote B > A1. Gepaarter Vorzeichen-Flip-Permutationstest über die 12 Fragen, einseitig, 20 000 Permutationen; Erfolg bei p < 0,05.
**H3b:** Trefferquote B > A2, gleicher Test.
**H3c:** Anteil falscher (nicht enthaltener) Antworten B < A1 und B < A2, gleicher Test.
Kosten (USD) und Laufzeit je Bedingung werden berichtet. Ergebnisse werden berichtet, egal wie sie ausfallen. Benjamini-Hochberg über H3a–c (m = 3, q = 0,1).

### Nachtrag H3, 2026-10-03 20:30: Fehlerkorrektur im Prüfer (während Lauf B)
Der Prüfer verwarf Intervalle der Breite genau 0,05 wegen Gleitkomma-Rundung (8,63 − 8,58 > 0,05). Die Regel „Intervallbreite ≤ 0,05“ war inklusiv gemeint; die Prüfung nutzt jetzt `<= 0.05 + 1e-9`. Betroffen war bis dahin nur Q7, Lauf 0 (alle 4 Forscher hatten 8,58–8,63 angegeben). Der Lauf wurde mit identischen, gecachten LLM-Antworten neu bewertet. Die ursprüngliche Datei liegt unter `results/benchmark/B_Q7_s0_vor_bugfix.json`. Sonst bleibt alles unverändert.
