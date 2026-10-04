---
name: "rigorous-innovation"
description: "Strukturiert zeitbegrenzte Teamarbeit wissenschaftlich (Verifizierer zuerst, Decision Gates, Subagent-Rollen, verifizierte Zitate). Verwenden, wenn der Nutzer einen Hackathon, eine Challenge oder einen 24h-/Wochenend-Sprint startet, ein Projekt für eine Jury baut, eine Start-up-Idee mit Daten oder Prototyp validieren will, ein Problem in einem fremden Fachgebiet lösen soll oder ausdrücklich einen neuartigen, aber belastbaren Ansatz sucht. Nicht für reines Pitch- oder Folien-Feedback, Einzelfragen zu Methoden, Code-Reviews, Bugfixes, Mathe-Übungsaufgaben oder Literaturfragen ohne Bau- oder Entscheidungsziel."
---

# Rigorous Innovation

Ziel: ein Ansatz, der **wissenschaftlich belastbar**, **neuartig** und **schwer schnell nachzubauen** ist. Innovation entsteht durch gezieltes Brechen von Annahmen und strukturell geprüfte Analogien, nie durch unbelegte Behauptungen. Der Mensch ist **Dirigent** und entscheidet an den Gates; Claude orchestriert, hält die Artefakte aktuell und erzwingt die Regeln.

## 0. Modus wählen (zuerst fragen)

| | **Lite** (Default bei ≤2 Personen, ≤12 h oder klarer Aufgabe) | **Full** (≥3 Personen, 24 h+, offenes oder fremdes Problem) |
|---|---|---|
| Artefakte | `context.md`, `decisions.md`, `evidence.md` | zusätzlich `assumptions.md`, `candidates.md`, `prereg.md`, `schema/` |
| Subagent-Rollen | Scout, Red-Team | alle sieben (Abschnitt 3) |
| Gates | 0+1 zusammen (Metrik, Verifizierer, Mathematisieren, Baseline, Coverage), 2, **3**, 4 | 0–5 |
| Datenvertrag | Spaltenliste mit Typen in `context.md` | Schema als Code + `make validate` |

Im Zweifel Lite starten und hochstufen, wenn ein Gate es verlangt. Gate 3 („schlägt die Baseline“) fällt in keinem Modus weg.

**Jury-Typ (in Phase 0 bestimmen, in `context.md`):** *Quant/Science* (Methodik, Validierung, Belege) oder *Produkt/Venture* (Nutzerproblem, Demo, Markt; z. B. AI-Produkt-Hackathons). Bei Produkt/Venture: Storyteller (auch in Lite) und Demo-Skizze ab Phase 0 statt erst Phase 5; Matrix-Kriterium „Jury-Fit“ zählt doppelt (Phase 2); Abgabe-Artefakte Phase 5; bei LLM-Produkt Modul G.

## 1. Prinzipien

1. **Verifizierer zuerst.** Was ist hier das Äquivalent zu Beweisprüfer bzw. Intervallarithmetik? Gibt es ein externes Orakel (Beweis, exakte Rechnung, Ground Truth, Outcome-Daten, physischer Test), darf frei exploriert werden; sonst zuerst einen künstlichen bauen (Metrik, Baseline, synthetische Ground Truth, Manipulationstest).
2. **Verifikation ≠ Validierung.** Beweise zeigen, dass das Modell richtig gelöst ist; ob es das richtige Modell ist, zeigen Daten. Alles Beweisbare formalisieren, den Rest als explizite Annahme führen (Block „Mathematisieren“, Phase 0).
3. **Metrik → Baseline → Coverage → erst dann Recherche.** Neues muss die dümmste funktionierende Lösung schlagen.
4. **Ausführung vor Neuheit.** LLM-Ideen verlieren nach Umsetzung messbar an Wert; Neuheit erst nach Ausführungstest bewerten.
5. **Kein Zitat ohne Tool-Beleg.** Quellen nur aus Tool-Ergebnissen. Sonst `UNVERIFIED`, und dann stützen sie keine Entscheidung.
6. **Analogie trägt nur, was aus der gemeinsamen Struktur folgt.** Alles andere ist Hypothese und braucht einen Vorcheck an echten Daten (Abschnitt 5.2).
7. **Ein Schema, eine Pipeline, ein Demo-Pfad.** Was gezeigt wird, ist aus Code rebuildbar. Keine Parallel-Pipelines.
8. **Markdown ist das Gedächtnis**, PDF nur Export für Menschen und Jury.
9. **Asymmetrische Rollen statt Debatte.** Rollen bekommen unterschiedliche Informationen und Werkzeuge; freie Agent-Debatte schlägt Self-Consistency meist nicht.
10. **Einfach zu verstehen, schwer nachzubauen.** Der Burggraben liegt in kuratierten Daten, Provenance, Validierung und Ausführungsqualität, nicht in Komplexität.
11. **Generator und Prüfer trennen.** Sprachmodelle schlagen nur Kandidaten vor; akzeptiert wird über einen Prüfer (5.1). LLMs sind beim Analogiefinden brüchig (Lewis & Mitchell).

## 2. Menschen und Agents trennen

Subagents sind Werkzeuge, Menschen tragen Verantwortung. Jeder Subagent hat einen menschlichen Owner, der sein Ergebnis abnimmt.

| Teamgröße | Mensch A | Mensch B | Mensch C | Mensch D |
|---|---|---|---|---|
| 1 | Dirigent + alles | — | — | — |
| 2 | Dirigent, Analyse (Scout, Analogist, Statistiker) | Bau + Integration (Architekt, Integrator) | — | — |
| 3 | Dirigent + Story (Storyteller, Red-Team) | Analyse | Bau + Integration | — |
| 4 | Dirigent + Story | Analyse | Bau | Integration + Validierung |

Menschliche Regel bei 24 h: gestaffelt schlafen, nie Bau- und Integrations-Owner gleichzeitig.

## 3. Subagent-Rollen

Subagents nur für parallelisierbare Breitenarbeit (3–5 gleichzeitig); eng gekoppelte Integration macht ein Agent. Rückgabe ≤ ~1.500 Tokens, jede Rolle schreibt nur in ihre Dateien.

- **Scout** (Web-Tools; → `evidence.md`; bekommt keine Lösungsideen): Literatur in drei Schichten (neu ~5 Jahre, analog gleicher kanonischer Typ, alt vor 2000); Seed-Paper + Snowballing Tiefe 1–2. Pro Quelle: ID aus Tool-Ergebnis, Kernzitat ≤2 Sätze, Belegstärke, übertragbarer Mechanismus.
- **Analogist** (Web-Tools; → `candidates.md`; bekommt nur die funktionale Abstraktion ohne Domänenvokabular): ≥2 Quelldomänen (z. B. Biologie, Physik, Ökologie, Epidemiologie, Signalverarbeitung, OR) mit gleicher relationaler Struktur; fern, aber nicht beliebig fern. Pro Domäne: gemeinsames Prinzip in einem Satz (Kandidat für $G$), was daraus folgt und was nur Hypothese ist, eine testbare Vorhersage. Bei Formal-Stufe zusätzlich Span mit Obligationen (5.2). Rein sprachliche Analogien verwerfen und begründen. Generator, nicht Prüfer.
- **Statistiker** (Bash; → `analysis/`): Fermi-Abschätzung vorab; jede Vorhersage gegen eine naive Alternative (Out-of-Sample oder Likelihood-Ratio); Effektgröße mit Intervall; Gesamtzahl aller Tests für FDR; verletzte Voraussetzungen nennen. Kein Ergebnis ohne Code.
- **Architekt** (→ `schema/`, `pipeline/`): Datenvertrag pflegen (Abschnitt 6), UML aus Code generieren, nie umgekehrt.
- **Red-Team** (nur lesen + ausführen; → `analysis/redteam.md`; bekommt Code und Ergebnisse, keine Begründungen): Pre-Mortem („Die Jury hat uns zerlegt. Warum?“), die drei wahrscheinlichsten Fehlerwege konkret testen, Liste der Annahmen, die *jedes* Konkurrenzteam macht, mit Markierung, welche testbar brechbar sind.
- **Integrator** (→ `context.md`, `decisions.md`): alle 3 h mergen, Validierung + Pipeline + Demo laufen lassen; rot = Feature-Stopp bis grün; danach `context.md` aktualisieren.
- **Storyteller** (→ `pitch/`; bei Venture-Jury ab Phase 0 mit Demo-Skizze): jedem Jury-Kriterium einen Demo-Moment und ein Artefakt zuordnen; eine Kerngrafik, drei Zahlen, eine Einsicht („welche Annahme haben wir gebrochen?“); keine Behauptung ohne Beleg in `evidence.md` oder `analysis/`.

## 4. Phasen und Gates (Full-Zeiten für 24 h; Start-up: Abschnitt 10)

**Zeitplan-Variante (Gesamtdauer $D$; für Lite und jede Dauer ≠ 24 h):** Gate 0+1 bei $\approx0{,}15D$, Gate 2 $\approx0{,}25D$, Gate 3 $\approx0{,}6D$, Freeze $\approx0{,}8D$, Rest Story/Video/Puffer. Beispiel Hack-Nation ($D=21$ h, Kickoff Sa 18:00, Abgabe So 15:00 Zürich): Gate 0+1 Sa ~21:10 · Gate 2 Sa ~23:15 · Gate 3 So ~06:35 · Freeze So ~10:50 · Video/README bis ~14:00 · Upload-Puffer bis 15:00.

**Lite:** Phase 0 und 1 laufen als ein Block (bis $\approx0{,}15D$). Gate 0 und Gate 1 werden gemeinsam an dessen Ende mit den Kriterien beider Gates geprüft; danach weiter ab Phase 2.

Am Gate entscheidet der Dirigent: **weiter / Scope verkleinern / Kandidat wechseln / Kill**. Jede Entscheidung in `decisions.md` (`ID | Zeit | Entscheidung | Alternativen | Evidenz | reversibel? | Owner`).

**Phase 0 · Rahmen (T+0–2 h)**
Jury-Rubrik wörtlich und Jury-Typ (§0) in `context.md`; bei Venture Demo-Skizze (Storyteller). Primärmetrik (eine Zahl) und Coverage als Erstmetrik. Kanonische Reformulierung („Welches Standardproblem ist das?“) mit Standardmethoden und deren Annahmen. Verifizierer benennen oder planen. Mathematisieren (Block unten). TRIZ-Widerspruch in einem Satz. Annahmen-Register mit „Was nimmt jeder stillschweigend an?“. Full: `prereg.md` (Hypothese, Metrik, Methodenraum, Erfolgs-/Abbruchkriterium) committen. Scout startet parallel.

**Mathematisieren (Pflichtblock, Ergebnis in `context.md` unter „Modell“)** – so viel wie möglich nachrechenbar machen, damit der nur geglaubte Rest klein und sichtbar wird:
1. **Größen:** Symbol, Einheit, Wertebereich, Datenquelle (z. B. $e_i\ge0$ Emissionen der Firma $i$ in t CO₂e, EPA).
2. **Ziel als Formel** ($S(x)$, $\min_x f(x)$, Trefferquote); bei mehreren Zielen den Konflikt hinschreiben.
3. **Nebenbedingungen** (Budget, Kapazität, Physik), z. B. $\sum_i w_i=1$, $w_i\ge0$.
4. **Axiome** (gewünschte Eigenschaften): Monotonie $e_i'\le e_i\Rightarrow S_i'\ge S_i$, Skaleninvarianz, Symmetrie, Manipulationsschranke $|\Delta S|\le L\lVert\Delta x_{\text{billig}}\rVert$.
5. **Prüfen:** kleine Lemmas beweisen oder Gegenbeispiele suchen; Extremfälle (alles null, riesiger Ausreißer, ein Datenpunkt, Gleichstand); Größenordnung per Überschlag. Status je Axiom: bewiesen / widerlegt / offen.
6. **Rest als Annahme** in `assumptions.md`, wird mit Daten getestet.
Hat das Ziel eine bekannte Form (LP, Ranking-Modell, Schätzproblem), deren Werkzeuge und Garantien nutzen. Nur bei Formal-Stufe (5.2) zusätzlich: Signatur, $(P_-,P_+,R_P)$ mit Prüfer, Symmetrien, Invarianten.

→ **Gate 0:** Metrik + Verifizierer stehen, Mathematisieren-Block ausgefüllt (Punkte 1–5, Axiome mit Status). Sonst: Aufgabe neu deuten, mit Mentoren klären.

**Phase 1 · Baseline und Coverage (T+2–6 h)**
Dumme Baseline End-to-End. Coverage pro Quelle/Feld/Segment messen und sichtbar machen. 30 min EDA (Verteilungen, Lücken, Ausreißer, Duplikate). Demo-Skelett, das nur Endtabellen liest.
→ **Gate 1:** Baseline läuft, Coverage bekannt. Coverage zu niedrig → Scope verkleinern oder Pooling einplanen, nie still imputieren.

**Phase 2 · Recherche, Analogie, Annahmenbruch (T+6–9 h)**
Scout (Zitate prüfen, Abschnitt 8), Analogist, Red-Team-Annahmenliste, Statistiker-Vorcheck parallel. Pro Kandidat: **statistischer Vorcheck** an echten Daten gegen naive Alternative; Stufe standardmäßig $(\emptyset,\infty)$. **Formal-Stufe** (5.2) nur, wenn eine Lösungsmethode aus einer anderen Domäne übertragen wird oder Modul C/F aktiv ist: Invariantenfilter → Span + Barthas Gate → Reduktion mit Rückweg → Stufe $(\Phi,\varepsilon)$. Optional Literature-Based Discovery (Zwischenkonzepte B zwischen Literatur A und C als Mechanismen). Auswahl per Matrix (je 1–5): verifizierbar*, erwarteter Gewinn vs. Baseline, Datenlage*, Aufwand ≤ Timebox, Jury-Fit (bei Venture-Jury ×2), schwer kopierbar, in 30 s erklärbar. (* K.-o. bei 1.)
→ **Gate 2:** gewählter Kandidat besteht den Vorcheck, Stufe eingetragen (Standard $(\emptyset,\infty)$); bei Formal-Stufe zusätzlich Span mit Status aller Obligationen und Zeuge für die Stufe; Fallback benannt. Kein Kandidat besteht → bester In-Domain-Ansatz.

**Phase 3 · Bau (T+9–15 h)**
Im bestehenden Vertrag bauen; Relaxationen nur mit bewiesener Schranke ($\Omega\subseteq\Omega'$, $J'\le J$ ⇒ $\inf J'\le\inf J\le J(y)$), Lücke berichten; Integration bei T+12 h und T+15 h.
→ **Gate 3:** schlägt Baseline auf der Primärmetrik. Sonst Fallback.

**Phase 4 · Validierung und Red-Team (T+15–19 h)**
Batterie aus Abschnitt 7, dazu: übertragene Lösungen **im Ziel neu prüfen** (5.1), Kondition $\delta/\mu$, falls $J$ stark konvex ist; sonst Sensitivität empirisch (Modul A bzw. Ablation) (5.3). Bricht etwas, werden Claims herabgestuft und offen gezeigt.
→ **Gate 4**, danach **Feature-Freeze bei T+19 h**.

**Phase 5 · Story, Demo, Export (T+19–24 h)**
Demo aus Code neu bauen, Rubrik-Mapping, 3-Minuten-Skript, Proben; Burggraben-Check (was kopiert ein Konkurrent in 1 h / 1 Tag / 1 Woche?); PDF per Pandoc; letzte Stunde Puffer. **Venture-Jury zusätzlich:** 2-min-Video (Problem → Demo → Zahl → Ausblick), README mit Eval-Ergebnis (Baseline vs. wir, Hold-out), ein Satz „Warum jetzt / warum wir“.

## 5. Mathematisches Fundament (kompakt)

Leitsatz: **Finden darf beliebig sein, akzeptiert wird nur, was geprüft ist.**

### 5.1 Zertifikate (immer)
| Behauptung | Zertifikat | Prüfer |
|---|---|---|
| Optimalität LP/konvex | duale Lösung, Lücke $\le\varepsilon$ | exakt rational einsetzen |
| MIP-Optimalität | VIPR-Zertifikat | exakter Checker |
| Schranke | Intervall-Einschließung | Intervallarithmetik |
| Satz | Beweisterm | Lean |
| „gilt nicht“ | Gegenbeispiel | Einsetzen |
| $A\cong B$ / $A\not\cong B$ | Abbildung auf Erzeugern / verschiedene Invariante | Relationen prüfen / Invariante rechnen |

**Neuprüfung im Ziel:** Eine über eine Reduktion oder Analogie gewonnene Lösung wird im Zielproblem neu geprüft ($V_{\text{Ziel}}=1$ tatsächlich berechnet), nie „geerbt“.

### 5.2 Formal-Stufe (nur bei Methodentransfer aus anderer Domäne oder Modul C/F)
- **Analogie als Span** $T_S\xleftarrow{\sigma_S}G\xrightarrow{\sigma_T}T_T$ über einer gemeinsamen kleinen Theorie $G$. **Übertragen wird nur, was aus $G$ folgt:** $G\vdash\chi\Rightarrow T_T\vdash\sigma_T(\chi)$. Zertifikat sind die Obligationen $T_T\vdash\sigma_T(\gamma)$ für alle Axiome $\gamma$ von $G$. Was nicht aus $G$ folgt, ist Hypothese (Status *offen*).
- **Barthas Gate** für eine Aussage $\chi$: (1) *prior association* $G\vdash\chi$ (oder explizit begründet plausibel); (2) *keine kritische Differenz* $T_T\cup\sigma_T(G)\nvdash\neg\sigma_T(\chi)$. Nur plausibel ⇒ Plausibilität, keine Bestätigung.
- **Reduktion mit Rückweg:** Problem $=(P_-,P_+,R)$ (Instanzen, Antworten, Korrektheit). Morphismus $\mathbf A\to\mathbf B$: $f_-:B_-\to A_-$ (**Instanzen rückwärts**), $f_+:A_+\to B_+$, mit $A(f_-(b),a)\Rightarrow B(b,f_+(a))$. Die Kontravarianz von $f_-$ ist die typische Fehlerstelle. Quantitativ: $c_B(b,f_+(a))\le g\big(c_A(f_-(b),a)\big)$, $g$ monoton, $g(0)=0$; Komposition $g_2\circ g_1$. L-Reduktion (Minimierung): $g(t)=\alpha\beta t$, sofern $c$ der relative Fehler $c=(J-\operatorname{OPT})/\operatorname{OPT}$ ist; für Maximierung separat nachrechnen.
- **Stufe** $(\Phi,\varepsilon)$: $\Phi$ = übertragene Satzklasse mit Richtung (Isomorphie: alle; Homomorphismus: positiv-existenzielle, vorwärts; Einbettung: ∃ vorwärts, ∀ rückwärts; Theorie-Morphismus: alle Theoreme von $G$), $\varepsilon$ = Verlust. Ohne Zeugen gilt $(\emptyset,\infty)$.

### 5.3 Robustheit und billige Filter
- **Kondition (nur falls $J$ stark konvex; sonst empirisch über Modul A/Ablation):** $J$ $\mu$-stark konvex, $\sup\lVert\nabla\tilde J-\nabla J\rVert\le\delta$ ⇒ $\lVert\tilde x^\ast-x^\ast\rVert\le\delta/\mu$; beim Transfer zusätzlich $\operatorname{Lip}(\psi)$. Kleines $\mu$ = schlecht konditioniert.
- **Invarianten:** $I(A)\ne I(B)\Rightarrow A\not\cong B$; erst billige Invarianten (Symmetriegruppe, Erhaltungsgrößen, dimensionslose Gruppen aus $\ker D$, Skalierungsexponenten), dann teure Abbildungssuche. Buckingham gilt nur bei vollständiger Ähnlichkeit (Barenblatt).
- **Symmetrie:** Bei $J\circ g=J$, $g\Omega=\Omega$ nur auf einem Fundamentalbereich suchen.
- Ähnlichkeit ist relativ zur Signatur: $\mathbb Q(\sqrt2)\cong\mathbb Q(\sqrt3)$ als $\mathbb Q$-Vektorräume, nicht als Körper.

## 6. Datenvertrag

Schichten: `src_` (Rohquellen, unveränderlich, Provenance + Einheiten) → `ana_` (dokumentierte Aggregationen) → `int_` (Integration, Entity Resolution mit Brückentabellen: `match_score`, `match_method`, `reviewed`) → optional `cfg_`/`mc_` (Modul A) → `out_` (einzige Quelle für Demo). Kantentypen: `derives_from` (deterministisch), `uses_fields` (liest Spalten, kein FK), `links_nm` (n:m über Brückentabelle). Jede Tabelle: Grain, Primärschlüssel, Typen, Nullbarkeit, Wertebereiche, Einheiten. Full: als Pandera-/Pydantic-Schema, `validate` blockiert die Pipeline bei Fehlern.

## 7. Validierungsbatterie

- **Synthetische Ground Truth** mit bekannter Antwort; Recovery messen. Generator ≠ Modell.
- **Negativkontrolle:** Das System muss scheitern, wenn es Falsches belegen soll.
- **Ablation** jeder Stufe und Quelle, mehrfach laufen lassen; Leave-one-source/segment-out.
- **Manipulationstest (Goodhart):** Wie billig lässt sich das Ergebnis gezielt verschieben?
- **Leakage:** Vorverarbeitung auf Gesamtdaten, Zeitleakage, Ziel-Proxy als Feature, Duplikate durch Entity-Resolution-Fehler.
- **Multiple Testing:** Benjamini-Hochberg mit $m$ = alle durchgeführten Tests.
- **Externe Validierung:** Outcome-Daten, Experten-Paarvergleiche (Bradley-Terry, Position randomisieren) oder physischer Test. Stabilität ist keine Validität.
- **Unsicherheit zeigen:** Intervalle oder Verteilungen statt Punktwerte.

## 8. Zitatprüfung

Per Skript; blockiert die Sandbox Crossref/arXiv, per `WebFetch` auf `https://api.crossref.org/works/{DOI}` bzw. `https://arxiv.org/abs/{ID}` und Titel vergleichen. Scheitert beides: `UNVERIFIED`.

```python
# scripts/verify_citations.py — Eingabe TSV: Titel<TAB>DOI-oder-arXiv-ID; Ausgabe: Status, Ähnlichkeit, gefundener Titel
import re, sys, json, difflib, urllib.request, urllib.parse
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ri/1.0"}), timeout=20) as r: return r.read().decode()
def check(title, ref):
    try:
        t = (json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(ref)))["message"]["title"][0]
             if ref.lower().startswith("10.") else re.findall(r"<title>(.*?)</title>", get("http://export.arxiv.org/api/query?id_list=" + ref), re.S)[1])
        s = difflib.SequenceMatcher(None, title.lower(), " ".join(t.split()).lower()).ratio()
        return ("VERIFIED" if s >= 0.9 else "MISMATCH"), round(s, 2), " ".join(t.split())
    except Exception as e:
        return "NETZ/FEHLER → per WebFetch prüfen", 0, type(e).__name__
for line in open(sys.argv[1]):
    if "\t" in line:
        title, ref = line.rstrip("\n").split("\t")[:2]; print(*check(title, ref.strip()), title, ref, sep="\t")
```

```python
# scripts/coverage_report.py — Aufruf: datei.csv key_spalte [segment_spalte]
import sys, pandas as pd
df = pd.read_csv(sys.argv[1]); key = sys.argv[2]; seg = sys.argv[3] if len(sys.argv) > 3 else None
vals = df.drop(columns=[c for c in (key, seg) if c])
per_unit = vals.notna().groupby(df[key]).any()
print("Anteil Einheiten mit ≥1 Wert je Spalte:\n", per_unit.mean().sort_values().round(3).to_string())
if seg:
    print("\nCoverage je Segment:\n", vals.notna().groupby(df[seg]).mean().round(2).to_string())
```

```python
# scripts/validate.py — Aufruf vom Projekt-Root: python scripts/validate.py [daten_ordner=pipeline/out]
# schema/contracts.json: {"out_scores.csv": {"pk": ["id"], "cols": {"id": "int", "score": "float"},
#                          "notnull": ["id"], "range": {"score": [0, 1]}}}   Typen: int | float | str | bool
import sys, json, pathlib, pandas as pd, pandas.api.types as T
root = pathlib.Path(__file__).resolve().parent.parent
data = root / (sys.argv[1] if len(sys.argv) > 1 else "pipeline/out")
# int: Lücken machen Int-Spalten zu float64, daher Ganzzahligkeit prüfen
TYPES = {"int": lambda s: T.is_integer_dtype(s) or (T.is_numeric_dtype(s) and not T.is_bool_dtype(s) and (s.dropna() % 1 == 0).all()),
         "float": lambda s: T.is_numeric_dtype(s) and not T.is_bool_dtype(s),
         "bool": lambda s: T.is_bool_dtype(s) or (T.is_object_dtype(s) and set(s.dropna().unique()) <= {True, False}),
         "str": lambda s: T.is_object_dtype(s) or T.is_string_dtype(s)}
ok = True
for f, c in json.load(open(root / "schema/contracts.json")).items():
    p = data / f
    if not p.exists(): print(f, ["Datei fehlt"]); ok = False; continue
    df = pd.read_csv(p); err = []
    for k, t in c["cols"].items():
        if k not in df: err.append(f"fehlt: {k}")
        elif not TYPES[t](df[k]): err.append(f"{k}: erwartet {t}, ist {df[k].dtype}")
    if c.get("pk") and df.duplicated(c["pk"]).any(): err.append("PK nicht eindeutig")
    err += [f"NULL in {k}" for k in c.get("notnull", []) if k in df and df[k].isna().any()]
    err += [f"{k} außerhalb {r}" for k, r in c.get("range", {}).items() if k in df and not df[k].dropna().between(*r).all()]
    print(f, "OK" if not err else err); ok &= not err
sys.exit(0 if ok else 1)
```

## 9. Module nach Aufgabentyp (in Phase 0 eins oder zwei auswählen und in `context.md` festhalten; die übrigen ignorieren)

**A · Ranking/Score/Index** (z. B. ESG, Bewertung, Auswahl): Multiverse bzw. Specification Curve über den Methodenraum: `cfg_` als Kreuzprodukt der Methodenwahlen plus Validitätsregeln als Code und Gewichte der Spezifikationen; `mc_` mit festen Seeds. Ausgaben: $\mathbb P(\text{rank}_i \le k)$, Rang-Bänder, Kendall $\tau$ zwischen Spezifikationen, Sobol $S_i$ **und** $S_{T_i}$ (bei abhängigen Faktoren Shapley-Effekte), Permutations-Nulltest. Coverage-Lücken: `coverage_tier` + Partial Pooling. Axiome des Scores (Monotonie, Skaleninvarianz, Manipulationsschranke $|\Delta S| \le L\,\lVert \Delta x_{\text{billig}} \rVert$). Qualität/Glaubwürdigkeit als separate Achse. Kerngrafik: Anteil der Einheiten, deren naiver Rang außerhalb ihres 80-%-Bands liegt.

**B · Vorhersage/ML:** Split nach Zeit/Gruppe; Leakage-Audit vor dem ersten Modell; starke einfache Baseline; Kalibrierung + Conformal-Intervalle; Fehleranalyse nach Segmenten; Feature-Ablation über mehrere Seeds. Fehler: Tuning auf dem Testset, Metrik passt nicht zur Entscheidung, Gewinn kleiner als Seed-Varianz.

**C · Optimierung/Planung:** Formulierung (LP/MIP/Graph/Flow) mit allen Constraints schriftlich; Relaxation → Schranke; Dualitätslücke als Zertifikat (VIPR für MIP); Heuristik auf kleinen Instanzen gegen exakte Lösung; robuste/szenariobasierte Variante; Machbarkeit unabhängig nachrechnen. Fehler: vergessene Constraints, Heuristik ohne Schranke, Optimum kippt bei kleiner Störung.

**D · Kausal/Policy:** nur bei echtem Treatment mit Zeitpunkt und Vorperioden. Kausalgraph mit Confoundern; DiD mit geprüften Parallel Trends (gestaffelt: moderne Schätzer statt naivem TWFE); Synthetic Control; Double ML mit Cross-Fitting; Placebo-Tests; Sensitivität für unbeobachtete Confounder. Fehler: Assoziation als Wirkung verkaufen.

**E · Hardware/Produkt:** First Principles + Fermi gegen physikalische Grenzen; Riskiest Assumption zuerst physisch/per Nutzertest; Simulation gegen ≥1 Messung kalibrieren; Toleranzanalyse per Monte Carlo; 2–3 treibende Parameter; Wiederholmessungen mit Messunsicherheit. Fehler: Simulation als Beweis, Messung ohne Fehlerbalken, Demo nur im Labor, Kosten ignoriert.

**F · Mathematik:** Aussage exakt (Quantoren, Randfälle); erst numerisch explorieren; Orakel (Lean, Intervallarithmetik, exakte Rechnung); Negativkontrolle (Prover lehnt knapp falsche Aussagen ab); Abgleich mit bekannten Identitäten und unabhängigen Bibliotheken; Vertrauensbasis offenlegen. Fehler: Numerik als Beweis, `sorry` übersehen, Rundung nicht eingeschlossen.

**G · AI-App/LLM-Produkt:** Verifizierer = Eval-Set aus 20–50 Fällen mit erwarteter Antwort oder Bewertungsregel, angelegt vor dem ersten Prompt-Tuning, mit Hold-out, der nie zum Tuning dient; Baseline = einfachster Prompt bzw. ein Modellaufruf ohne Pipeline, Gewinn als „Baseline X % → wir Y %“; LLM-as-Judge nur mit Stichprobe gegen Menschenurteil, Position und Länge randomisieren; Negativkontrolle: Fälle, in denen das System ablehnen oder „weiß nicht“ sagen muss; Kosten, Latenz und Fehlerrate je Anfrage messen und in der Demo zeigen; Demo-Pfad aus Code mit festen Beispielen und Fallback bei API-Ausfall. Fehler: Tuning auf dem Eval-Set, Demo nur aus Cherry-Picking-Beispielen, Wrapper ohne messbaren Mehrwert, keine Nutzer-/Problemvalidierung.

Weitere Werkzeuge nach Bedarf: Value of Information, inverse Probleme, Bayesian Optimization, Optimal Transport, Extremwerttheorie, Copulas, Graph-Analyse, Bootstrap; TDA, ABM, Causal Discovery nur, wenn die Aufgabe sie verlangt.

## 10. Start-up-Variante (4–6 Wochen)

W1: Rahmen + Riskiest Assumption Test mit echten Kunden/Experten (keine LLM-Personas). W2: Baseline, Vertrag, Coverage. W3: vollständigere Recherche, Snowballing Tiefe 2, Analogie-Kandidaten. W4–5: Bau, wöchentliche Gates, externe Validierung gegen Outcomes. W6: Moat-Analyse, dann fortsetzen / pivotieren / stoppen. Red-Team zusätzlich durch einen externen Menschen.

## 11. Anti-Patterns (ETHack 2026)

Parallele Pipelines und mehrere Dashboards · Demo nicht aus Code rebuildbar · Coverage (127/500) erst spät sichtbar · Recherche vor Baseline · PDFs als KI-Gedächtnis · Methoden-Kreuzprodukt ohne Validitätsregeln · kein externes Validierungsziel.

## 12. Skill-Evaluation

≥4 verschiedenartige Replays mit und ohne Skill (Ranking/ETHack 2026, ML, Optimierung, Hardware). Messen: Zeit bis Baseline, Zeitpunkt der Coverage-Erkennung, Anteil verifizierter Zitate, parallele Code-Pfade, Gewinn vs. Baseline. Ändern nur bei Verbesserung über mehrere Tasks.

## 13. Belege und Grenzen

Titel und Autoren verifiziert am 2026-10-02 (arXiv/Crossref/Verlag): Si et al. arXiv:2409.04109 und arXiv:2506.20803 (Ideation, Ideation–Execution Gap) · Cemri et al. arXiv:2503.13657 (MAST) · Smit et al. arXiv:2311.17371 · Zhang et al. arXiv:2502.08788 (Agent-Debatte) · Silberzahn et al. doi:10.1177/2515245917747646 · Steegen et al. doi:10.1177/1745691616658637 · Simonsohn et al. doi:10.1038/s41562-020-0912-z · Kapoor & Narayanan doi:10.1016/j.patter.2023.100804 · Gick & Holyoak doi:10.1016/0010-0285(80)90013-4 · Blass arXiv:math/9309208 · Goguen & Burstall doi:10.1145/147508.147524 · Farmer et al. doi:10.1007/3-540-55602-8_192 · Cousot & Cousot doi:10.1145/2535838.2537850 · Chazal et al. doi:10.1145/1542362.1542407 · Bjerkevik et al. doi:10.1007/s10208-019-09442-y · McConnell et al. doi:10.1016/j.cosrev.2010.09.009 · Lewis & Mitchell arXiv:2411.14215 · de Paiva, „The Dialectica categories“, Cambridge TR UCAM-CL-TR-213 (1991) · de Paiva, „A Dialectica-like model of linear logic“, CTCS 1989, doi:10.1007/BFb0018360.

Der quantitative Morphismus in 5.2 ist für $g=\mathrm{id}$ ein Dialectica-Morphismus über dem Lineal $([0,\infty],\ge)$ (de Paiva 1989/1991, mit Lineal-Werten nach Hyland & de Paiva); die Verzerrung durch monotones $g$ ist eine naheliegende Variante, kein eigener Beitrag.

Nicht verifiziert: Crescenzi 1997, Bartha 2010, Hyland & de Paiva (Lineales), Barenblatt, VIPR, Konferenz-Zuordnungen, Anthropic-Zahlen. Verifiziert = Quelle existiert unter diesem Titel; Zahlenwerte nicht erneut nachgelesen.
Befunde älterer Modelle: Richtung strukturell, Größen heute vermutlich kleiner. Hackathon-Evidenz dünn; Rubrik hat Vorrang.