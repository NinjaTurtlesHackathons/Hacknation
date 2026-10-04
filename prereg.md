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

### Nachtrag H6, 2026-10-04: Familie und Prüferkorrektur (nach Runde 5, vor den Runden 6 ff.)
1. **Entartete Familienmitglieder ausgeschlossen:** 4 der 92 Netze haben keinen Weg von E zum Produktzustand ohne die Produktkante. Dort ist keine Nettoproduktion möglich, eta = 0/0 ist undefiniert. Die Familie gebunden<=2 hat jetzt 88 Mitglieder. Die Namen bleiben stabil (fam2_0 … fam2_91, die entarteten Nummern sind frei).
2. **Prüferfehler behoben:** Bei diesen Netzen stürzte `schranke_familie` mit „Invalid NaN comparison“ ab (Runde 5, L3). Jetzt gilt: undefiniertes eta = nicht bewiesen, und ein Fehler bei einem Mitglied führt nicht zum Absturz. Neuer Selbsttest-Fall, 16/16 bestanden.
3. **L3 wird wiederholt,** weil Runde 5 am Prüfer gescheitert ist und nicht an der Hypothese. Runde 5 bleibt als negatives Ergebnis protokolliert.
Hypothesen, Erfolgskriterien und Budget bleiben unverändert.

### Nachtrag H6, 2026-10-04: Vollständige Klassifikation (vor den Runden mit fragen2.json)
Neue Werkzeuge: `classify_family`, `search_counterexamples` (Explorer, nur Kandidaten) und der Prüfungstyp `erreichbar_liste` (Zertifikat a je Fall). Selbsttest 18/18.
- **L2b (vollständig):** Hypothese: Für die vollständige Liste der beweisbaren Mitglieder gilt eta >= 1/D**2 für alle Raten. Erfolg: `schranke_familie` besteht für diese Liste. Erwartet: rund 50 von 88 (Vorrechnung des Explorers).
- **L2c:** Hypothese: Unter den übrigen Mitgliedern gibt es mehrere exakt zertifizierbare Gegenbeispiele mit eta < 1e-4. Erfolg: `erreichbar_liste` besteht mit mindestens 5 Fällen. Abbruch: weniger als 5 Fälle nach 1 Runde, wird dann als Teilergebnis berichtet.
Zusammen ergibt das eine Klassifikation: bewiesen / Gegenbeispiel / offen. Offene Fälle werden als offen berichtet.

## H7 (2026-10-04, vor dem ersten Lauf irgendeiner Bedingung): Gemessene Beschleunigung durch das Labor (Replay, Domäne lattice)

**Aufgabe (Replay eines bekannten Resultats):** Gemeinsamer Forschungsauftrag für alle Bedingungen: „Wie verhalten sich die energieminimierenden
2D-Gitter, wenn nu sehr groß wird (nu → ∞)? Bestimme das Grenzverhalten quantitativ und formuliere eine prüfbare Aussage.“
Zielresultat (Suleman 2026): Rechteckgitter mit Seitenverhältnis y_inf = sqrt((sqrt(17)-1)/2) ≈ 1,249621 (dazu P* ≈ 1,431734).
**Treffer (per Code, nicht per LLM):** eine vom unveränderten Verifier bestandene Behauptung vom Typ `grenzwert` mit `groesse = y_inf`
(der Verifier rechnet den Fit über nu = 100…1000 selbst und akzeptiert nur innerhalb seiner festen Toleranz 2·10⁻⁴), die aus dem
Behauptungspfad kommt (nicht aus einer Red-Team-Gegenprüfung).
**Ehrliche Einschränkung, vorab:** Der Lattice-Verifier ist numerisch (Stufe „numerisch“), nicht exakt/rigoros, und hat keinen
Prüfungstyp für P*. Der Verifier wird für diesen Benchmark nicht geändert; ein Treffer heißt also „numerisch geprüft“, nicht „bewiesen“.

**Leckschutz:** Das Suleman-2026-Preprint und alle daraus abgeleiteten Wissensdateien sind für alle Agenten gesperrt (leere Wissensbasis
im Replay-Projekt, Sperrliste `omni/leak_guard.json`). Kanarien-Test vor jedem Lauf: Der gesamte Agenten-Kontext (Domänenkontext,
Experiment- und Prüfungsdokumentation, Wissensstand, Fragenpool) darf weder „1.2496“, „1,2496“, „sqrt(17)“, „√17“ noch „17“ im Umkreis von
40 Zeichen um „Seitenverh“/„aspect“/„y_inf“ enthalten; sonst Abbruch.

**Bedingungen** (gleicher Auftrag, gleiche Modelle = Kaskade haiku→haiku→sonnet→sonnet, gleiches Budget):
- **LAB:** volles Labor (`asd.lab_loop`): Integrator wählt Fragen, Code-Planer (`asd/planner.py`) wählt das Vorgehen, Forscher-Kaskade mit
  Stärke-Maximierung, Verifier-Rückmeldung (bestätigte und abgelehnte Behauptungen mit Grund im Kontext der nächsten Runde), Red-Team, Lernen.
- **OHNE_FEEDBACK:** dieselben Forscher (Strategie/Modell reihum aus der Kaskade), aber unabhängige Versuche am Auftrag ohne jede
  Rückmeldung des Verifiers oder früherer Versuche.
- **ZUFALL:** Teilfragen aus einem festen, handgeschriebenen Pool (`benchmarks/replay_pool.json`, enthält den Auftrag selbst) in zufälliger
  Reihenfolge, Strategie/Modell zufällig, kein Integrator, kein Lernen, keine Rückmeldung.
- **CLAUDE_PUR (explorativ, nur falls Zeit; nicht Teil der Hypothese):** ein einzelner `claude -p`-Agent mit Python, am Ende einmal Verifier.

**Seeds:** 10 je Bedingung (1000–1009); der Seed geht als Salt in jeden LLM-Aufruf (reproduzierbar über `cache/llm`).
**Budget:** 30 Verifier-Aufrufe je Lauf (alle `Domain.check`-Aufrufe zählen, auch Red-Team; der Selbsttest nicht).
**Metrik:** N = Verifier-Aufrufe bis zum ersten Treffer, N = 31 bei Scheitern. Zusätzlich: Wanduhrzeit, Zahl abgelehnter Behauptungen.

**H7a (primär):** LAB braucht weniger Verifier-Aufrufe als ZUFALL. **H7b:** LAB braucht weniger als OHNE_FEEDBACK.
Test: gepaarter einseitiger Vorzeichen-Flip-Permutationstest über die 10 Seeds (20 000 Permutationen); Speedup = mittleres N(Vergleich) /
mittleres N(LAB) mit gepaartem Bootstrap-95-%-KI (5000 Ziehungen). Erfolg je Hypothese: p < 0,05 UND KI-Untergrenze > 1.
Benjamini-Hochberg über H7a, H7b (m = 2, q = 0,1). Trefferquote je Bedingung mit exaktem Clopper-Pearson-95-%-KI.
Ergebnisse werden berichtet, egal wie sie ausfallen. Menschliche Baseline wird NICHT gemessen; die Angabe „Paper in einer Nacht, ca. 12–14 h“
ist eine Schätzung des Autors.
