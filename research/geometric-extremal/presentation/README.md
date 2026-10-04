# AI Agent Lab · Demo-Materialien

Deutschsprachiges, lokal ausführbares Demo-Paket zur Arbeit *Exact planar few-distance constructions with 111 and 81 points*, Forschungsentwurf vom 4. Oktober 2026. Keine Videos.

## Einstieg

`index.html` im Browser öffnen. Kein Server, Login, Build oder Internetzugang nötig. Schriften sind eingebettet.

- **Labor:** 81/111 Punkte auswählen, Abstandsklassen anklicken, einzelne Punkte isolieren, SVG exportieren.
- **Ergebnis:** Vergleich 80 → 81 und 109 → 111. Balken verwenden eine gemeinsame Nullbasis je Vergleich.
- **Nachweis:** Eine echte lokale Paarzählung prüft jede Histogrammposition; Prüfbericht als JSON speichern.
- **Quellen & Prozess:** Primärquellen und ausdrücklich als Manuskriptbeschreibung gekennzeichnete Prozesszuordnung.

## Material

- `praesentation.html`: sechs Folien; Pfeiltasten, Leertaste, Scrollen oder Wischen.
- `praesentation.pdf`: PDF der sechs Folien.
- `ergebnisblatt.pdf`: einseitiges Handout.
- `ergebnisblatt.html`: druckbare HTML-Version des Handouts.
- `assets/ergebnis-poster.svg` und `.png`: Hauptgrafik für Präsentation, Website und Posts.
- `assets/konstruktion-81.svg` / `konstruktion-111.svg` und entsprechende PNGs: einzelne Punktdiagramme.
- `MODERATION.md`: 3-Minuten-Demo, Sprechernotizen, Publikumsfragen und Caption.
- `paper.pdf`: aktuelle redaktionelle Fassung des Quellmanuskripts.
- `data/`: Koordinaten als CSV, Abstandshäufigkeiten als CSV und vollständige Definitionen als JSON.
- `verify.py`: unabhängiger Prüfer mit Python-Standardbibliothek.

## Exakt prüfen

```sh
python3 verify.py
```

Erwartet: PASS für 81 Punkte / 31 Abstandsklassen / 3.240 Paare und 111 Punkte / 41 Abstandsklassen / 6.105 Paare. Der Prüfer verwendet die expliziten Manuskriptdefinitionen und den kartesischen Ganzzahlnumerator. Vollständige Zeilenintervalle und Halbebenen müssen dieselbe Menge ergeben.

## Aussage und Grenzen

**Belegt:** G(31) ≥ 81 und G(41) ≥ 111. Die Punktmengen übertreffen die Vergleichskonstruktionen von Ahmed–Snevily (2013), Seite 5, mit 80 und 109 Punkten.

**Nicht daraus abzuleiten:** globale Optimalität, vollständige weltweite Rekordprüfung, eine neue allgemeine mathematische Methode oder die Lösung des allgemeinen Erdős–Fishburn-Problems.

Die Grafiken zeigen nur die neuen Punktmengen. Historische Formen werden nicht erfunden. Prozessangaben stammen aus dem Manuskript; es gibt keinen nachgestellten Forschungs-Replay. Die Ladeanzeige im Nachweis begleitet die echte Paarzählung.

## Quellen

- Ahmed–Snevily (2013): https://www.combinatorics.org/ojs/index.php/eljc/article/view/v20i4p33
- Bao–Yu (2025): https://arxiv.org/abs/2509.00880
- Balaji et al., revidierter Preprint: https://arxiv.org/abs/1911.11688

DM Sans: Google Fonts, SIL Open Font License; Lizenz in `assets/FONT-LICENSE.txt`.
