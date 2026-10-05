Fokussierte Gliederung für Version 3 (Form: A. Suleman, „Optimal lattices for a three-body power-law energy“, 2026; zweispaltig).

KERNAUSSAGE (Titel und Abstract daran ausrichten, nichts darüber hinaus behaupten):
Für jedes ungerade Gewicht 3 <= w <= 61 gilt für die Kombination X_w dihedraler Modulgraphfunktionen aus D'Hoker-Green-Vanhove (DGV,
Gl. 3.57) exakt X_w = f_w E_w + g_w zeta(w) mit f_w = 3((w-1)/2)!/w und g_w = 6|B_{w-1}|/((w-1)/2)! (B = Bernoulli-Zahlen).
DGV geben die Kombinationen an; f_w steht dort bis w = 9 (Gl. 3.34), g_w nur für w = 3, 5 (g_7, g_9 als unbestimmte Integrationskonstanten); g_7 später bei arXiv:2109.05017. Titelvorschlag in dieser
Richtung: „Closed forms for the constants in the odd-weight identities between dihedral modular graph functions“.

Theoreme (Reihenfolge):
1. Theorem 1 (Hauptresultat, Claim modular-R17a, Prüfungstyp mgf_identitaet_familie): die Identität für alle ungeraden w <= 61.
   Beweis in drei Schritten: (i) exakte Laplace-Algebra ergibt Delta X_w = w(w-1) f_w E_w; (ii) harmonisch + invariant + polynomiales
   Wachstum => X_w - f_w E_w konstant; (iii) die Konstante ist der tau2^0-Term des Laurent-Polynoms, aus Prop. 2.1 und Thm. 5.1 von
   D'Hoker-Kaidi (arXiv:1902.04180) in rationaler Arithmetik; die Übertragung wurde an deren Gl. (5.19) geprüft, und alle übrigen
   Laurent-Terme stimmen mit f_w E_w überein (Konsistenzprüfung). Annahmen offen nennen: Thm. 5.1 (dort bewiesen) und das Standard-Lemma.
2. Theorem 2 (R14): Eindeutigkeit, d. h. der Raum {X : Delta X in Q E_w} ist eindimensional (ungerade) bzw. null (gerade) für w <= 25.
3. Conjecture 1: die geschlossenen Formen gelten für alle ungeraden w (als Vermutung kennzeichnen; bewiesen bis w = 61).
4. Numerische Bestätigung, unabhängig vom Beweis: Konstanten bei w = 3..17 vom numerischen Prüfer bestätigt; w = 15 war eine
   Vorhersage, w = 17 ein präregistrierter Blindtest. Volle Gewicht-11-Basis hat genau eine Relation (R12; Kriterium 1 verfehlt und
   offen berichtet, Kriterium 2 vorab nachregistriert und bestanden). Härtung (fakt-haertung) einschließlich der dabei gefundenen
   und behobenen Fehler im Auswerter. Abbildung der Konstanten.

Neuheit ehrlich: Die Kombinationen X_w, f_w für w <= 9 und g_w für w = 3, 5 sind bekannt (DGV Gl. 3.34); g_7 steht bei
Dorigoni-Kleinschmidt-Schlotterer (arXiv:2109.05017, Gl. 3.77: C(3,3,1)+C(3,2,2) = 3/7 E7 + zeta(7)/252, mit unserem Ergebnis identisch), dort mit
einem allgemeinen Verfahren über Laurent-Polynome, aber ohne Werte für w > 7; das Laurent-Polynom jeder einzelnen C_{u,v;w} ist bekannt
(D'Hoker-Kaidi Thm. 5.1). In 12 durchsuchten Volltexten steht keine geschlossene Form für allgemeines w. Neu ist die Auswertung für diese Identitäten: die geschlossenen Formen f_w, g_w
und ihr Nachweis für w <= 61. Nichts als „first“ oder „novel“ bezeichnen; Neuheitsstatus exakt wie in den Claims.

Validierung/Anhang (kurz): bekannte Identitäten und Laplace-Gleichungen (w = 3, 5, 7), holomorphe Sturm-zertifizierte Identitäten und die
Eta-Quotienten-Tabelle (R8) als Systemtest des Prüfers; Laborablauf, Präregistrierung, Red-Team nur im Anhang.

Discussion: offene Fragen (i) Beweis für alle ungeraden w (eine Binomialsummen-Identität), (ii) Konstanten der nichtharmonischen
Eigenwertgleichungen, (iii) höhere Schleifenordnung.

Regeln: keine E-Mail-Adressen; zertifizierte Resultate und Negativergebnisse nicht streichen, aber in Validierung/Anhang verschieben.

Layout (zweispaltig): keine langen Wertelisten in Formeln oder Theoremen (sie laufen über den Spaltenrand); die Werte f_w, g_w stehen nur in
EINER Tabelle mit den Spalten w, f_w, g_w (keine Spalte mit Claim-IDs). Theoreme kurz, Formeln höchstens eine Spaltenbreite: in Theorem 1 f_w und g_w in zwei getrennten Displays.
