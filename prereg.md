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

## H4 (2026-10-03, vor dem ersten Lauf): Kostenoptimierte Kaskade (BK)

**Bedingung BK:** dieselben 12 Fragen, 3 Läufe (salt 0, 1, 2). Die Forscher arbeiten nacheinander: sparsam/Haiku → numeriker/Haiku → skeptiker/Sonnet → theoretiker/Sonnet. Der Lauf stoppt bei der ersten Behauptung, die den Code-Prüfer besteht und zur Antworttext passt (`consistent`). Prüfer, Lab und Bewertung sind unverändert.
**Referenz:** B kostete 7,42 USD für 36 Läufe (0,206 USD je Frage, aus dem LLM-Cache, `benchmarks/cost.py`).
**H4a:** Kosten BK ≤ 30 % von B. **H4b:** Trefferquote BK ≥ 35/36 und höchstens 1 falsche Antwort. **H4c (Test):** Trefferquote BK > A2, gepaarter Vorzeichen-Flip-Permutationstest wie H3b.
Ergebnis wird berichtet, egal wie es ausfällt.

## H5 (2026-10-03, vor dem ersten Lauf): Literatur-Hypothesen als GP-Prior

**Policy hybrid_lit:** identisch zu hybrid (GP + EI, Prior-Mittelwert a·m(x), a wird nach jeder Messung geschätzt). m(x) stammt aus `hypotheses/literature.json`: 8 Hypothesen des Recherche-Agenten, jede mit per Code bestätigten Literaturzitaten. Quellen zum Testdatensatz sind durch den Leck-Filter gesperrt (u. a. „Ahneman“, „Doyle“, „rxnpredict“, „machine learning“, „dataset“).
**Neue Seeds:** 1020–1039 (bisher nicht verwendet), Budget 400, 5 zufällige Startexperimente.
**H5a (primär):** hybrid_lit braucht weniger Experimente als gp_ei. Gepaarter Permutationstest, einseitig, 20 000 Permutationen; Erfolg bei p < 0,05 und KI-Untergrenze des Speedups > 1.
**H5b (Replikation):** hybrid (Hypothesen ohne Literatur) vs gp_ei auf denselben neuen Seeds, gleicher Test.
**Negativkontrolle:** hybrid_lit auf vertauschten Ausbeuten (eigene Vertauschung je Seed); erwartet: kein Speedup gegenüber Zufall.
Ergebnis wird berichtet, egal wie es ausfällt.

## H6 (2026-10-04, vor dem Lauf): Kinetic Proofreading, Lücken L1–L5 aus `projects/proofreading/lueckenkarte.md`

Modell und Prüfer: `asd/domains/proofreading*.py`, Selbsttest 15/15 bestanden. Budget: 6 Runden, höchstens 6 USD. Startfragen nur aus der Lückenkarte (`projects/proofreading/fragen.json`), Reihenfolge nach Value of Information.

- **L2 (Universalität, primär):** Hypothese: e^{-2Δ} ist KEINE universelle Grenze der Familie gebunden<=2 (92 Topologien). Prüfung: `erreichbar` mit eta_max < 1e-4 auf einem Mitglied fam2_* (exakt). Erfolg: mindestens ein exakt zertifiziertes Mitglied mit eta < e^{-2Δ}. Abbruch: kein zertifiziertes Gegenbeispiel nach 2 Runden. Erwartet: Gegenbeispiele existieren (Vorbefund des Explorers, numerisch).
- **L2b (Teilfamilie):** Hypothese: Für eine nichtleere Teilfamilie gilt eta >= 1/D**2 für alle Raten. Prüfung: `schranke_familie` mit Mitgliederliste. Erfolg: bestanden. Erwartet: rund 50 Mitglieder.
- **L3 (Mechanismus):** Hypothese: Unterschreiten erfordert einen treibstoffgetriebenen Ausgang (Verwerfen mit fuel 1) an einem Zustand, in den Produkt zurückbinden kann. Prüfung: Gegenbeispiel (`erreichbar`) bzw. Teilfamilien-Schranke für Netze ohne dieses Merkmal. Erfolg: entweder Schranke für die Teilfamilie ohne Merkmal bewiesen oder ein exaktes Gegenbeispiel ohne Merkmal (dann ist die Hypothese widerlegt).
- **L1 (Kette):** Hypothese: eta >= e^{-(n+1)Δ} für n = 0, 1, 2 für alle Raten. Prüfung: `untere_schranke`. Erwartet: bestanden (Reproduktion, rigoros).
- **L4 (Geschwindigkeit):** Hypothese: Für hopfield_n1 mit v >= 1e-3 ist eta < 2e-4 bei sigma <= 10 kT erreichbar. Prüfung: `erreichbar` (exakt). Abbruch: nicht erreichbar nach 1 Runde.
- **L5 (gleichgewichtsnah):** Hypothese: eta <= 1.2e-4 bei sigma <= 0.2 kT pro Produkt erreichbar (v beliebig). Prüfung: `erreichbar` (exakt).
Alle Ergebnisse, auch negative, werden berichtet. Neuheit wird erst in Phase 6 beurteilt.
