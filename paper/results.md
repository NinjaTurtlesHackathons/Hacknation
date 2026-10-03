# Ergebnisse (automatisch aus `claims` erzeugt)

Gates: 13/15 grün. Jede Aussage nennt ihre claim_id, ihr Evidenzlevel und ihren Status.

## Theorie

- Für Zufallssuche ohne Zurücklegen gilt E[N] = (n+1)/(k+1); Beweis in Lean 4 (lean/ENRandom.lean). [C-lemma, proved_lean, bestätigt]
- Zufallssuche (echt) stimmt mit der Theorie überein: gemessen 96.2, Theorie 98.4, z = -0.10 (Schranke |z| < 3, 20 Seeds). [C-theorie-echt, statistical, bestätigt]
- Die Pipeline reproduziert die Selbsttest-Rohdaten exakt (echt/random: gleich; echt/gp_ei: gleich; negativkontrolle/random: gleich; negativkontrolle/gp_ei: maschinenabhängig, Ø 118.8 statt 125.8 (nur berichtet)). [C-repro, computed_rigorous, bestätigt]

## Bayes'sche Optimierung als Baseline

- random: im Mittel 96.2 Experimente bis zum ersten Top-1-%-Treffer (Median 62, 20 Seeds). [C-mean-random, observed, bestätigt]
- gp_ei: im Mittel 34.2 Experimente bis zum ersten Top-1-%-Treffer (Median 18, 20 Seeds). [C-mean-gp_ei, observed, bestätigt]
- GP + EI schlägt Zufallssuche: gp_ei vs random (echt): Ø N 34.2 vs 96.2, Speedup 2.81 (95 %-KI 1.47–5.34), p = 0.0054, Seeds 20. [C-gp, statistical, bestätigt]

## KI-Vorwissen (Hybrid), präregistrierte Hypothese H1

- hybrid: im Mittel 27.8 Experimente bis zum ersten Top-1-%-Treffer (Median 26, 20 Seeds). [C-mean-hybrid, observed, bestätigt]
- Hybrid schlägt Zufallssuche: hybrid vs random (echt): Ø N 27.8 vs 96.2, Speedup 3.47 (95 %-KI 2.05–5.54), p = 0.0007, Seeds 20. [C-hybrid-zufall, statistical, bestätigt]
- H1: Hybrid schlägt GP + EI: Nicht belegt, das präregistrierte Erfolgskriterium (p < 0,05 und KI-Untergrenze > 1) ist verfehlt. hybrid vs gp_ei (echt): Ø N 27.8 vs 34.2, Speedup 1.23 (95 %-KI 0.84–1.67), p = 0.1449, Seeds 20. [C-H1, statistical, offen]

## Kontaminationstest (H2)

- hybrid_neutral: im Mittel 31.2 Experimente bis zum ersten Top-1-%-Treffer (Median 26, 20 Seeds). [C-mean-hybrid_neutral, observed, bestätigt]
- H2 (Kontamination): hybrid_neutral vs gp_ei: Speedup 1.10 (KI 0.82–1.40), p = 0.2651; Ø N hybrid 27.8 vs hybrid_neutral 31.2 (Verhältnis 1.13, KI 0.92–1.36). Gegenüber gp_ei ist kein Gewinn belegt; wird offen berichtet. [C-H2, statistical, offen]

## Negativkontrollen

- Zufallssuche (negativkontrolle_je_seed) stimmt mit der Theorie überein: gemessen 75.1, Theorie 98.4, z = -1.09 (Schranke |z| < 3, 20 Seeds). [C-theorie-negativkontrolle_je_seed, statistical, bestätigt]
- Negativkontrolle (vertauschte Ausbeuten, eigene Vertauschung je Seed): gp_ei: Speedup 1.05 (KI 0.68–1.78), p = 0.432: kein Effekt, wie erwartet | hybrid: Speedup 0.89 (KI 0.57–1.56), p = 0.659: kein Effekt, wie erwartet | hybrid_neutral: Speedup 1.16 (KI 0.68–1.84), p = 0.291: kein Effekt, wie erwartet [C-neg, statistical, bestätigt]
- Negativkontrolle wie präregistriert (eine Vertauschung, Seed 7), GP + EI: Speedup 0.99 (KI 0.56–1.69), p = 0.513: kein Effekt, wie erwartet. [C-neg-seed7, statistical, bestätigt]
- hybrid auf der präregistrierten Einzel-Vertauschung (Seed 7): Speedup 5.89 (KI 3.43–9.24), p = 0.0001. Kein Leck: das feste KI-Vorwissen ordnet die Kandidaten für alle Seeds gleich, ein zufällig hoch eingestufter Treffer wird daher in jedem Seed gefunden (Werte von N: [1, 16, 17, 18, 19, 21, 22, 24, 36, 58]). Die 20 Seeds sind hier keine unabhängigen Wiederholungen; maßgeblich ist C-neg. [C-neg-seed7-hybrid, observed, bestätigt]
- hybrid_neutral auf der präregistrierten Einzel-Vertauschung (Seed 7): Speedup 3.11 (KI 1.31–11.60), p = 0.0102. Kein Leck: das feste KI-Vorwissen ordnet die Kandidaten für alle Seeds gleich, ein zufällig hoch eingestufter Treffer wird daher in jedem Seed gefunden (Werte von N: [1, 9, 10, 13, 14, 16, 24, 30, 189, 349]). Die 20 Seeds sind hier keine unabhängigen Wiederholungen; maßgeblich ist C-neg. [C-neg-seed7-hybrid_neutral, observed, bestätigt]

## Hypothesen der KI (Status nach Benjamini-Hochberg, q = 0,1)

- KI-Hypothese (named): Arylchloride senken die Ausbeute, weil die oxidative Addition der starken C-Cl-Bindung bei nur 60 °C mit einer milden organischen Base geschwindigkeitsbestimmend und langsam ist. [r = 0.46, p = 0.0000, p_BH = 0.0000] [C-hyp-named-H1, statistical, bestätigt]
- KI-Hypothese (named): Arylbromide und -iodide erhöhen die Ausbeute gegenüber dem Mittel, weil ihre schwächeren C-X-Bindungen eine schnelle oxidative Addition ermöglichen. [r = 0.26, p = 0.0001, p_BH = 0.0011] [C-hyp-named-H2, statistical, bestätigt]
- KI-Hypothese (named): Elektronenreiche Arylhalogenide (4-Methoxy) liefern geringere Ausbeuten als elektronenarme (4-CF3), da Elektronendonoren die oxidative Addition verlangsamen. [r = 0.03, p = 0.3224, p_BH = 0.4912] [C-hyp-named-H3, hypothesis, offen]
- KI-Hypothese (named): 2-Halogenpyridine senken die Ausbeute, weil der benachbarte Pyridin-Stickstoff nach oxidativer Addition stabile, chelatisierte bzw. verbrückte Pd-Spezies bildet, die den Katalysezyklus hemmen. [r = -0.23, p = 0.9989, p_BH = 0.9991] [C-hyp-named-H4, hypothesis, widerlegt]
- KI-Hypothese (named): Die sperrigen Liganden AdBrettPhos und t-BuXPhos erhöhen die Ausbeute, da sie monoligierte, reaktive L1Pd(0)-Spezies stabilisieren und die reduktive Eliminierung beschleunigen. [r = 0.16, p = 0.0122, p_BH = 0.0260] [C-hyp-named-H5, statistical, bestätigt]
- KI-Hypothese (named): XPhos senkt die Ausbeute, weil der weniger sperrige, weniger elektronenreiche Dicyclohexylphosphin-Ligand mit primären Anilinen und schwachen Basen bei 60 °C eine weniger aktive Katalyse ergibt. [r = 0.23, p = 0.0003, p_BH = 0.0016] [C-hyp-named-H6, statistical, bestätigt]
- KI-Hypothese (named): Die stärkeren Basen P2Et und BTMG erhöhen die Ausbeute gegenüber MTBD, da sie die Deprotonierung des Pd-gebundenen Amins effizienter bewirken. [r = -0.16, p = 0.9884, p_BH = 0.9991] [C-hyp-named-H7, hypothesis, widerlegt]
- KI-Hypothese (named): Isoxazole mit elektronenziehenden Estergruppen senken die Ausbeute, weil ihre geschwächte N-O-Bindung oxidativ an Pd(0) addieren kann und so Katalysator verbraucht wird. [r = 0.02, p = 0.3750, p_BH = 0.5455] [C-hyp-named-H8, hypothesis, offen]
- KI-Hypothese (named): Isoxazole mit unsubstituierter C3-H-Position (5-substituiert) senken die Ausbeute, da sie unter Basenbedingungen zu Cyanoenolaten ringöffnen können, die an Pd koordinieren und es vergiften. [r = 0.00, p = 0.4950, p_BH = 0.6566] [C-hyp-named-H9, hypothesis, offen]
- KI-Hypothese (named): Sterisch abgeschirmte, elektronenreiche 3,5-disubstituierte Isoxazole stören kaum und liefern überdurchschnittliche Ausbeuten, weil ihre N-O-Bindung schwer zugänglich und wenig aktiviert ist. [r = 0.21, p = 0.0019, p_BH = 0.0068] [C-hyp-named-H10, statistical, bestätigt]
- KI-Hypothese (named): Benzo[c]isoxazol (Anthranil) senkt die Ausbeute, da seine sehr labile N-O-Bindung leicht an Pd(0) addiert bzw. als Aminierungs-Elektrophil mit Konkurrenzreaktionen wirkt. [r = 0.22, p = 0.0001, p_BH = 0.0012] [C-hyp-named-H11, statistical, bestätigt]
- KI-Hypothese (named): 5-Phenyl-1,2,4-oxadiazol ist ein weniger koordinierendes und gegen Pd(0) robusteres Additiv und senkt die Ausbeute kaum, sodass es leicht überdurchschnittlich abschneidet. [r = -0.10, p = 0.9285, p_BH = 0.9991] [C-hyp-named-H12, hypothesis, offen]
- KI-Hypothese (neutral): Substrate mit der niedrigsten Masse in ihrer Serie (ca. 113, 140, 142, 180 g/mol) sind vermutlich Arylchloride, deren C-Cl-Bindung die oxidative Addition am Metall stark verlangsamt, daher sinkt die Ausbeute. [r = 0.43, p = 0.0000, p_BH = 0.0000] [C-hyp-neutral-H1, statistical, bestätigt]
- KI-Hypothese (neutral): Substrate mit stark negativen C1-NMR-Verschiebungen (Schweratomeffekt) bzw. der hoechsten Masse sind vermutlich Aryliodide, die am leichtesten oxidativ addieren und daher hoehere Ausbeuten liefern. [r = 0.24, p = 0.0003, p_BH = 0.0016] [C-hyp-neutral-H2, statistical, bestätigt]
- KI-Hypothese (neutral): Substrate mittlerer Masse (vermutlich Arylbromide) liegen zwischen Chloriden und Iodiden und liefern leicht ueberdurchschnittliche Ausbeuten. [r = 0.14, p = 0.0263, p_BH = 0.0527] [C-hyp-neutral-H3, statistical, bestätigt]
- KI-Hypothese (neutral): Elektronenarme Arylhalogenide (niedrigstes HOMO/LUMO, z. B. die schwerere aromatische Serie mit ca. 180/225/272 g/mol) addieren schneller oxidativ als elektronenreiche (hoeheres HOMO wie H4, H6, H7, H11, H14), was die Ausbeute erhoeht. [r = 0.10, p = 0.0842, p_BH = 0.1585] [C-hyp-neutral-H4, hypothesis, offen]
- KI-Hypothese (neutral): Heteroaryl-Halogenide mit kleinem Volumen und hohem Dipol (H8, H15, H13) koennen ueber ein Ring-Stickstoffatom an das Metall koordinieren und den Katalysator teilweise vergiften, was die Ausbeute senkt. [r = -0.23, p = 0.9991, p_BH = 0.9991] [C-hyp-neutral-H5, hypothesis, widerlegt]
- KI-Hypothese (neutral): Die groesste und polarste Base B3 (vermutlich eine sehr starke Phosphazen-artige Base) deprotoniert den Nukleophil-Metall-Komplex am effizientesten und steigert die Ausbeute, waehrend die schwaechste, am wenigsten negativ geladene Base B2 die Ausbeute senkt. [r = -0.17, p = 0.9909, p_BH = 0.9991] [C-hyp-neutral-H6, hypothesis, widerlegt]
- KI-Hypothese (neutral): Liganden mit stark negativ geladenem Phosphor (L1, L3) sind elektronenreicher, beschleunigen die oxidative Addition und erhoehen die Ausbeute, besonders bei Chloriden; L4 mit dem am wenigsten negativen Phosphor senkt sie. [r = 0.16, p = 0.0118, p_BH = 0.0260] [C-hyp-neutral-H7, statistical, bestätigt]
- KI-Hypothese (neutral): Der Ligand L4 mit der hoechsten C1-NMR-Verschiebung und geringem Dipol ist vermutlich sterisch/elektronisch am wenigsten passend fuer die reduktive Eliminierung und liefert die niedrigsten Ausbeuten. [r = 0.23, p = 0.0003, p_BH = 0.0016] [C-hyp-neutral-H8, statistical, bestätigt]
- KI-Hypothese (neutral): Additive mit sehr niedrigem LUMO (stark elektrophile Heterocyclen, z. B. A8, A22, A14, A4) koennen selbst oxidativ addieren oder mit Base/Nukleophil reagieren und senken dadurch die Ausbeute. [r = 0.16, p = 0.0119, p_BH = 0.0260] [C-hyp-neutral-H9, statistical, bestätigt]
- KI-Hypothese (neutral): Additive mit hohem LUMO und relativ hohem HOMO (elektronenreich, wenig reaktiv, z. B. A9, A16, A21, A18, A5) stoeren den Katalysezyklus kaum und lassen die Ausbeute leicht ueberdurchschnittlich. [r = 0.17, p = 0.0082, p_BH = 0.0219] [C-hyp-neutral-H10, statistical, bestätigt]
- KI-Hypothese (neutral): Additive mit stark negativ geladenem Stickstoff (A11, A21, A4) koordinieren als Lewis-Basen am Metall und hemmen den Katalysator etwas, was die Ausbeute moderat senkt. [r = 0.18, p = 0.0045, p_BH = 0.0144] [C-hyp-neutral-H11, statistical, bestätigt]
- KI-Hypothese (neutral): Bei Arylchloriden verstaerkt sich der Basen-Effekt: die schwache Base B2 fuehrt hier zu besonders niedrigen Ausbeuten, waehrend B3 den Nachteil teilweise kompensiert. [r = -0.01, p = 0.5400, p_BH = 0.6646] [C-hyp-neutral-H12, hypothesis, offen]
