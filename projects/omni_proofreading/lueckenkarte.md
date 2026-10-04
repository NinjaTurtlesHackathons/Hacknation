# Lückenkarte: Kinetic Proofreading (Phase 2)

Grundlage: `research/kb/proofreading/kb.json` (Lauf 1: 266 Quellen, 87 Befunde mit per Code bestätigtem Zitat) plus Sichtung der
großen Recherche (2602 Quellen, 2352 bewertet; Extraktion läuft separat). Quellen-IDs wie in `wissensstand.md`.

| # | Lücke | Warum offen (Beleg) | Neuheitstyp | Prüfbarkeit | VoI (Neuheit × Machbarkeit) |
|---|---|---|---|---|---|
| L1 | Gilt die Hopfield-Grenze η ≥ e^{-(n+1)Δ} der linearen Kette für **alle** Raten und jeden endlichen Treibstoff, nicht nur im Limes unendlicher Energie und verschwindender Geschwindigkeit? | Hopfield 1974 begründet die Grenze im Limes; arXiv:1710.06038: Schranken „außerhalb des asymptotischen Regimes nicht analytisch bewiesen“ | (c) Schranke | `untere_schranke` (symbolisch, Matrix-Tree, Koeffizienten-Positivität) | 0,4 × 0,9 = 0,36: wahrscheinlich bekannt, aber hier für n ≤ 2 rigoros und parameterfrei |
| L2 | Ist e^{-2Δ} eine **universelle** Grenze für alle Netzwerke mit zwei gebundenen Zuständen (≤ 5 Zustände) unter den Modellregeln? | doi:10.1002/qub2.75: „Netzwerktopologie, Kinetik und Energetik bestimmen gemeinsam die Grenzen“, aber keine vollständige Klassifikation; Murugan–Huse–Leibler betrachten Ketten-Regime | (b) Gegenbeispiel / (c) Schranke | `schranke_familie` (Prüfer erzeugt die Familie selbst) + `erreichbar` (exaktes Gegenbeispiel) | 0,8 × 0,8 = 0,64 |
| L3 | **Welcher Mechanismus** erlaubt das Unterschreiten von e^{-2Δ} mit nur zwei gebundenen Zuständen? | Vorbefund des Explorers (numerisch, Kandidat): Topologien mit treibstoffgetriebenem Ausgang am Produktzustand erreichen η ≪ e^{-2Δ}; in der Literatur ist Editing (Exonuklease) bekannt, aber nicht als Topologie-Kriterium in dieser Modellklasse | (b) Gegenbeispiel | `erreichbar` + `schranke_familie` für die Teilfamilien | 0,7 × 0,6 = 0,42 |
| L4 | Front η*(σ) bei **geforderter Geschwindigkeit** v ≥ v_min für die Kette n = 1 | arXiv:2312.01051 und doi:10.1098/rsif.2024.0232: Pareto-Fronten numerisch bzw. im gemischten Regime; Kombination mit v_min und exakten Punkten offen | (a) Erweiterung | `erreichbar` (obere Kurve exakt) + `optimum` (numerisch) | 0,4 × 0,8 = 0,32 |
| L5 | Gleichgewichtsnahes Regime: Wird η ≈ e^{-2Δ} schon mit σ < 0,2 kT pro Produkt erreicht (bei v → 0)? | Vorbefund des Explorers: η = 1,15·e^{-2Δ} bei σ = 0,14 kT; Bennett-Argument (langsames Kopieren) erwartet kleine Kosten, aber kein exakter Punkt bekannt | (a) Erweiterung | `erreichbar` mit `sigma_max` | 0,3 × 0,9 = 0,27 |
| L6 | Vermutung aus arXiv:1710.06038: σ·ln(μ/μ_eq)/P < 1 außerhalb des asymptotischen Regimes | „numerisch erfüllt …, außerhalb des asymptotischen Regimes nicht analytisch bewiesen“ (arXiv:1710.06038) | (c) Schranke | **Prüfer fehlt** (Definitionen von σ, μ, P weichen von unserem Modell ab) | 0,9 × 0,1 = 0,09 |

**Abnahme Phase 2:** Lücken mit Neuheitstyp ≠ Reproduktion und vorhandenem Prüfer: L2, L3, L4, L5 (4 ≥ 3). L6 bleibt offen (Prüfer fehlt).
Reihenfolge nach VoI: L2, L3, L1, L4, L5.
