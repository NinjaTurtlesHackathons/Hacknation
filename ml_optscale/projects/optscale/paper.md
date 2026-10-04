# Spektren, Rotation und Breite: ein verifikator-gesteuertes Agentenlabor zu Optimierern und Skalierungsgesetzen

Verifier-Gated Discovery Lab, Team Ninja Turtles, Hack-Nation 2026, Challenge 3

## 1 Einleitung

**Frage.** Warum funktionieren moderne Optimierer und Lernraten-Schedules, wann überträgt sich die Lernrate über die Modellbreite, und woher stammen die Exponenten von Skalierungsgesetzen? Diese Arbeit berichtet, was ein verifikator-gesteuertes Agentenlabor darauf numerisch belegen konnte und was nicht.

**Kontext.** Die Literaturlage im Labor ist folgende:
- Das spektrale Schrittweitenprofil (volatiler Kopf an der Stabilitätsgrenze, toleranter Bulk) wird als Erklärung dafür angeführt, dass Muon Adam und Adam SGD übertrifft [C-lit3] (arXiv:2608.25990v1).
- Im linearen Assoziativspeicher-Modell mit Potenzgesetz-Spektrum wird Muons Skalierungsgesetz hergeleitet und seine bessere Skalierungseffizienz gegenüber GD gezeigt [C-lit8] (arXiv:2602.05725v3).
- Unter μP bleiben viele optimale Hyperparameter über Modellgrößen stabil [C-lit29] (arXiv:2203.03466v2).

**Beitrag.** Das Labor prüft solche Aussagen in numerischen Modellwelten. Eine Behauptung gilt nur, wenn ein unabhängiger Code-Prüfer sie mit eigenen Seeds, eigenem Lernraten-Tuning und eigener Auflösung nachrechnet. Red-Team-Gegenprüfungen versuchen jede Aussage zu widerlegen.

**Zusammenfassung der Resultate.**
- Gradientenfluss: Die Verlustexponenten stimmen an vier geprüften (a, b)-Paaren mit den behaupteten Werten überein (Befund I) [C-optscale-R17].
- Rechenoptimum bei C = P·t: Es wurden sieben (a, b)-Punkte bestätigt, und die Alternative "reiner Gradientenfluss-Exponent" wurde nicht gezeigt (Befund II) [C-optscale-R6] [C-optscale-R8] [C-optscale-R9].
- Random-Feature- und Ridge-Exponenten sind nur an wenigen Punkten bestätigt. In Regimen mit kleinem a und großem b liegen die Fits unter dem Abschneide-Exponenten, und die asymptotischen Exponenten sind ungeklärt (Befunde III und IV) [C-optscale-R1-RT1] [C-optscale-R1-RT2].
- Muon gegen Adam hängt von Rotation und Spektrum ab. Rotation allein entscheidet das Vorzeichen nicht (Beobachtungen V und VI) [C-optscale-R2] [C-optscale-R4] [C-optscale-R5].
- Unter heavy-tailed Rauschen schlagen Shampoo und Muon SGD (Beobachtung VII) [C-optscale-R13].
- Lernraten-Schedules senken den Endverlust in den geprüften Fällen (Beobachtung VIII) [C-optscale-R15].
- Edge of Stability tritt bei einer geprüften Lernrate in allen fünf Seeds auf (Befund IX) [C-optscale-R16].
- Für GD und Heavy-Ball auf einer rationalen Quadratik liegen exakte Stabilitätszertifikate vor (Proposition 1) [C-optscale-R18].
- μP überträgt die optimale Lernrate über Breiten, SP nicht (Befund X) [C-optscale-R10].

## 2 Modell

Die Annahmen, die die Resultate tragen, stehen jeweils in den Prüfaufträgen der Claims.

- **Lineares Modell mit Potenzgesetz-Spektrum.** Die Eigenwerte sind lambda_k = k^-a und die Zielanteile k^-b [C-optscale-R1] [C-optscale-R17]. Betrachtet werden der Gradientenfluss-Verlust über die Zeit t, der Verlust des linearen Random-Feature-Modells über P [C-optscale-R1], der Exzess-Risiko-Verlauf der Ridge-Regression über N [C-optscale-R12] und das rechenoptimale Budget C = P·t [C-optscale-R6]. Ein Exponent e bedeutet Verlust ~ x^-e.
- **Optimierer auf Quadratiken.** Es geht um Kronecker-Krümmung mit Spektren a_L und a_R, wahlweise rotiert. Verglichen werden adam, muon, shampoo, sgd, signum und weitere mit Schedules (const, cosine, wsd) bei selbst getunter Lernrate [C-optscale-R2] [C-optscale-R13] [C-optscale-R15]. Die Metrik ist der relative Endverlust.
- **Edge of Stability.** Voll-Batch-GD auf einem tanh-Netz, Kenngröße lr·lambda_max/2 [C-optscale-R16].
- **μP gegen SP.** Es wird geprüft, ob sich die optimale Lernrate mit der Breite verschiebt [C-optscale-R10].
- **Exakte Anker.** GD und Heavy-Ball auf Quadratiken mit rationaler Matrix H, mit der Stabilitätsbedingung |beta| < 1, H > 0 und H < 2(1+beta)/lr [C-optscale-R18].

## 3 Methode: das agentische Labor

Das Labor lief 18 Runden, 18 geprüfte Aussagen, 0 negative Ergebnisse, Kosten 8.86 USD [C-methode]. Jede Runde wurde vor dem Experiment präregistriert (prereg.md) [C-methode].

Die Claims dokumentieren drei Mechanismen:
1. **Code-Prüfer.** Er rechnet mit eigenen Seeds nach, tunet die Lernrate selbst und fittet Exponenten in zwei Fenstern mit fester Toleranz. Für exakte Anker verwendet er rationale Arithmetik [C-optscale-R17] [C-optscale-R18].
2. **Red-Team.** Es formuliert Gegenprüfungen zu jeder Aussage. Eine Aussage gilt als *angefochten*, sobald eine Gegenprüfung besteht, auch wenn diese mit der Aussage vereinbar ist. Angefochten sind optscale-R7, optscale-R15 und optscale-R18. Im Einzelfall ist zu lesen, ob die bestandene Gegenprüfung der Aussage widerspricht [C-redteam-methode].
3. **Präregistrierte Mehrfachtest-Korrektur.** Benjamini-Hochberg mit q = 0.1 über alle 20 Optimierer-Vergleiche des Prüfers [C-bh]. Prüfungen mit Lernraten-Optimum am Gitterrand gelten als nicht entscheidbar und zählen nicht als Test [C-bh].

Die Rollen Scout, Integrator und Forscher sind in der Claim-Liste nicht beschrieben und werden hier nicht weiter ausgeführt.

**Lesregel.** Eine nicht bestandene Gegenprüfung zeigt nur, dass ihre Behauptung nicht gezeigt ist, nicht das Gegenteil. Die allgemeine Formel hinter mehreren geprüften Einzelpunkten ist eine Interpretation, kein Theorem.

## 4 Resultate

### 4.1 Skalierung im linearen Modell

**Numerischer Befund I (observed).** Der Gradientenfluss-Verlust über t fällt an vier Punkten mit den Prüfer-Exponenten in beiden Fenstern innerhalb der Toleranz 0.03 wie behauptet [C-optscale-R17]:

| (a, b) | Exponent | Beleg |
|---|---|---|
| (1.0, 2.0) | 1.0 | [C-optscale-R17] |
| (1.0, 3.0) | 2.0 | [C-optscale-R17] |
| (2.0, 4.0) | 1.5 | [C-optscale-R17] |
| (0.5, 1.5) | 1.0 | [C-optscale-R17] |

Zusätzlich lieferte der Prüfer bei (a=2.0, b=3.0) den Exponenten 1.0000 [C-optscale-R17-RT1] und bei (a=0.5, b=3.0) den Exponenten 4.0000 [C-optscale-R17-RT2]. Beide Werte liegen in beiden Fenstern vor. Die Alternative e = (b−1)·a wurde nicht gezeigt [C-optscale-R17-RT1] [C-optscale-R17-RT2].

**Numerischer Befund II (observed).** Der rechenoptimale Verlust bei Budget C = P·t fällt an folgenden Punkten wie behauptet, mit Toleranz 0.03 [C-optscale-R6] [C-optscale-R8] [C-optscale-R9]:

| (a, b) | Exponent | Beleg |
|---|---|---|
| (1.0, 2.0) | 0.5 | [C-optscale-R6] |
| (2.0, 3.0) | 0.6667 | [C-optscale-R6] |
| (1.0, 4.0) | 1.5 | [C-optscale-R6] |
| (1.5, 1.5) | 0.2 | [C-optscale-R6] |
| (0.5, 2.0) | 0.6667 | [C-optscale-R8] |
| (1.0, 3.0) | 1.0 | [C-optscale-R8] |
| (2.0, 2.0) | 0.3333333333 | [C-optscale-R9] |

Die Gegenhypothese des reinen Gradientenfluss-Exponenten (b−1)/a wurde nicht gezeigt. Bei (a=2.0, b=3.0) lieferte der Prüfer 0.6658 und 0.6663 statt 1.0 [C-optscale-R6-RT1]. Bei (a=3.0, b=4.0) lieferte er 0.7474 und 0.7484 statt 1.0 [C-optscale-R6-RT2].

Die Formel C^-(b−1)/(a+1) fasst diese Punkte zusammen. Sie ist eine Interpretation [C-optscale-R6-I] und kein Resultat.

Die Claims R8 und R9 fragen nach dem Budget C = P·N mit Random-Feature und Ridge. Die vom Prüfer geprüfte Kurve ist jedoch die Gradientenfluss-Kurve "compute", nicht die RF-Ridge-Kurve [C-optscale-R8-RT2]. Auch R7 stellt die Frage nach einem RF-basierten Optimum. Bestätigt ist dort nur der RF-Exponent über P bei (1.0, 2.0) (Befund III), während die bestandenen Gegenprüfungen wiederum die Gradientenfluss-Kurve betreffen [C-optscale-R7] [C-optscale-R7-RT1] [C-optscale-R7-RT2]. Der Exponent für C = P·N bleibt daher ungeprüft (siehe die Abschnitte zu negativen Ergebnissen und zu Grenzen).

**Numerischer Befund III (observed).** Der Verlust des linearen Random-Feature-Modells über P fällt an zwei Punkten wie x^-1.0 (Toleranz 0.1) [C-optscale-R1] [C-optscale-R11]:
- bei (a=1.0, b=2.0) mit Exponenten 0.9909 und 1.0540 [C-optscale-R1];
- bei (a=2.0, b=2.0) mit Exponenten 1.0782 und 1.0806 [C-optscale-R11].

**Numerischer Befund IV (observed).** Der Exzess-Risiko-Verlust der Ridge-Regression über N (a=1.0, b=3.0, ridge = 0.001, noise = 0) fällt wie x^-2.0, mit Exponenten 1.9893 und 1.9258 (Toleranz 0.1) [C-optscale-R12].

### 4.2 Optimierer auf Quadratiken

**Beobachtung V (statistical).** Ohne Rotation bei (a_L, a_R) = (3.0, 3.0) und 500 Schritten erreicht Adam (const) einen kleineren relativen Endverlust als Muon (const) [C-optscale-R2] [C-optscale-R3]. Die Werte sind 4.932e-23 gegen 2.825e-04, mit p = 0.0008 auf 10 frischen Seeds und eigenem Tuning (beste Lernraten 2^-2 und 2^-5) [C-optscale-R2] [C-optscale-R3].

**Beobachtung VI (statistical).** Mit Rotation hängt das Vorzeichen vom Spektrum ab [C-optscale-R4] [C-optscale-R5] [C-optscale-R14]:

| (a_L, a_R) | Befund | Verlust Muon / Adam | Verhältnis | Beleg |
|---|---|---|---|---|
| (3.0, 3.0) | Muon besser | 4.481e-04 / 1.810e-03 | 0.248 (p = 0.0008) | [C-optscale-R4] |
| (2.5, 2.5) | Muon besser | 1.814e-04 / 1.683e-03 | 0.108 (p = 0.0008) | [C-optscale-R14] |
| (1.0, 1.0) | Adam besser | 8.863e-05 / 3.170e-11 | p = 0.0041 | [C-optscale-R4] [C-optscale-R5] |

Rotation allein entscheidet das Vorzeichen daher nicht. Bei (3.0, 3.0) kehrt es sich zwischen unrotiert und rotiert um [C-optscale-R2] [C-optscale-R4]. Bei (1.0, 1.0) rotiert gewinnt Adam [C-optscale-R5]. Die geprüften Punkte begrenzen den Wechsel auf das Intervall zwischen a = 1.0 und a = 2.5 [C-optscale-R5] [C-optscale-R14]. Seine genaue Lage ist nicht bestätigt.

Der Befund bei (1.0, 1.0) steht in den Claims R4 und R5. Der BH-Eintrag zu R5 nennt zudem ein Verhältnis 0.107 für Muon gegen Adam, ohne den zugehörigen Punkt auszuweisen [C-optscale-R5] [C-bh].

**Beobachtung VII (statistical).** Unter Student-Rauschen (df = 2, sigma = 0.1) auf der rotierten Quadratik mit (a_L, a_R) = (2.0, 2.0) erreichen Shampoo und Muon kleinere Endverluste als SGD [C-optscale-R13]:

| Vergleich | Verlust | Verhältnis | Beleg |
|---|---|---|---|
| Shampoo gegen SGD | 5.032e-02 / 9.663e-02 | 0.521 | [C-optscale-R13] |
| Muon gegen SGD | 5.483e-02 / 9.663e-02 | 0.567 | [C-optscale-R13] |

Beide haben p = 0.0008 [C-optscale-R13]. Die Claims bestätigen keinen Vergleich von Clipping gegen SGD und keinen Vergleich von Adam oder Signum gegen SGD zugunsten der anderen Seite (siehe den Abschnitt zu negativen Ergebnissen).

### 4.3 Schedules

**Beobachtung VIII (statistical, angefochten).** Auf der rotierten Quadratik mit (2.5, 2.5) und Gauss-Rauschen (sigma = 0.1) erreicht Adam mit Cosine-Schedule einen kleineren Endverlust als mit const [C-optscale-R15]. Die Werte sind 1.142e-02 gegen 3.190e-02, Verhältnis 0.358, p = 0.0008 [C-optscale-R15].

Der Befund ist nicht auf Cosine mit Adam beschränkt. SGD mit WSD schlägt SGD mit const unter Student-Rauschen (df = 3): 1.422e-02 gegen 2.563e-02, Verhältnis 0.555 [C-optscale-R15-RT2] [C-bh]. Die Anfechtung beruht auf dieser bestandenen Gegenprüfung, die den Befund erweitert, ihm aber nicht widerspricht [C-redteam-methode].

### 4.4 Edge of Stability

**Numerischer Befund IX (observed).** Voll-Batch-GD auf dem tanh-Netz (Breite 16, lr = 1.0, 2000 Schritte) hat am Ende lr·lambda_max/2 in [0.85, 1.25], und zwar in 5 von 5 frischen Seeds [C-optscale-R16]. Die Werte bei 80 % und 100 % der Schritte liegen zwischen 0.958 und 1.152, gemessen am vollen Hesse-Eigenwert [C-optscale-R16].

**Proposition 1 (computed_rigorous; optscale-R18 ist angefochten).** Exakte Zertifikate in rationaler Arithmetik auf H = diag(1, 2) [C-optscale-R18] [C-optscale-R18-RT1] [C-optscale-R18-RT2]:
- GD mit lr = 99/100 ist stabil, mit lr = 101/100 nicht [C-optscale-R18].
- GD mit lr = 1 ist nicht stabil. Das ist der Randfall 2/lr = 2 mit Spektralradius 1 [C-optscale-R18-RT1].
- Heavy-Ball mit lr = 3/2 und beta = 9/10 ist stabil (Grenze 38/15) [C-optscale-R18].
- Heavy-Ball mit lr = 19/10 und beta = 9/10 ist nicht stabil [C-optscale-R18-RT2].

Die Anfechtung beruht auf den bestandenen Gegenprüfungen zu lr = 1 und lr = 19/10 [C-optscale-R18-RT1] [C-optscale-R18-RT2]. Diese sind mit der Aussage vereinbar, da sie genau die Randfälle der Bedingung H < 2(1+beta)/lr belegen [C-redteam-methode].

### 4.5 μP gegen SP

**Numerischer Befund X (observed).** Optimale log2-Lernraten über die Breiten 32, 64, 128, 256 (Gitter mit Faktor 2, 300 Schritte, 2 Seeds) [C-optscale-R10]:

| Parametrisierung, Optimierer | Optima (kleinste bis größte Breite) | Verschiebung | Spannweite | Kriterium | Beleg |
|---|---|---|---|---|---|
| μP, Adam | -7/-6/-7/-7 | 0 | 1 | Transfer | [C-optscale-R10] |
| SP, Adam | -6/-6/-7/-8 | -2 | 2 | kein Transfer | [C-optscale-R10] |
| μP, SGD | -1/-1/0/-1 | 0 | 1 | Transfer | [C-optscale-R10] |
| SP, SGD | 0/-1/-1/-2 | -2 | 2 | kein Transfer | [C-optscale-R10] |

Dieser Befund ist verträglich mit dem berichteten μP-Transfer in der Literatur [C-lit29] (arXiv:2203.03466v2).

### 4.6 Mehrfachtest-Korrektur

**Beobachtung XI (statistical).** Von 20 eindeutigen Optimierer-Vergleichen des Prüfers bleiben nach Benjamini-Hochberg (q = 0.1) 11 signifikant mit Verhältnis unter 0.9 [C-bh]. Das sind die Hauptprüfungen von R2, R3, R4, R5, R13, R14 und R15 sowie die Gegenprüfung R15-RT2 [C-bh]. Die nicht signifikanten Tests sind Gegenprüfungen mit p_adj = 1.0, außer R4-RT2 mit p = 0.9967 und R13-RT2 mit p = 0.994 [C-bh].

## 5 Negative Ergebnisse und Red-Team-Befunde

Nicht bestandene Gegenprüfungen belegen nur, dass ihre Behauptung nicht gezeigt ist.

**Skalierung (Gegenprüfungen nicht bestanden).**
- **Random-Feature-Exponent über P bei kleinem a und großem b.** Die Behauptungen eines RF-Exponenten von 1.0 bei (a=0.5, b=3.5) und von 0.6 bei (a=0.3, b=4.0) sind nicht gezeigt [C-optscale-R1-RT1] [C-optscale-R1-RT2]. Die Prüfer-Fits sind 0.6189 und 0.7694 bzw. 0.3146 und 0.4394 [C-optscale-R1-RT1] [C-optscale-R1-RT2]. Auch die Behauptung 1.0 bei (a=0.5, b=3.0) ist nicht gezeigt (0.6077 und 0.7600) [C-optscale-R11-RT1]. Alle Fits liegen unter den im Red-Team genannten Abschneide-Exponenten 2,5 bzw. 3 und steigen mit dem Fenster [C-optscale-R1-RT1] [C-optscale-R1-RT2]. Die Sättigungsformel P^-min(b-1, 2a) ist dadurch nicht bestätigt, und der asymptotische Exponent bleibt offen.
- **Ridge-Exponent über N in Sättigungsregimen.** Nicht gezeigt sind 1.0 bei (a=0.5, b=3.0, 1.4644 und 1.8149) [C-optscale-R12-RT1], 0.8 bei (a=0.4, b=4.0, 1.2112 und 1.5759) [C-optscale-R12-RT2] und 2.0 bei (a=1.0, b=4.0, 2.5008 und 2.7484) [C-optscale-R9-RT2]. Die rauschbehaftete Behauptung 0.5 bei (a=2.0, b=2.0, noise = 1.0) ist ebenfalls nicht gezeigt, die Fits sind -0.1666 und -0.2154 [C-optscale-R11-RT2].
- **RF-Exponent bei C = P·N.** Nicht gezeigt sind 0.5 bei (a=2.0, b=2.0, Fits 1.0782 und 1.0806) und 1.0 bei (a=2.0, b=3.0, Fits 1.8814 und 1.8742) [C-optscale-R8-RT1] [C-optscale-R8-RT2]. Auch der behauptete compute-Exponent 1.2 bei (a=1.0, b=4.0) ist nicht gezeigt; der Prüfer maß dort 1.4990 und 1.4998 [C-optscale-R9-RT1].

**Optimierer (Gegenprüfungen nicht bestanden).**
- Muon gleich gut oder besser als Adam bei a = 0.1 ohne Rotation ist nicht gezeigt [C-optscale-R3-RT2]. Gemessen wurden 1.162e-05 gegen 3.883e-23 [C-optscale-R3-RT2]. Auch rotiert bei a = 0.1 ist Muon nicht besser (1.131e-05 gegen 3.873e-23) [C-optscale-R5-RT2].
- Adam besser als Muon im rotierten Fall mit Ungleichgewicht a_L ≠ a_R ist nicht gezeigt (2.605e-04 gegen 3.093e-05) [C-optscale-R2-RT2] [C-optscale-R3-RT1]. Dieselben Zahlen stehen in beiden Claims.
- Muon besser als Adam bei (1.0, 1.0) rotiert ist nicht gezeigt (8.863e-05 gegen 3.170e-11) [C-optscale-R4-RT2] [C-optscale-R5-RT1].
- Adam besser als Muon bei a = 2.5 und a = 3.0 rotiert ist nicht gezeigt [C-optscale-R14-RT1] [C-optscale-R14-RT2].
- SGD besser als Adam oder Signum unter Student-Rauschen ist nicht gezeigt (9.663e-02 gegen 8.435e-02 bzw. 8.455e-02) [C-optscale-R13-RT1] [C-optscale-R13-RT2].
- Cosine besser als const bei SGD im MLP ist nicht gezeigt (4.859e-03 gegen 3.732e-03) [C-optscale-R15-RT1].

**Nicht entscheidbar.** Bei der Gegenprüfung zu Shampoo ohne Rotation und bei Shampoo gegen Adam bei (3, 3) rotiert lag das Lernraten-Optimum am Gitterrand 2^-16..2^4 [C-optscale-R2-RT1] [C-optscale-R4-RT1]. Sie sind weder bestanden noch widerlegt und zählen nicht als Test [C-bh].

**EOS (Gegenprüfungen nicht bestanden).** Der EOS-Wert am Ende ist nicht unter Wert 1 gedrückt (Werte 0.958 bis 1.152) [C-optscale-R16-RT1]. Dass EOS bei kleinerer Lernrate in 4000 Schritten erreicht wird, ist nicht gezeigt [C-optscale-R16-RT2]. Dort liegen die Werte zwischen 0.595 und 0.896 [C-optscale-R16-RT2].

**μP und SGD (Gegenprüfungen nicht bestanden).** Der Befund "SGD unter SP verschiebt sich nicht" und der Befund "SGD unter μP verschiebt sich um mehr als eine Gitterstufe" sind beide nicht gezeigt [C-optscale-R10-RT1] [C-optscale-R10-RT2].

## 6 Grenzen und offene Fragen

- **Formeln sind Interpretationen.** Die Formeln e = (b−1)/a [C-optscale-R17-I] und C^-(b-1)/(a+1) [C-optscale-R6-I] sind ungeprüfte Interpretationen mehrerer geprüfter Einzelpunkte, keine Theoreme. Ebenso ungeprüft sind die Aufteilung P_opt ~ C^(1/(1+a)), t_opt ~ C^(a/(1+a)) [C-optscale-R6-I] und die vermutete Sättigung der Random-Feature- und Ridge-Exponenten bei 2a [C-optscale-R12-I].
- **Rechenoptimum bei C = P·N.** Der Exponent für Random-Feature plus optimierte Ridge ist nicht bestätigt. Das gilt auch für die Zerlegung in e_P und e_N [C-optscale-R9] [C-optscale-R11-I]. Die Fits in Regimen mit kleinem a und großem b sind fensterabhängig (siehe den Abschnitt zu negativen Ergebnissen) [C-optscale-R1-RT1] [C-optscale-R1-RT2].
- **Lage und Art des Muon-Adam-Wechsels.** Die genaue Lage zwischen a = 1.0 und a = 2.5 und die Frage "Phasenübergang oder glatter Übergang" sind offen [C-optscale-R5] [C-optscale-R14] [C-optscale-R4-I]. Die Rotation ist nur binär steuerbar, graduelle Rotation wurde nicht getestet [C-optscale-R4-I]. Die Hypothese "Rotation sei der alleinige Treiber" [C-optscale-R3-I] ist durch die geprüften Punkte mit Rotation und Adam-Vorteil bei (1.0, 1.0) nicht gedeckt [C-optscale-R5]. Die Hypothese eines Wechsels zwischen 1.0 und 1.5 [C-optscale-R5-I] ist ungeprüft.
- **Shampoo.** Der Vergleich mit Adam ohne und mit Rotation ist wegen Randoptima nicht entscheidbar [C-optscale-R2-RT1] [C-optscale-R4-RT1]. Zu Clipping, Signum und Adam unter heavy-tailed Rauschen liegt kein bestätigter Vorteil gegenüber SGD vor [C-optscale-R13]. Die Literatur zu heavy-tailed Konvergenzraten [C-lit18] (arXiv:2602.07425v2) ist nicht mit eigenen Messungen verknüpft.
- **Schedules.** Bestätigt sind nur Adam/cosine bei Gauss-Rauschen und SGD/wsd bei Student-Rauschen mit df = 3 [C-optscale-R15] [C-optscale-R15-RT2]. Dass Schedules im MLP helfen, ist nicht gezeigt [C-optscale-R15-RT1].
- **EOS.** Die Schwelle der Lernrate, ab der EOS auftritt, ist nicht bestimmt. Gezeigt ist nur ein Punkt bei Breite 16 [C-optscale-R16].
- **μP gegen SP.** Der Transfer ist nur an vier Breiten mit grobem Faktor-2-Gitter, wenigen Schritten und 2 Seeds geprüft. Die Verschiebung pro Breitenverdopplung ist nicht quantifiziert [C-optscale-R10] [C-optscale-R10-I].
- **Exakte Anker.** Die Zertifikate betreffen nur diagonale rationale Matrizen und einzelne Lernraten [C-optscale-R18].
- **Statistik.** Die BH-Korrektur deckt nur die 20 Optimierer-Vergleiche ab, nicht die Exponenten-Fits [C-bh].

## Literatur

Nur Quellen aus Claims:
- arXiv:2203.03466v2 [C-lit29] [C-lit30]
- arXiv:2602.05725v3 [C-lit8] [C-lit9]
- arXiv:2602.07425v2 [C-lit18]
- arXiv:2608.25990v1 [C-lit3] [C-lit4]

---
Prüfprotokoll: 72 Claims zitiert, Korrekturrunden [{"runde": 0, "verstoesse": 54}, {"runde": 1, "verstoesse": 8}, {"final_verstoesse_entfernt": 0}], 0 unbelegte Sätze entfernt, verbleibende Verstöße: 0.
