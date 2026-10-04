# Moderationsleitfaden · AI Agent Lab

## 3-Minuten-Demo

**0:00–0:25 · Die Frage**

Öffne `index.html`, Bereich **Labor**, Konstruktion **111 Punkte**.

„Jedes Paar von Punkten hat einen Abstand. Unsere Forschungsfrage lautet: Wie viele Punkte können wir anordnen, wenn nur 41 verschiedene Längen vorkommen dürfen?“

„Hier sind 111 Punkte. Ihre 6.105 Paarungen verwenden zusammen nur 41 verschiedene Längen.“

**0:25–1:00 · Die Geometrie**

Wähle nacheinander q = 1, q = 111 und q = 127. q bezeichnet den **quadrierten** Abstand.

„Die kurze Gitterlänge kommt oft vor. Die Länge √111 kommt überhaupt nicht vor. Dafür kommt die längere Länge √127 genau sechsmal vor. Die Gesamtzahl bleibt bei 41.“

„Diese Auswahl von Längen hilft bei der Konstruktion. Der allgemeine Gedanke, Abstandsklassen auszutauschen, ist bekannt; unser Beitrag ist die konkret verbesserte Punktmenge.“

**1:00–1:35 · Der Gewinn**

Öffne **Ergebnis**.

„Ahmed und Snevily veröffentlichten 2013 eine Konstruktion mit 109 Punkten und 41 Abständen. Die neue Konstruktion hat 111. Ein zweiter Fund verbessert ihren Vergleichswert bei 31 Abständen von 80 auf 81 Punkte.“

„Die Bilder zeigen unsere neuen Formen. Die historischen Formen haben wir hier nicht nachgebildet.“

**1:35–2:20 · Der Nachweis**

Öffne **Nachweis** und starte die Verifikation. Lass die echte Berechnung durchlaufen.

„Die Suchsoftware ist für den Beweis nicht mehr nötig. Wir erzeugen die Punkte aus zehn Ungleichungen und berechnen alle Paare mit Ganzzahlen. Keine numerische Toleranz entscheidet darüber, ob zwei Abstände gleich sind.“

„Auch jede einzelne Paarhäufigkeit stimmt mit dem Zertifikat überein. Der Python-Prüfer ist mitgeliefert und läuft ohne zusätzliche Pakete.“

**2:20–3:00 · Das Agentenlabor**

Öffne **Quellen & Prozess**.

„Laut Forschungsprotokoll stellte der Mensch das Ziel und die Ressourcen bereit. Agenten entwickelten die Suche, fanden eine Konstruktion, entwickelten sie weiter und kontrollierten die Resultate mit separat implementierten Prüfern.“

„Der mathematische Gewinn ist klein und exakt. Für das Lab ist interessant, dass aus einer offenen Frage ein Ergebnis mit überprüfbarem Zertifikat entstand.“

Schlusssatz: **„AI-Agenten fanden zwei geometrische Konstruktionen, die publizierte Schranken aus einer Arbeit von 2013 verbessern. Das Ergebnis kann jeder exakt nachprüfen.“**

## Fragen aus dem Publikum

**Ist das die optimale Lösung?**

Das ist nicht bewiesen. Die Konstruktionen zeigen G(31) ≥ 81 und G(41) ≥ 111, keine Gleichheit.

**Ist das ein Weltrekord?**

Es verbessert die genannten publizierten Vergleichswerte. Die geprüften Quellen liefern keinen Beweis vollständiger weltweiter Literaturabdeckung. Deshalb lautet die Aussage „verbesserte publizierte untere Schranken“.

**Hat die KI ein Erdős-Problem gelöst?**

Sie hat zwei untere Schranken in einem von Erdős und Fishburn untersuchten Problem verbessert. Das allgemeine Problem ist damit nicht gelöst.

**Was ist daran neu, wenn ein Optimierer die Suche macht?**

Die konkreten verbesserten Konstruktionen können neue mathematische Ergebnisse sein. Die eingesetzten Optimierungswerkzeuge und der allgemeine Abstandsklassen-Austausch sind bekannt. Das Lab-Ergebnis ist kein Nachweis einer neuen universellen Suchmethode.

**Ist das autonom entstanden?**

Das Manuskript beschreibt Agentenarbeit nach einem menschlichen Forschungsauftrag. Die genaue Prozesszuordnung stammt aus dem Manuskript. Dieses Demo-Paket auditiert nicht selbst sämtliche Agentenprotokolle oder menschlichen Eingriffe.

**Wie lange hat die Forschung gebraucht?**

Das Manuskript nennt Laufzeiten einzelner Suchinstanzen. Diese dürfen nicht als Gesamtzeit der Forschung ausgegeben werden. Ohne vollständige Zeit- und Kostenabrechnung keine Gesamtzahl nennen.

## Folien-Sprechernotizen

1. **Titel:** Eine präzise, überprüfbare Entdeckung zeigen. Nicht mit „Weltrekord“ eröffnen.
2. **Frage:** Viele Paarungen können dieselbe Länge besitzen; „41 Abstände“ meint verschiedene Längen.
3. **Vergleich:** +1 und +2 Punkte gegenüber den Originalwerten auf Seite 5 der Publikation von 2013.
4. **Geometrie:** Bei 111 Punkten √111 fehlt, √127 tritt hinzu. Keine Animation als historischen Suchlauf ausgeben.
5. **Prüfung:** Zum Labor wechseln. Die Paarprüfung ist eine reale lokale Rechnung.
6. **Impact:** Konkrete Schrankenverbesserung plus überprüfbarer Forschungsprozess. Globale Optimalität offen.

## Kurze Caption für eine Grafik

„AI Agent Lab: 111 Punkte mit genau 41 verschiedenen Abständen. Die exakte Konstruktion verbessert den publizierten Vergleichswert von Ahmed–Snevily (2013) um zwei Punkte. Sämtliche 6.105 Punktpaare sind mit Ganzzahlarithmetik überprüfbar. Globale Optimalität ist offen.“
