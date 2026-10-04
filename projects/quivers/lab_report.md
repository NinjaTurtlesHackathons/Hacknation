# Laborbericht: Köcher-Domäne

Selbsttest: bestanden. Start 2026-10-04 01:12:09.

## Runde 1 (F1): Gabriel: Welche der betrachteten Köcher sind von endlichem Typ, und hat D4 = star3 genau eine Unzerlegbare je positiver Wurzel?

- [quivers-R1-1] BESTÄTIGT: Die Tits-Form von star1 ist positiv definit (endlicher Typ: Dynkin) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist endlich (exakt, Hauptminoren): {'fuehrende_hauptminoren': ['2', '3']}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-2] BESTÄTIGT: Die Tits-Form von star2 ist positiv definit (endlicher Typ: Dynkin) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist endlich (exakt, Hauptminoren): {'fuehrende_hauptminoren': ['2', '3', '4']}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-3] BESTÄTIGT: Die Tits-Form von star3 ist positiv definit (endlicher Typ: Dynkin) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist endlich (exakt, Hauptminoren): {'fuehrende_hauptminoren': ['2', '3', '4', '4']}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-4] BESTÄTIGT: Die Tits-Form von star4 ist positiv semidefinit, nicht definit (euklidisch, zahm) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist zahm (exakt, Hauptminoren): {'alle_hauptminoren_nichtnegativ': 31, 'det': '0'}  
  Red-Team: Wäre der Typ endlich, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-5] BESTÄTIGT: Die Tits-Form von star5 ist indefinit (wild) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist wild (exakt, Hauptminoren): {'negativer_hauptminor': [0, 1, 2, 3, 4, 5], 'zeuge_q_negativ': [2, 1, 1, 1, 1, 1], 'q_zeuge': -1}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-6] BESTÄTIGT: Die Tits-Form von star6 ist indefinit (wild) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist wild (exakt, Hauptminoren): {'negativer_hauptminor': [0, 1, 2, 3, 4, 5], 'zeuge_q_negativ': [2, 0, 1, 1, 1, 1, 1], 'q_zeuge': -1}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-7] BESTÄTIGT: Die Tits-Form von star7 ist indefinit (wild) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist wild (exakt, Hauptminoren): {'negativer_hauptminor': [0, 1, 2, 3, 4, 5], 'zeuge_q_negativ': [2, 0, 0, 1, 1, 1, 1, 1], 'q_zeuge': -1}  
  Red-Team: Wäre der Typ zahm, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-8] BESTÄTIGT: Die Tits-Form von kronecker ist positiv semidefinit, nicht definit (euklidisch, zahm) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist zahm (exakt, Hauptminoren): {'alle_hauptminoren_nichtnegativ': 3, 'det': '0'}  
  Red-Team: Wäre der Typ endlich, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-9] BESTÄTIGT: Die Tits-Form von cycle3_oriented ist positiv semidefinit, nicht definit (euklidisch, zahm) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist zahm (exakt, Hauptminoren): {'alle_hauptminoren_nichtnegativ': 7, 'det': '0'}  
  Red-Team: Wäre der Typ endlich, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-10] BESTÄTIGT: Die Tits-Form von cycle4_oriented ist positiv semidefinit, nicht definit (euklidisch, zahm) (exakte Hauptminoren).  
  Prüfer: Tits-Form ist zahm (exakt, Hauptminoren): {'alle_hauptminoren_nichtnegativ': 15, 'det': '0'}  
  Red-Team: Wäre der Typ endlich, würde diese Prüfung bestehen. -> durchgefallen
- [quivers-R1-11] BESTÄTIGT: star3 hat genau 12 positive Wurzeln.  
  Prüfer: 12 positive Wurzeln (W-Bahn der einfachen Wurzeln): [(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1), (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1), (2, 1, 1, 1)]  
  Red-Team: Eine 13. Wurzel würde die Anzahl erhöhen. -> durchgefallen
- [quivers-R1-12] BESTÄTIGT: Für star3 über F_2 und alle Dimensionsvektoren 0 < beta <= [2, 1, 1, 1]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 23 Vektoren <= [2, 1, 1, 1] über F_2: reelle Wurzeln genau 1, Nicht-Wurzeln 0  
  Red-Team: Zwei Unzerlegbare zur maximalen Wurzel? -> durchgefallen
- [quivers-R1-13] BESTÄTIGT: Für star3 über F_3 und alle Dimensionsvektoren 0 < beta <= [2, 1, 1, 1]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 23 Vektoren <= [2, 1, 1, 1] über F_3: reelle Wurzeln genau 1, Nicht-Wurzeln 0  
  Red-Team: Zwei Unzerlegbare zur maximalen Wurzel? -> durchgefallen
- [quivers-R1-14] BESTÄTIGT: Für A3 über F_2 und alle Dimensionsvektoren 0 < beta <= [2, 2, 2]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 26 Vektoren <= [2, 2, 2] über F_2: reelle Wurzeln genau 1, Nicht-Wurzeln 0  
  Red-Team: Keine Unzerlegbare zur Wurzel (1,1,1)? -> durchgefallen

## Runde 2 (F2): Vier-Unterraum-Problem (star4 = D~4): Wie sehen alle Unzerlegbaren mit Dimensionsvektor delta aus, und wie viele gibt es über F_q?

- [quivers-R2-15] BESTÄTIGT: Das Radikal der Tits-Form von star4 ist eindimensional, erzeugt von delta = [2, 1, 1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [2, 1, 1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R2-16] BESTÄTIGT: Für star4 ist [2, 1, 1, 1, 1] eine imaginäre Wurzel mit 1 - q(alpha) = 1.  
  Prüfer: [2, 1, 1, 1, 1]: imaginaer, 1 - q = 1  
  Red-Team: Zwei Parameter? -> durchgefallen
- [quivers-R2-17] BESTÄTIGT: Für star4 ist [4, 2, 2, 2, 2] eine imaginäre Wurzel mit 1 - q(alpha) = 1.  
  Prüfer: [4, 2, 2, 2, 2]: imaginaer, 1 - q = 1  
  Red-Team: Ist 2 delta gar keine Wurzel? -> durchgefallen
- [quivers-R2-18] BESTÄTIGT: Für star4 und alpha = [2, 1, 1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 4*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[2, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'burnside', 'burnside']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + 3 (nur P^1 plus zwei Ausnahmen)? -> durchgefallen
- [quivers-R2-19] BESTÄTIGT: Für star4: die Familie V_t mit Dimensionsvektor [2, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0]], '1': [[0], [1]], '2': [[1], [1]], '3': [[1], ['t']]} erfüllt für alle t außerhalb []: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s, V_t) = 0 für s != t   
  Prüfer: Elimination über Q(t): rang(End-System) = 7 von 8 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 8 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb [], s != t  
  Red-Team: Zerfällt V_5? -> durchgefallen
- [quivers-R2-20] BESTÄTIGT: Über F_2 ist die angegebene Liste von 6 Darstellungen von star4 mit Dimensionsvektor [2, 1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 6 paarweise nicht isomorphe Unzerlegbare über F_2; Zählung I = 6 (Methode direkt) -> Liste vollständig  
  Red-Team: Reicht die Liste ohne das letzte Element? -> durchgefallen
- [quivers-R2-21] BESTÄTIGT: Über F_3 ist die angegebene Liste von 7 Darstellungen von star4 mit Dimensionsvektor [2, 1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 7 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 7 (Methode direkt) -> Liste vollständig  
  Red-Team: Reicht die Liste ohne das letzte Element? -> durchgefallen
- [quivers-R2-22] BESTÄTIGT: Über F_5 ist die angegebene Liste von 9 Darstellungen von star4 mit Dimensionsvektor [2, 1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 9 paarweise nicht isomorphe Unzerlegbare über F_5; Zählung I = 9 (Methode burnside) -> Liste vollständig  
  Red-Team: Reicht die Liste ohne das letzte Element? -> durchgefallen
- [quivers-R2-23] BESTÄTIGT: Die Darstellung von star4 mit Dimensionsvektor [1, 1, 1, 1, 1] und Abbildungen {'0': [[1]], '1': [[1]], '2': [[1]], '3': [[1]]} ist absolut unzerlegbar (End/Rad = k).  
  Prüfer: dim End = 1, dim J(End) = 0: absolut unzerlegbar  
  Red-Team: Ist der Vektor imaginär? -> durchgefallen
- [quivers-R2-24] BESTÄTIGT: Die Darstellung von star4 mit Dimensionsvektor [3, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0], [0]], '1': [[0], [1], [0]], '2': [[0], [0], [1]], '3': [[1], [1], [1]]} ist absolut unzerlegbar (End/Rad = k).  
  Prüfer: dim End = 1, dim J(End) = 0: absolut unzerlegbar  
  Red-Team: Ist der Vektor imaginär? -> durchgefallen
- [quivers-R2-25] BESTÄTIGT: Die Darstellung von star4 mit Dimensionsvektor [2, 2, 1, 1, 1] und Abbildungen {'0': [[1, 0], [0, 1]], '1': [[1], [0]], '2': [[0], [1]], '3': [[1], [1]]} ist absolut unzerlegbar (End/Rad = k).  
  Prüfer: dim End = 1, dim J(End) = 0: absolut unzerlegbar  
  Red-Team: Ist der Vektor imaginär? -> durchgefallen
- [quivers-R2-26] BESTÄTIGT: Die Darstellung von star4 mit Dimensionsvektor [2, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0]], '1': [[1], [0]], '2': [[0], [1]], '3': [[0], [1]]} ist über dem algebraischen Abschluss zerlegbar.  
  Prüfer: dim End = 2, dim J(End) = 0: zerlegbar über Q̄  
  Red-Team: Doch unzerlegbar? -> durchgefallen
- [quivers-R2-27] BESTÄTIGT: Für star4 über F_2 und alle Dimensionsvektoren 0 < beta <= [3, 1, 1, 1, 1]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 63 Vektoren <= [3, 1, 1, 1, 1] über F_2: reelle Wurzeln genau 1, Nicht-Wurzeln 0; imaginäre Wurzeln: {'[2, 1, 1, 1, 1]': 6}  
  Red-Team: Keine Unzerlegbare in (3;1,1,1,1)? -> durchgefallen
- [quivers-R2-28] BESTÄTIGT: Für star4 über F_3 und alle Dimensionsvektoren 0 < beta <= [3, 1, 1, 1, 1]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 63 Vektoren <= [3, 1, 1, 1, 1] über F_3: reelle Wurzeln genau 1, Nicht-Wurzeln 0; imaginäre Wurzeln: {'[2, 1, 1, 1, 1]': 7}  
  Red-Team: Keine Unzerlegbare in (3;1,1,1,1)? -> durchgefallen

## Runde 3 (F3): Wilde Sterne (star n, n >= 5): Wie wachsen Parameterzahl und Anzahl der Unzerlegbaren, gibt es eine geschlossene Formel für alpha_n = (2;1^n)?

- [quivers-R3-29] BESTÄTIGT: Für star5 ist [2, 1, 1, 1, 1, 1] eine imaginäre Wurzel mit 1 - q(alpha) = 2.  
  Prüfer: [2, 1, 1, 1, 1, 1]: imaginaer, 1 - q = 2  
  Red-Team: Einen Parameter weniger? -> durchgefallen
- [quivers-R3-30] BESTÄTIGT: Für star6 ist [2, 1, 1, 1, 1, 1, 1] eine imaginäre Wurzel mit 1 - q(alpha) = 3.  
  Prüfer: [2, 1, 1, 1, 1, 1, 1]: imaginaer, 1 - q = 3  
  Red-Team: Einen Parameter weniger? -> durchgefallen
- [quivers-R3-31] BESTÄTIGT: Für star7 ist [2, 1, 1, 1, 1, 1, 1, 1] eine imaginäre Wurzel mit 1 - q(alpha) = 4.  
  Prüfer: [2, 1, 1, 1, 1, 1, 1, 1]: imaginaer, 1 - q = 4  
  Red-Team: Einen Parameter weniger? -> durchgefallen
- [quivers-R3-32] BESTÄTIGT: Für star8 ist [2, 1, 1, 1, 1, 1, 1, 1, 1] eine imaginäre Wurzel mit 1 - q(alpha) = 5.  
  Prüfer: [2, 1, 1, 1, 1, 1, 1, 1, 1]: imaginaer, 1 - q = 5  
  Red-Team: Einen Parameter weniger? -> durchgefallen
- [quivers-R3-33] BESTÄTIGT: Für star5 ist [4, 2, 2, 2, 2, 2] eine imaginäre Wurzel mit 1 - q(alpha) = 5.  
  Prüfer: [4, 2, 2, 2, 2, 2]: imaginaer, 1 - q = 5  
  Red-Team: Bleibt die Parameterzahl beschränkt? -> durchgefallen
- [quivers-R3-34] BESTÄTIGT: Für star5 ist [6, 3, 3, 3, 3, 3] eine imaginäre Wurzel mit 1 - q(alpha) = 10.  
  Prüfer: [6, 3, 3, 3, 3, 3]: imaginaer, 1 - q = 10  
  Red-Team: Bleibt die Parameterzahl beschränkt? -> durchgefallen
- [quivers-R3-35] BESTÄTIGT: Für star4 und alpha = [2, 1, 1, 1, 1] stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit ((q+1)**3 - 1 - 7*q)/(q*(q-1)) überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[2, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'burnside', 'burnside']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: Konstante um 1 verschoben? -> durchgefallen
- [quivers-R3-36] BESTÄTIGT: Für star5 und alpha = [2, 1, 1, 1, 1, 1] stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit ((q+1)**4 - 1 - 15*q)/(q*(q-1)) überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[2, 1, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'burnside', 'burnside', 'burnside']) mit dem Polynom überein; Grad 2 = 1 - q(alpha)  
  Red-Team: Konstante um 1 verschoben? -> durchgefallen
- [quivers-R3-37] BESTÄTIGT: Für star6 und alpha = [2, 1, 1, 1, 1, 1, 1] stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit ((q+1)**5 - 1 - 31*q)/(q*(q-1)) überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[2, 1, 1, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7, 11] (Methoden ['direkt', 'burnside', 'burnside', 'burnside', 'burnside']) mit dem Polynom überein; Grad 3 = 1 - q(alpha)  
  Red-Team: Konstante um 1 verschoben? -> durchgefallen
- [quivers-R3-38] BESTÄTIGT: Für star7 und alpha = [2, 1, 1, 1, 1, 1, 1, 1] stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit ((q+1)**6 - 1 - 63*q)/(q*(q-1)) überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polyn  
  Prüfer: A_[2, 1, 1, 1, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7, 11, 13] (Methoden ['direkt', 'burnside', 'burnside', 'burnside', 'burnside', 'burnside']) mit dem Polynom überein; Grad 4 = 1 - q(alpha)  
  Red-Team: Konstante um 1 verschoben? -> durchgefallen
- [quivers-R3-39] BESTÄTIGT: Für star8 und alpha = [2, 1, 1, 1, 1, 1, 1, 1, 1] stimmt die Anzahl absolut unzerlegbarer Darstellungen über F_q an deg + 2 Primzahlen q mit ((q+1)**7 - 1 - 127*q)/(q*(q-1)) überein; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-P  
  Prüfer: A_[2, 1, 1, 1, 1, 1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7, 11, 13, 17] (Methoden ['burnside', 'burnside', 'burnside', 'burnside', 'burnside', 'burnside', 'burnside']) mit dem Polynom überein; Grad 5 = 1 - q(alpha)  
  Red-Team: Konstante um 1 verschoben? -> durchgefallen
- [quivers-R3-40] BESTÄTIGT: Über F_2 ist die angegebene Liste von 25 Darstellungen von star5 mit Dimensionsvektor [2, 1, 1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 25 paarweise nicht isomorphe Unzerlegbare über F_2; Zählung I = 25 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element -> durchgefallen
- [quivers-R3-41] BESTÄTIGT: Für star5: die Familie V_t mit Dimensionsvektor [2, 1, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0]], '1': [[0], [1]], '2': [[1], [1]], '3': [[1], [2]], '4': [[1], ['t']]} erfüllt für alle t außerhalb []: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s,   
  Prüfer: Elimination über Q(t): rang(End-System) = 8 von 9 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 9 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb [], s != t  
  Red-Team: Zerfällt ein Mitglied? -> durchgefallen
- [quivers-R3-42] BESTÄTIGT: Für star5: die Familie V_t mit Dimensionsvektor [2, 1, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0]], '1': [[0], [1]], '2': [[1], [1]], '3': [[1], [3]], '4': [[1], ['t']]} erfüllt für alle t außerhalb []: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s,   
  Prüfer: Elimination über Q(t): rang(End-System) = 8 von 9 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 9 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb [], s != t  
  Red-Team: Zerfällt ein Mitglied? -> durchgefallen
- [quivers-R3-43] BESTÄTIGT: Für star5: die Familie V_t mit Dimensionsvektor [2, 1, 1, 1, 1, 1] und Abbildungen {'0': [[1], [0]], '1': [[0], [1]], '2': [[1], [1]], '3': [[1], [-1]], '4': [[1], ['t']]} erfüllt für alle t außerhalb []: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s,  
  Prüfer: Elimination über Q(t): rang(End-System) = 8 von 9 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 9 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb [], s != t  
  Red-Team: Zerfällt ein Mitglied? -> durchgefallen

## Runde 4 (F4): 3- und 4-Zykel: Klassifikation der Unzerlegbaren (orientiert und azyklisch), Unabhängigkeit von der Orientierung.

- [quivers-R4-44] BESTÄTIGT: Das Radikal der Tits-Form von cycle3_oriented ist eindimensional, erzeugt von delta = [1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R4-45] BESTÄTIGT: Für cycle3_oriented und alpha = [1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 2*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'direkt', 'direkt']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + n - 2? -> durchgefallen
- [quivers-R4-46] BESTÄTIGT: Über F_3 ist die angegebene Liste von 5 Darstellungen von cycle3_oriented mit Dimensionsvektor [1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 5 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 5 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element vollständig? -> durchgefallen
- [quivers-R4-47] BESTÄTIGT: Das Radikal der Tits-Form von cycle3_acyclic ist eindimensional, erzeugt von delta = [1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R4-48] BESTÄTIGT: Für cycle3_acyclic und alpha = [1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 2*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'direkt', 'direkt']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + n - 2? -> durchgefallen
- [quivers-R4-49] BESTÄTIGT: Über F_3 ist die angegebene Liste von 5 Darstellungen von cycle3_acyclic mit Dimensionsvektor [1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 5 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 5 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element vollständig? -> durchgefallen
- [quivers-R4-50] BESTÄTIGT: Das Radikal der Tits-Form von cycle4_oriented ist eindimensional, erzeugt von delta = [1, 1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [1, 1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R4-51] BESTÄTIGT: Für cycle4_oriented und alpha = [1, 1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 3*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'direkt', 'direkt']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + n - 2? -> durchgefallen
- [quivers-R4-52] BESTÄTIGT: Über F_3 ist die angegebene Liste von 6 Darstellungen von cycle4_oriented mit Dimensionsvektor [1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 6 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 6 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element vollständig? -> durchgefallen
- [quivers-R4-53] BESTÄTIGT: Das Radikal der Tits-Form von cycle4_acyclic31 ist eindimensional, erzeugt von delta = [1, 1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [1, 1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R4-54] BESTÄTIGT: Für cycle4_acyclic31 und alpha = [1, 1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 3*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'direkt', 'direkt']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + n - 2? -> durchgefallen
- [quivers-R4-55] BESTÄTIGT: Über F_3 ist die angegebene Liste von 6 Darstellungen von cycle4_acyclic31 mit Dimensionsvektor [1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 6 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 6 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element vollständig? -> durchgefallen
- [quivers-R4-56] BESTÄTIGT: Das Radikal der Tits-Form von cycle4_acyclic22 ist eindimensional, erzeugt von delta = [1, 1, 1, 1].  
  Prüfer: Radikal: Dimension 1, Erzeuger [1, 1, 1, 1]  
  Red-Team: Anderer Erzeuger? -> durchgefallen
- [quivers-R4-57] BESTÄTIGT: Für cycle4_acyclic22 und alpha = [1, 1, 1, 1] ist die Anzahl absolut unzerlegbarer Darstellungen über F_q für q = 2, 3, 5, 7 gleich 3*q^0 + 1*q^1; da A_alpha nach Kac ein Polynom vom Grad 1 - q(alpha) ist, ist dies das Kac-Polynom.  
  Prüfer: A_[1, 1, 1, 1](q) stimmt an q = [2, 3, 5, 7] (Methoden ['direkt', 'direkt', 'direkt', 'direkt']) mit dem Polynom überein; Grad 1 = 1 - q(alpha)  
  Red-Team: q + n - 2? -> durchgefallen
- [quivers-R4-58] BESTÄTIGT: Über F_3 ist die angegebene Liste von 6 Darstellungen von cycle4_acyclic22 mit Dimensionsvektor [1, 1, 1, 1] eine vollständige Liste der Isoklassen Unzerlegbarer.  
  Prüfer: 6 paarweise nicht isomorphe Unzerlegbare über F_3; Zählung I = 6 (Methode direkt) -> Liste vollständig  
  Red-Team: Liste ohne letztes Element vollständig? -> durchgefallen
- [quivers-R4-59] BESTÄTIGT: Für cycle3_oriented: die Familie V_t mit Dimensionsvektor [1, 1, 1] und Abbildungen {'0': [[1]], '1': [[1]], '2': [['t']]} erfüllt für alle t außerhalb [0]: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s, V_t) = 0 für s != t (paarweise nicht isomorph);  
  Prüfer: Elimination über Q(t): rang(End-System) = 2 von 3 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 3 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb ['0'], s != t  
  Red-Team: Zerfällt t = 4? -> durchgefallen
- [quivers-R4-60] BESTÄTIGT: Für cycle4_acyclic22: die Familie V_t mit Dimensionsvektor [1, 1, 1, 1] und Abbildungen {'0': [[1]], '1': [[1]], '2': [[1]], '3': [['t']]} erfüllt für alle t außerhalb [0]: End(V_t) = k (Ziegel, absolut unzerlegbar) und Hom(V_s, V_t) = 0 für s != t (paarweise   
  Prüfer: Elimination über Q(t): rang(End-System) = 3 von 4 (dim End <= 1), Pivot-Faktoren []; Hom(V_s, V_t): rang 4 (dim Hom <= 0), Pivot-Faktoren ['-s_ + t']; gültig für t, s außerhalb ['0'], s != t  
  Red-Team: Zerfällt t = 4? -> durchgefallen
- [quivers-R4-61] BESTÄTIGT: Die Darstellung von cycle4_oriented mit Dimensionsvektor [3, 3, 3, 3] und Abbildungen {'0': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '1': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '2': [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '3': [[2, 1, 0], [0, 2, 1], [0, 0, 2]]} ist absolut u  
  Prüfer: dim End = 3, dim J(End) = 2: absolut unzerlegbar  
  Red-Team: Zerlegbar? -> durchgefallen
- [quivers-R4-62] BESTÄTIGT: Die Darstellung von cycle3_oriented mit Dimensionsvektor [2, 2, 1] und Abbildungen {'0': [[1, 0], [0, 1]], '1': [[1, 0]], '2': [[0], [1]]} ist absolut unzerlegbar (End/Rad = k).  
  Prüfer: dim End = 2, dim J(End) = 1: absolut unzerlegbar  
  Red-Team: Zerlegbar? -> durchgefallen
- [quivers-R4-63] BESTÄTIGT: Für cycle3_oriented über F_2 und alle 0 < beta <= [2, 2, 2] stimmt die Zahl der Unzerlegbaren mit der Klassifikation (nilpotente Strings S(i, l) und unzerlegbare Moduln über F_q[x, 1/x] für beta = m delta) überein.  
  Prüfer: 26 Dimensionsvektoren <= [2, 2, 2] über F_2: Zählung = Vorhersage (Strings + Monodromie)  
  Red-Team: Keine Unzerlegbare in der Schranke? -> durchgefallen
- [quivers-R4-64] BESTÄTIGT: Für cycle3_oriented über F_3 und alle 0 < beta <= [2, 2, 2] stimmt die Zahl der Unzerlegbaren mit der Klassifikation (nilpotente Strings S(i, l) und unzerlegbare Moduln über F_q[x, 1/x] für beta = m delta) überein.  
  Prüfer: 26 Dimensionsvektoren <= [2, 2, 2] über F_3: Zählung = Vorhersage (Strings + Monodromie)  
  Red-Team: Keine Unzerlegbare in der Schranke? -> durchgefallen
- [quivers-R4-65] BESTÄTIGT: Für cycle4_oriented über F_2 und alle 0 < beta <= [2, 2, 2, 2] stimmt die Zahl der Unzerlegbaren mit der Klassifikation (nilpotente Strings S(i, l) und unzerlegbare Moduln über F_q[x, 1/x] für beta = m delta) überein.  
  Prüfer: 80 Dimensionsvektoren <= [2, 2, 2, 2] über F_2: Zählung = Vorhersage (Strings + Monodromie)  
  Red-Team: Keine Unzerlegbare in der Schranke? -> durchgefallen
- [quivers-R4-66] BESTÄTIGT: Für cycle3_acyclic über F_2 und alle Dimensionsvektoren 0 < beta <= [2, 2, 2]: genau eine Unzerlegbare für reelle Wurzeln, keine für Nicht-Wurzeln.  
  Prüfer: 26 Vektoren <= [2, 2, 2] über F_2: reelle Wurzeln genau 1, Nicht-Wurzeln 0; imaginäre Wurzeln: {'[1, 1, 1]': 4, '[2, 2, 2]': 5}  
  Red-Team: Zwei Unzerlegbare in (1,1,0)? -> durchgefallen

## Runde 5 (F5): Vielfache von delta: Wie viele Unzerlegbare hat 2 delta, und ist A_{2 delta} = A_delta?

- [quivers-R5-67] BESTÄTIGT: Über F_2 hat cycle3_oriented genau 5 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode direkt).  
  Prüfer: I_[2, 2, 2](2) = 5 (Methode: direkt)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-68] BESTÄTIGT: Über F_3 hat cycle3_oriented genau 8 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2](3) = 8 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-69] BESTÄTIGT: Über F_5 hat cycle3_oriented genau 17 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2](5) = 17 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-70] BESTÄTIGT: Über F_2 hat cycle3_acyclic genau 5 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode direkt).  
  Prüfer: I_[2, 2, 2](2) = 5 (Methode: direkt)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-71] BESTÄTIGT: Über F_3 hat cycle3_acyclic genau 8 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2](3) = 8 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-72] BESTÄTIGT: Über F_5 hat cycle3_acyclic genau 17 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2](5) = 17 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-73] BESTÄTIGT: Über F_2 hat cycle4_oriented genau 6 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2, 2](2) = 6 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-74] BESTÄTIGT: Über F_3 hat cycle4_oriented genau 9 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2, 2](3) = 9 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-75] BESTÄTIGT: Über F_2 hat cycle4_acyclic22 genau 6 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2, 2](2) = 6 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen
- [quivers-R5-76] BESTÄTIGT: Über F_3 hat cycle4_acyclic22 genau 9 Isoklassen unzerlegbarer Darstellungen mit Dimensionsvektor [2, 2, 2, 2] (exakte Zählung, Methode burnside).  
  Prüfer: I_[2, 2, 2, 2](3) = 9 (Methode: burnside)  
  Red-Team: Eine Unzerlegbare mehr? -> durchgefallen

## Runde 6 (F6): Gilt das Unzerlegbarkeitskriterium für (2;1^n) (alle v_i != 0, mindestens drei verschiedene Geraden) für ausnahmslos alle Darstellungen?

- [quivers-R6-77] BESTÄTIGT: Über F_2 ist eine Darstellung von star4 mit Dimensionsvektor (2;1^4), gegeben durch Vektoren v_1, ..., v_4 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^3 - 1 - 7  
  Prüfer: alle 256 Darstellungen von star4 mit (2;1^4) über F_2 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 6, Formel = 6  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen
- [quivers-R6-78] BESTÄTIGT: Über F_3 ist eine Darstellung von star4 mit Dimensionsvektor (2;1^4), gegeben durch Vektoren v_1, ..., v_4 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^3 - 1 - 7  
  Prüfer: alle 6561 Darstellungen von star4 mit (2;1^4) über F_3 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 7, Formel = 7  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen
- [quivers-R6-79] BESTÄTIGT: Über F_2 ist eine Darstellung von star5 mit Dimensionsvektor (2;1^5), gegeben durch Vektoren v_1, ..., v_5 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^4 - 1 - 1  
  Prüfer: alle 1024 Darstellungen von star5 mit (2;1^5) über F_2 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 25, Formel = 25  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen
- [quivers-R6-80] BESTÄTIGT: Über F_3 ist eine Darstellung von star5 mit Dimensionsvektor (2;1^5), gegeben durch Vektoren v_1, ..., v_5 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^4 - 1 - 1  
  Prüfer: alle 59049 Darstellungen von star5 mit (2;1^5) über F_3 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 35, Formel = 35  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen
- [quivers-R6-81] BESTÄTIGT: Über F_2 ist eine Darstellung von star6 mit Dimensionsvektor (2;1^6), gegeben durch Vektoren v_1, ..., v_6 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^5 - 1 - 3  
  Prüfer: alle 4096 Darstellungen von star6 mit (2;1^6) über F_2 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 90, Formel = 90  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen
- [quivers-R6-82] BESTÄTIGT: Über F_2 ist eine Darstellung von star7 mit Dimensionsvektor (2;1^7), gegeben durch Vektoren v_1, ..., v_7 in k^2, genau dann unzerlegbar, wenn alle v_i != 0 sind und mindestens drei verschiedene Geraden aufspannen; die Zahl der Isoklassen ist ((q+1)^6 - 1 - 6  
  Prüfer: alle 16384 Darstellungen von star7 mit (2;1^7) über F_2 aufgezählt: unzerlegbar <=> alle v_i != 0 und >= 3 verschiedene Geraden (keine Abweichung); I = 301, Formel = 301  
  Red-Team: Gibt es gar keine Unzerlegbaren? -> durchgefallen

Ergebnis: 82 bestätigte Aussagen, 0 nicht bestätigt, Literatur: 8 DOIs per Crossref bestätigt.
