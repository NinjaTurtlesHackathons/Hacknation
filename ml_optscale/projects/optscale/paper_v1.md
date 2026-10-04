# Spektren, Rotation und Breite: ein verifikator-gesteuertes Agentenlabor zu Optimierern und Skalierungsgesetzen

Verifier-Gated Discovery Lab, Team Ninja Turtles, Hack-Nation 2026, Challenge 3

# Spektren, Rotation und Breite: ein verifikator-gesteuertes Agentenlabor zu Optimierern und Skalierungsgesetzen

## Zusammenfassung

Ein agentisches Labor untersucht vier numerische Modellwelten: ein lineares Modell mit Potenzgesetz-Spektrum, Optimierer auf Matrix-Quadratiken und im MLP, Edge of Stability sowie μP gegen SP. Als Resultat gilt nur, was ein unabhängiger Code-Prüfer mit eigenen Seeds, eigenem Lernraten-Tuning und eigener Auflösung nachgerechnet hat. Ungeprüfte Interpretationen der Agenten (Claims mit Suffix „-I") werden nicht als Resultat verwendet. Evidenzstufen stehen in Klammern, Claim-IDs in eckigen Klammern.

## 1 Einleitung

**Frage.** Warum funktionieren moderne Optimierer und Lernraten-Schedules? Wann überträgt sich die Lernrate über die Modellbreite? Woher kommen die Exponenten von Skalierungsgesetzen? Ein Skalierungsexponent e bedeutet Verlust ~ x^-e.

**Beitrag.** Das Labor lief 18 Runden mit 18 geprüften Aussagen bei Kosten von 8.86 USD, und jede Runde wurde vor dem Experiment präregistriert [C-methode]. Jede Aussage wurde durch Red-Team-Gegenprüfungen angegriffen.

**Resultate in Kürze:**

- Der Gradientenfluss-Exponent und der rechenoptimale Exponent bei C = P*t sind an allen geprüften Punkten numerisch bestätigt, die Gegenhypothesen scheitern [C-optscale-R6, C-optscale-R17].
- Für das Random-Feature-Modell und die Ridge-Regression bei kleinem a und großem b ist der asymptotische Exponent offen. Die gemessenen Steigungen liegen deutlich unter dem Abschneide-Exponenten [C-optscale-R1-RT1, C-optscale-R1-RT2].
- Muon gegen Adam hängt von Rotation und Spektrum ab. Es gibt keine universelle Regel [C-optscale-R2, C-optscale-R4, C-optscale-R5, C-optscale-R14].
- Unter μP überträgt sich die optimale Lernrate über die Breiten für Adam und SGD, unter SP nicht [C-optscale-R10].
- Voll-Batch-GD befindet sich bei der geprüften Lernrate an der Edge of Stability [C-optscale-R16].
- Exakte Stabilitätszertifikate für Gradientenabstieg und Heavy-Ball sind erbracht [C-optscale-R18].

## 2 Modell

Vier Welten, alle numerisch (numpy):

- **Lineares Modell:** Eigenwerte lambda_k = k^-a, Zielanteile lambda_k w_k^2 = k^-b mit b > 1 [C-optscale-R17].
- **Optimierer:** sgd, momentum, adam, signum, clip_sgd, muon und shampoo auf Matrix-Quadratiken (Kronecker-Krümmung, wahlweise rotiert, Gauß- oder Student-Rauschen) und im tanh-Lehrer-Schüler-MLP. Die Schedules sind const, cosine, linear und wsd. Die Metrik ist der relative Endverlust [C-optscale-R15].
- **Edge of Stability:** Voll-Batch-GD auf einem kleinen tanh-Netz mit der Kenngröße lr*lambda_max/2 [C-optscale-R16].
- **μP gegen SP:** 3-Schicht-ReLU-MLP. Bei Basisbreite 64 sind μP und SP identisch [C-optscale-R10-RT2].

Exakte Anker bieten quadratische Iterationen mit rationaler Krümmungsmatrix [C-optscale-R18].

## 3 Methode: das agentische Labor

Das Labor besteht aus Scout, Integrator, Forscher, Code-Prüfer, Red-Team und Präregistrierung [C-methode]. Für Optimierervergleiche tunt der Prüfer die Lernrate je Arm selbst auf den Seeds 100, 101 und 102 [C-optscale-R2]. Er bewertet auf 10 frischen Seeds mit einem gepaarten Permutationstest [C-optscale-R2]. *[entfernt: unbelegt — Zahl ohne Beleg]* Prüfungen mit Lernraten-Optimum am Gitterrand zählen als nicht entscheidbar [C-bh].

Das Red-Team stellt Gegenprüfungen auf. Eine Aussage gilt als „angefochten", sobald eine Gegenprüfung besteht, auch wenn diese mit der Aussage vereinbar ist. Angefochten sind R7, R15 und R18. Der Status bleibt unverändert, und die Einzelfälle sind zu lesen [C-redteam-methode].

## 4 Resultate

### 4.1 Skalierung im linearen Modell

**Numerischer Befund 1 (Gradientenfluss, observed).** Der Verlust des Gradientenflusses über t folgt den Prüfer-Fits mit fester Toleranz [C-optscale-R17]:

- (a, b) = (1.0, 2.0): Exponent 1.0000 [C-optscale-R17]
- (a, b) = (1.0, 3.0): Exponent 2.0000 [C-optscale-R17]
- (a, b) = (2.0, 4.0): Exponent 1.5000 [C-optscale-R17]
- (a, b) = (0.5, 1.5): Exponent 1.0000 [C-optscale-R17]
- (a, b) = (0.5, 3.0): Exponent 4.0000 in beiden Fenstern [C-optscale-R17-RT2]

Alle Werte sind mit e = (b−1)/a vereinbar.

**Proposition 1 (computed_rigorous).** Die Alternative e = (b−1)·a scheitert bei (a=2.0, b=3.0). Der Prüfer misst 1.0000 in beiden Fenstern gegen behauptete 4.0 [C-optscale-R17-RT1].

**Numerischer Befund 2 (Rechenoptimum bei C = P*t, observed).** Die Prüfer-Fits der Kurve „compute" mit fester Toleranz lauten (Fenster 1 / Fenster 2) [C-optscale-R6]:

- (1.0, 2.0): 0.4998 / 0.5000 [C-optscale-R6]
- (2.0, 3.0): 0.6658 / 0.6663 [C-optscale-R6]
- (1.0, 4.0): 1.4990 / 1.4998 [C-optscale-R6]
- (1.5, 1.5): 0.1999 / 0.2000 [C-optscale-R6]
- (0.5, 2.0): 0.6667 / 0.6667 [C-optscale-R8]
- (1.0, 3.0): 0.9995 / 0.9999 [C-optscale-R8]
- (2.0, 2.0): 0.3329 / 0.3331 [C-optscale-R9]

Sie entsprechen der Form C^-(b-1)/(a+1) [C-optscale-R7-RT1]. Die Aufteilung des Budgets auf P und t wurde nicht gemessen.

**Proposition 2 (computed_rigorous).** Die Gegenhypothese (b-1)/a für das Rechenoptimum scheitert. Bei (a=2.0, b=3.0) misst der Prüfer 0.6658 und 0.6663 [C-optscale-R6-RT1]. Bei (a=3.0, b=4.0) misst er 0.7474 und 0.7484 [C-optscale-R6-RT2]. Die behauptete 1.0 liegt jeweils außerhalb der festen Toleranz [C-optscale-R6-RT1, C-optscale-R6-RT2].

**Numerischer Befund 3 (Random Feature über P und Ridge über N, observed).** Bei (a=1.0, b=2.0) misst der Prüfer für das Random-Feature-Modell 0.9909 und 1.0540 gegen 1.0 mit Toleranz 0.1 [C-optscale-R1]. Bei (a=2.0, b=2.0) misst er 1.0782 und 1.0806 gegen 1.0 [C-optscale-R11]. Für Ridge über N misst er bei (a=1.0, b=3.0, ridge=0.001, noise=0.0) 1.9893 und 1.9258 gegen 2.0 [C-optscale-R12].

**Proposition 3 (computed_rigorous).** Bei kleinem a und großem b verfehlt der RF-Exponent die jeweils behauptete Sättigungsvorhersage der Gegenprüfung:

- (a, b) = (0.5, 3.5): Fit 0.6189 / 0.7694, behauptet 1.0 [C-optscale-R1-RT1]
- (a, b) = (0.3, 4.0): Fit 0.3146 / 0.4394, behauptet 0.6 [C-optscale-R1-RT2]
- (a, b) = (0.5, 3.0): Fit 0.6077 / 0.7600, behauptet 1.0 [C-optscale-R11-RT1]

Die Fits liegen deutlich unter dem Abschneide-Exponenten, der laut den Gegenprüfungen bei (0.5, 3.5) 2,5 und bei (0.3, 4.0) 3 beträgt [C-optscale-R1-RT1, C-optscale-R1-RT2]. Das Fenster mit größerem P liefert jeweils die größere Steigung. Die Sättigungsvorhersage trifft innerhalb der Toleranz nicht zu [C-optscale-R1-RT1, C-optscale-R1-RT2, C-optscale-R11-RT1].

### 4.2 Optimierer

**Beobachtung 1 (Muon gegen Adam, statistical).** Alle Vergleiche verwenden selbst getunte Lernraten und frische Seeds [C-optscale-R2].

- Unrotiert, a_L = a_R = 3.0: Adam gewinnt, relativer Endverlust 4.932e-23 gegen 2.825e-04, p = 0.0008 [C-optscale-R2].
- Rotiert, a_L = a_R = 3.0: Muon gewinnt, 4.481e-04 gegen 1.810e-03, Verhältnis 0.248 [C-optscale-R4].
- Rotiert, a_L = a_R = 1.0: Adam gewinnt, 3.170e-11 gegen 8.863e-05, p = 0.0041 [C-optscale-R5].
- Rotiert, a_L = a_R = 2.5: Muon gewinnt, 1.814e-04 gegen 1.683e-03, Verhältnis 0.108 [C-optscale-R14].
- Bei fast flachem Spektrum (a=0.1) gewinnt Adam unrotiert (3.883e-23 gegen 1.162e-05) [C-optscale-R3-RT2] und rotiert (3.873e-23 gegen 1.131e-05) [C-optscale-R5-RT2].

Die Rotation allein entscheidet also nicht. Der Vorzeichenwechsel auf der rotierten Diagonalen liegt zwischen den geprüften Punkten a=1.0 und a=2.5 [C-optscale-R5, C-optscale-R14]. Wo genau, ist nicht eingegrenzt.

**Beobachtung 2 (heavy-tailed Rauschen, statistical).** Auf der rotierten Quadratik mit a=2.0 und Student-Rauschen (df = 2) schlagen Shampoo und Muon SGD mit Verhältnissen 0.521 und 0.567 [C-optscale-R13]. Adam schlägt SGD ebenfalls. Der Prüfer misst für SGD gegen Adam das Verhältnis 1.146 [C-bh, C-optscale-R13-RT1]. Auch Signum schlägt SGD, das Verhältnis für SGD gegen Signum beträgt 1.143 [C-bh, C-optscale-R13-RT2]. Clipping wurde nicht geprüft.

**Beobachtung 3 (Schedules, statistical).**

- Adam mit cosine schlägt Adam mit const auf der verrauschten rotierten Quadratik: 1.142e-02 gegen 3.190e-02, Verhältnis 0.358 [C-optscale-R15].
- SGD mit wsd schlägt SGD mit const bei Student-Rauschen, Verhältnis 0.555 [C-bh, C-optscale-R15-RT2].
- Im MLP war SGD mit cosine nicht besser als mit const: 4.859e-03 gegen 3.732e-03, Verhältnis 1.302, p = 0.9419 [C-optscale-R15-RT1, C-bh].

**Korrektur für multiples Testen.** Von m = 20 Vergleichen bleiben 11 nach Benjamini-Hochberg signifikant mit Verhältnis unter 0.9 [C-bh].

### 4.3 Edge of Stability und μP

**Numerischer Befund 4 (Edge of Stability, observed).** Bei Breite 16, lr = 1.0 und 2000 Schritten liegt lr*lambda_max/2 am Ende in [0.85, 1.25] [C-optscale-R16]. Das gilt für 5 von 5 frischen Seeds, gemessen mit dem vollen Hesse-Eigenwert [C-optscale-R16].

*[entfernt: unbelegt — Zahl(en) [5.0] stehen in keiner zitierten Claim]*

- μP, Adam: -7, -6, -7, -7, Verschiebung +0 Oktaven [C-optscale-R10]
- SP, Adam: -6, -6, -7, -8, Verschiebung -2 Oktaven [C-optscale-R10]
- μP, SGD: -1, -1, 0, -1, Verschiebung +0 Oktaven [C-optscale-R10]
- SP, SGD: 0, -1, -1, -2, Verschiebung -2 Oktaven [C-optscale-R10]

Das Transferkriterium (|Verschiebung| <= 1 und Spannweite <= 1) ist unter μP erfüllt, unter SP nicht. Grundlage sind 300 Schritte, zwei Seeds und ein Gitter mit Faktor 2 [C-optscale-R10]. Das steht im Einklang mit der Literatur zum Hyperparameter-Transfer [C-lit29].

### 4.4 Exakte Stabilität

**Proposition 4 (computed_rigorous).** Für f(x) = x^T H x / 2 mit H = [[1, 0], [0, 2]] gilt nach rationaler Arithmetik und Sylvester-Kriterium:

- GD ist stabil bei lr = 99/100 [C-optscale-R18].
- GD ist instabil bei lr = 101/100 [C-optscale-R18].
- GD ist instabil bei lr = 1, also exakt an der Grenze lr*lambda_max/2 = 1 [C-optscale-R18-RT1].
- Heavy-Ball mit beta = 9/10 ist stabil bei lr = 3/2 [C-optscale-R18].
- Heavy-Ball mit beta = 9/10 ist instabil bei lr = 19/10 [C-optscale-R18-RT2].

Die Bedingung lautet |beta| < 1, H > 0 und H < 2(1+beta)/lr [C-optscale-R18]. Der Status „angefochten" resultiert aus der Protokollregel, da die bestandenen Gegenprüfungen mit der Aussage vereinbar sind [C-redteam-methode].

## 5 Negative Ergebnisse und Red-Team-Befunde

Die folgenden Gegenprüfungen sind nicht bestanden, ihre Gegenhypothesen also zurückgewiesen:

- **Rechenoptimum:** Die Gegenhypothese (b-1)/a scheitert (Proposition 2). Die Gegenprüfungen zum rf-basierten Rechenoptimum wurden auf der Gradientenfluss-Kurve „compute" bestanden [C-optscale-R7-RT1, C-optscale-R7-RT2]. Der rf-basierte Fall selbst bleibt damit ungemessen.
- **Budget C = P*N, rf-Fits:** Die Vorhersage (b-1)/2 wurde nicht bestätigt. Bei (a=2.0, b=2.0) misst der Prüfer 1.0782 und 1.0806 gegen behauptete 0.5 [C-optscale-R8-RT1]. Bei (a=2.0, b=3.0) misst er 1.8814 und 1.8742 gegen behauptete 1.0 [C-optscale-R8-RT2].
- **Budget C = P*N, Ridge und Zerlegung:** Die Ridge-Kurve bei (a=1.0, b=4.0) misst 2.5008 und 2.7484 gegen behauptete 2.0 [C-optscale-R9-RT2]. Die Vorhersage C^-1,2 scheiterte ebenfalls, der Prüfer maß 1.4990 und 1.4998 gegen behauptete 1.2 [C-optscale-R9-RT1].
- **Ridge-Sättigung:** Bei (a=0.5, b=3.0) misst der Prüfer 1.4644 und 1.8149 gegen behauptete 1.0 [C-optscale-R12-RT1]. Bei (a=0.4, b=4.0) misst er 1.2112 und 1.5759 gegen behauptete 0.8 [C-optscale-R12-RT2]. Mit Rauschen bei (a=2.0, b=2.0) misst er die Exponenten -0.1666 und -0.2154 gegen behauptete 0.5 [C-optscale-R11-RT2].
- **Rotation, a=1.0:** Die Gegenaussage, Muon schlage Adam rotiert bereits bei a=1.0, hat sich nicht bestätigt [C-optscale-R5-RT1].
- **Rotation, a=2.5 und a=3.0:** Die Gegenaussage, Adam gewinne rotiert noch bei a=2.5, hat sich nicht bestätigt [C-optscale-R14-RT1]. Dasselbe gilt für die Gegenaussage bei a=3.0 [C-optscale-R14-RT2].
- **Rotation, Adam gegen Muon:** Auch die Aussage, Adam schlage Muon im rotierten Fall, hat sich nicht bestätigt [C-optscale-R2-RT2, C-optscale-R3-RT1].
- **Shampoo:** Die Gegenprüfungen zu Shampoo gegen Adam sind nicht entscheidbar, da das Lernraten-Optimum am Rand des Prüfer-Gitters 2^-16..2^4 lag [C-optscale-R2-RT1, C-optscale-R4-RT1].
- **Edge of Stability:** Bei kleinerer Lernrate und 4000 Schritten liegen die Werte 0.595/0.607, 0.752/0.763, 0.695/0.699, 0.639/0.645 und 0.886/0.896 höchstens in einem Seed im Intervall [0.85, 1.25] [C-optscale-R16-RT2, C-optscale-R16]. Das Kriterium (mindestens 4 von 5) ist nicht erfüllt [C-optscale-R16-RT2, C-optscale-R16].
- **SGD in μP und SP:** Die Gegenhypothesen „SP-SGD transferiert" und „μP-SGD transferiert nicht" scheitern (μP-gegen-SP-Befund) [C-optscale-R10-RT1, C-optscale-R10-RT2].
- **Heavy-tailed Rauschen:** SGD schlägt weder Adam noch Signum [C-optscale-R13-RT1, C-optscale-R13-RT2].

Das Labor selbst zählt 0 negative Ergebnisse [C-methode]. Das bezieht sich auf die Buchführung der Hauptaussagen. Die oben genannten Gegenprüfungen sind davon unabhängig.

## 6 Grenzen und offene Fragen

- **Asymptotik bei kleinem a:** Die Fits steigen mit dem Fenster (Proposition 3). Der asymptotische RF-Exponent und das Ridge-Verhalten sind nicht bestätigt, ebenso die Sättigung [C-optscale-R1-RT1, C-optscale-R12-RT1].
- **Rechenoptimum bei C = P*N:** Die direkte Minimierung über ein (P,N)-Gitter ist nicht belegt, und die optimale Aufteilung auf P und t wurde nicht gemessen [C-optscale-R9, C-optscale-R8-RT2].
- **Rotation:** Eine graduelle Rotation und die Frage, ob es einen Phasenübergang gibt, wurden nicht untersucht. Die Lage des Vorzeichenwechsels zwischen a=1.0 und a=2.5 ist nicht eingegrenzt [C-optscale-R5, C-optscale-R14].
- **Lernraten-Gitter:** Mehrere Prüfungen mit Optimum am Gitterrand sind nicht entscheidbar, so Shampoo gegen Adam [C-optscale-R4-RT1].
- **Breite des Tests:** μP und SP wurden nur bis Breite 256 mit 300 Schritten und zwei Seeds geprüft [C-optscale-R10]. Der Schedule-Vergleich im MLP stützt sich auf einen Einzelvergleich [C-optscale-R15-RT1]. Offen sind außerdem Clipping, Edge of Stability bei anderen Lernraten und Trainingsdauern sowie die Wechselwirkung von Momentum- und Batchgrößen-Skalierung [C-lit11, C-optscale-R16-RT2].

## Literatur (nur aus Claims)

- Zum spektralen Schrittweitenprofil, das Muon gegenüber Adam und Adam gegenüber SGD erklärt: arXiv:2608.25990v1 [C-lit3].
- Zum Muon-Skalierungsgesetz im linearen Assoziativspeicher: arXiv:2602.05725v3 [C-lit8, C-lit9].
- Zu Shampoo und SOAP: arXiv:2409.11321v2 [C-lit12, C-lit13].
- Zur Stabilitätsschwelle von Adam am Edge of Stability: arXiv:2207.14484v2 [C-lit16, C-lit17].
- Zu stabilem Training am Edge of Stability: arXiv:2606.15551v1 [C-lit14] und arXiv:2205.09745v3 [C-lit15].
- Zu μP und Hyperparameter-Transfer: arXiv:2203.03466v2 [C-lit29, C-lit30] und arXiv:2308.01814v2 [C-lit5, C-lit6].
- Zu heavy-tailed Rauschen: arXiv:2602.07425v2 [C-lit18] und arXiv:2412.19529v4 [C-lit19, C-lit20].

---
Prüfprotokoll: 70 Claims zitiert, Korrekturrunden [{"runde": 0, "verstoesse": 45}, {"runde": 1, "verstoesse": 10}, {"final_verstoesse_entfernt": 2}], 2 unbelegte Sätze entfernt, verbleibende Verstöße: 0.
