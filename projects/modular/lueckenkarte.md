# Lückenkarte: Modulformen und Stringtheorie-Identitäten (Phase 2)

Grundlage: `research/kb/modular/known_results.md` (Recherche vom 2026-10-04, 3298 Quellen, 133 per Code geprüfte Zitate).

| ID | Lücke | Warum offen (Beleg) | Neuheitstyp | Prüfbarkeit | VoI (Neuheit × Machbarkeit) |
|---|---|---|---|---|---|
| L1 | Explizite algebraische Identität zwischen den sieben dihedralen Funktionen C_{a,b,c} vom Gewicht 9, E_9 und zeta(9) | arXiv:1608.04393: „all identities at weight six and all dihedral identities at weight seven are obtained and proven“ – Gewicht 9 wird dort nicht behandelt; arXiv:2004.05156 nennt „higher, hitherto unexplored weights“ | (d) geschlossene Form / (a) Erweiterung auf Gewicht 9 | mgf_relation (exakter Laurent-Leitkoeffizient + numerisch an Prüfer-Punkten) | 0,7 × 0,8 = 0,56 |
| L2 | Dasselbe bei Gewicht 11 (zehn Funktionen C_{a,b,c}) | wie L1; kein Befund der Recherche nennt Gewicht-11-Identitäten explizit | (d) / (a) | mgf_relation, mgf_relationsraum (45-60 Stellen nötig) | 0,7 × 0,5 = 0,35 |
| L3 | Vollständigkeit: Dimension des Raums aller rationalen linearen Relationen zwischen {C_{a,b,c}} und {E_w, zeta(w)} bei Gewicht 3, 5, 7, 9 (gibt es genau eine pro ungeradem Gewicht?) | arXiv:1608.04393 zählt Eigenwerte s(s-1) nur „bounded by the weight“; eine Zählung der algebraischen Relationen für w ≥ 9 fehlt in der Recherche | (c) Schranke / (a) | mgf_relationsraum (Singulärwertabstand, numerisch) | 0,6 × 0,7 = 0,42 |
| L4 | Keine algebraischen Relationen bei geradem Gewicht 6 und 8 in der Basis aus C_{a,b,c}, Eisenstein-Polynomen und zeta·E (Negativbefund) | arXiv:1608.04393 leitet Gewicht-6-Identitäten über Laplace-Gleichungen her; ob rein algebraische Relationen ohne Laplace-Operator existieren, ist dort nicht als Zählung angegeben | (b) Gegenbeispiel / negatives Ergebnis | mgf_relationsraum mit dim 0 | 0,4 × 0,7 = 0,28 |
| L5 | Laplace-Gleichungen der Form (Delta - s(s-1)) C = Quellen für C_{3,1,1} und C_{2,2,2}, C_{3,2,1} als Validierung des Auswerters (Anker) | bekannt (arXiv:1608.04393, DGGV); dient der Kalibrierung | Reproduktion (Anker) | mgf_relation mit L[...] | 0,1 × 0,8 = 0,08 |
| L6 | Spann der holomorphen Eta-Quotienten in M_4(Gamma_0(N)) für alle N ≤ 30, exakt | doi:10.1016/j.aim.2014.12.002 (Rouse–Webb) behandelt Spannfragen allgemein; eine vollständige Tabelle für Gewicht 4 ist in der Recherche nicht belegt | (a) Erweiterung | eta_span_tabelle (exakt, Sturm-Schranke) | 0,3 × 0,9 = 0,27 |
| L7 | Stringtheorie-Identitäten holomorph: Jacobi (Verschwinden der GSO-projizierten Zustandssumme), theta_{E8}^2 = theta_{D16+}, Delta = eta^24, j-Koeffizient 196884 | klassisch bekannt | Reproduktion (Anker) | identitaet / koeffizient (Sturm-Zertifikat, exakt) | 0,05 × 1,0 = 0,05 |
| L8 | Bestimmt das Verschwinden des vollen Laurent-Polynoms die Identität? | arXiv:1608.04393: „Whenever the Laurent polynomial at the cusp is available, the form of these identities confirms the pattern“ | (c) | Prüfer fehlt (nur der Leitkoeffizient ist exakt implementiert) | 0,6 × 0,1 = 0,06 |

## Nachtrag 2026-10-04 (nach Nutzer-Review von Paper v2)
| ID | Lücke | Warum offen (Beleg) | Neuheitstyp | Prüfbarkeit | VoI |
|---|---|---|---|---|---|
| L9 | Exakte Bestimmung des harmonischen Raums (Delta X in Q*E(w)) für alle w <= 25 und geschlossene Form von f_w | arXiv:1502.06698 (Gl. 3.33, 3.57): Kombinationen angegeben, f_w, g_w „may be determined from the asymptotic behavior“, Werte nur bis w = 9 | (d) geschlossene Form / (a) Erweiterung | mgf_harmonisch_familie (exakt) | 0,5 × 0,9 |
| L10 | Integrationskonstanten g_w der ungeraden Identitäten (geschlossene Form) | arXiv:1502.06698 Gl. 3.34: „g7, g9 are integration constants“; Gl. 3.57 ohne Werte | (d) geschlossene Form (Vermutung) | mgf_relation (Blindtest w = 17) | 0,7 × 0,7 |
| L11 | Vollständiger Relationsraum der zehn C(a,b,c) vom Gewicht 11 mit E(11), zeta(11) | Paper v2: nur Teilbasis bestimmt | (a) | mgf_relationsraum | 0,6 × 0,6 |

## Nachtrag 2 (2026-10-05, vor dem Laborlauf zu F14)
| ID | Lücke | Warum offen (Beleg) | Neuheitstyp | Prüfbarkeit | VoI |
|---|---|---|---|---|---|
| L12 | Beweis der Konstanten g_w (nicht nur numerisch) für alle ungeraden w <= 25 | arXiv:1502.06698 Gl. 3.57: „f_w and g_w … may be determined from the asymptotic behavior near the cusp; their values for weight up to 9 are given in (3.34)“, dort g7, g9 aber unbestimmt; arXiv:1902.04180 Thm. 5.1 gibt das Laurent-Polynom aller C_{u,v;w}, wertet es für diese Identitäten aber nicht aus | (d) geschlossene Form, bewiesen | mgf_identitaet_familie (exakt) | 0,8 × 0,9 |
