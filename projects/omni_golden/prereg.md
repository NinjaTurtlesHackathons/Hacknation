# Präregistrierung Omnigent-Lauf (2026-10-04 04:14)

- Startfrage F30: Welche der 24 noch offenen Topologien der Familie mit höchstens zwei gebundenen Zuständen (fam2_*) erreichen eta < e^{-2 Delta} = 1e-4 (exaktes Zertifikat erreichbar_liste), und für welche lässt sich die Schranke eta >= 1/D**2 beweisen?
- Erwartung (Annahme A1): Klassifikation 50 / 14 / 24: genau ['fam2_11', 'fam2_35', 'fam2_39', 'fam2_41', 'fam2_43', 'fam2_45', 'fam2_58', 'fam2_66', 'fam2_67', 'fam2_75', 'fam2_82', 'fam2_83', 'fam2_9', 'fam2_91'] verletzen eta >= e^(-2 Delta) unter den 88 Topologien
- Budget: 40 Verifier-Aufrufe

## Hypothese H1 (2026-10-04 04:14:50, agent-generiert von planner, vor dem Experiment)
- Aussage: F30 will be confirmed: the checked claim passes verification
- Erfolgskriterium (maschinell geprüft): {"frage": "F30", "erwartet": "bestanden"}
- sha256: 7c658804dc1efa5497159ff9c8e7aa9862526744bfa22022adb2b7c70c08d25a

## 2026-10-04 04:14:55, vor dem Experiment (Omnigent, planner)
- Frage [F30]: Welche der 24 noch offenen Topologien der Familie mit höchstens zwei gebundenen Zuständen (fam2_*) erreichen eta < e^{-2 Delta} = 1e-4 (exaktes Zertifikat erreichbar_liste), und für welche lässt sich die Schranke eta >= 1/D**2 beweisen?
- Option O2 (tiefe_rechnung): Tiefe, möglichst zertifizierte Rechnung an wenigen, gezielt gewählten Punkten; genau eine Behauptung prüfen.
- Erwartete Verifier-Aufrufe: 1
- Verworfen: O1 breiter_scan
- Begründung: Deep certified computation on one claim has the higher expected gain (0.65 vs 0.35) at cost 1 versus 3; budget is ample (40) but the broad scan adds little for F30.

## Hypothese H2 (2026-10-04 04:19:25, agent-generiert von planner, vor dem Experiment)
- Aussage: F32 experiment will confirm the prediction (no surprise)
- Erfolgskriterium (maschinell geprüft): {"frage": "F32", "erwartet": "keine_ueberraschung"}
- sha256: 8c08aae6848e27d3d4bc32da564cf0905f906356667ad30346fab41af0015faf

## 2026-10-04 04:19:34, vor dem Experiment (Omnigent, planner)
- Frage [F32]: Lassen sich die thermodynamischen Grenzen für den Fehler-Kosten-Geschwindigkeit-Zielkonflikt auf andere zelluläre Fehlerkorrektur-Mechanismen jenseits von Kinetic Proofreading generalisieren (z. B. DNA-Mismatch-Repair, Immunsystem-Rezeptor-Sortierung)?
- Option O2 (tiefe_rechnung): Tiefe, möglichst zertifizierte Rechnung an wenigen, gezielt gewählten Punkten; genau eine Behauptung prüfen.
- Erwartete Verifier-Aufrufe: 1
- Verworfen: O1 breiter_scan
- Begründung: Deep certified check of one claim for F32 is cheap (1 call) with highest expected gain 0.65; budget 38 left.

## 2026-10-04 04:19:35, vor dem Experiment (Omnigent, planner)
- Frage [F32]: Lassen sich die thermodynamischen Grenzen für den Fehler-Kosten-Geschwindigkeit-Zielkonflikt auf andere zelluläre Fehlerkorrektur-Mechanismen jenseits von Kinetic Proofreading generalisieren (z. B. DNA-Mismatch-Repair, Immunsystem-Rezeptor-Sortierung)?
- Option O1 (breiter_scan): Breiter Scan über viele Parameterwerte mit geringer Präzision, danach bis zu 3 Kandidaten-Behauptungen prüfen.
- Erwartete Verifier-Aufrufe: 3
- Verworfen: O2 tiefe_rechnung
- Begründung: Complementary broad scan (3 calls) over F32 parameter range to surface candidates; budget 38 covers both.
