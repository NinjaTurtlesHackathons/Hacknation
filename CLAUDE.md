# Projekt: AI-Labor mit Prüfschicht (Hack-Nation, Challenge #3 Databricks)

**Challenge:** „Agentic Scientific Discovery“: mehrere AI-Agenten recherchieren, bilden Hypothesen, planen Experimente, führen sie aus, lernen aus den Ergebnissen und entscheiden über das nächste Experiment. Ziel: Entdeckung „10× schneller“.
**Unser Ziel:** ein Framework, das die wissenschaftliche Methode ausführbar macht, und ein Paper, das das Framework selbst erzeugt. Jede Behauptung darin ist geprüft.
**Abgabe:** So 15:00 Zürich. Drei Videos: Technical, Team, Live-Demo.
**Methodik:** Skill `rigorous-innovation` (liegt in `.claude/skills/`). Bei Konflikt gilt diese Datei.

## Setup
```bash
git clone --depth 1 https://github.com/doylelab/rxnpredict.git   # Daten: rxnpredict/data_table.csv
pip install numpy pandas scipy scikit-learn
python lab.py 20 400        # reproduziert die Tabelle unter „Stand“ (~15 min auf 2 Kernen)
```

## Rollen
- **A · Outreach:** Forscher anschreiben, Paper bewerten lassen
- **B · KI-Teil:** Hypothesen-Agent, Policy „Hybrid“, Kontaminationstest
- **C · Plattform:** Databricks (Delta, MLflow), Agenten-Loop, Dashboard, Live-Demo
- **D · Prüfen:** Gates, Claims, Negativkontrollen, Lean, Integration alle 3 h (00:00, 03:00, 06:00, 09:00)

Jede Rolle schreibt nur in ihre eigenen Dateien. Ist bei der Integration etwas rot, stoppt die Feature-Arbeit, bis es wieder grün ist.

## Ablauf
Frage → Formalisieren → Hypothesen (KI) → Planen → Ausführen (Lab) → Prüfen (Gates) → Festhalten (Claims) → Paper

## Schnittstellen (fest; Änderungen nur per Eintrag in `decisions.md`)
```python
class Lab:            # einziger Zugang zur Ground Truth
    def run(self, i: int) -> float: ...       # loggt jeden Aufruf in experiments
class Policy:         # random | gp_ei | hybrid
    def propose(self, history: list[tuple[int, float]], rng) -> int: ...
@dataclass
class Hypothesis:     # vom KI-Agenten erzeugt, nie selbst akzeptiert
    id: str; text: str; effect: dict[str, float]; status: str  # offen | bestätigt | widerlegt
class Gate:
    def check(self, results) -> tuple[bool, str]: ...          # (bestanden, Grund)
```

## Tabellen (einzige Quelle für Dashboard und Paper)
- `experiments`: `run_id, seed, policy, dataset, step, x_index, y, mlflow_run_id, ts`
- `claims`: `claim_id, text, level, evidence_run_ids, status`. Werte für `level`: `proved_lean | computed_rigorous | statistical | observed | hypothesis`
- `gates`: `gate, passed, reason, ts`

Das Dashboard liest nur diese drei Tabellen, nie direkt aus dem Code.

## Metrik
- Kandidaten: $n=4132$ Buchwald-Hartwig-Reaktionen aus `doylelab/rxnpredict`, Duplikate gemittelt.
- Treffer: Top-1 % der Ausbeute, $k=41$.
- Primärmetrik: $N_\pi$ = Zahl der Experimente bis zum ersten Treffer.
- Speedup: $\mathbb E[N_{\text{random}}]/\mathbb E[N_\pi]$.
- Theorie-Check: Für Zufallssuche gilt $\mathbb E[N_{\text{random}}]=\frac{n+1}{k+1}=98{,}4$. Weicht die Messung stark ab, ist der Code falsch.

## Stand (Sa 21:00, 20 Seeds, Budget 400)

| Strategie | Ø $N$ | Speedup vs. Zufall (95 %-KI) | $p$ |
|---|---|---|---|
| Zufall | 96,2 | – | – |
| RF + EI | 138,2 | 0,70 (0,40–1,23) | 0,85 |
| GP + EI | 34,2 | 2,81 (1,56–5,02) | 0,006 |
| Negativkontrolle GP | 125,8 | 0,94 (0,55–1,54) | 0,59 |
| Hybrid (Sa 22:30, `python run.py`) | 27,8 | 3,47 (2,05–5,54); vs GP + EI 1,23 (0,84–1,67) | vs GP + EI 0,14 → H1 nicht belegt |
| Hybrid neutral (Kontamination) | 31,2 | vs GP + EI 1,10 (0,82–1,40) | 0,27 |

Rohdaten: `results_selftest.json`, Code: `lab.py`. Volle Pipeline: `python run.py` → `tables/`, Gates und Claims dort (siehe README.md).
Für „10×“ muss Hybrid etwa 3,5× besser sein als GP + EI, also im Mittel ~10 Experimente brauchen.

## Vier Pflicht-Prüfungen (laufen bei jedem Lauf automatisch)
1. **Gepaarter Permutationstest und Bootstrap-KI.** Gate 3 gilt erst bei ≥20 Seeds, $p<0{,}05$ und einem Konfidenzintervall, das 1 ausschließt. Wenige Seeds sind kein Beleg: ein Vorlauf mit 2 Seeds hatte $p=0{,}5$.
2. **Negativkontrolle.** Mit vertauschten Ausbeuten darf keine Strategie den Zufall schlagen.
3. **Kontaminationstest.** Der Datensatz ist öffentlich bekannt. Hybrid läuft deshalb einmal mit neutralen Codes und Deskriptoren statt Namen und SMILES. Bricht der Gewinn dort ein, ist es Auswendiglernen und kommt offen ins Paper.
4. **Benjamini-Hochberg** über alle getesteten Hypothesen, mit $m$ = Gesamtzahl der Tests.

Dazu bei jedem Lauf der Theorie-Check für Zufallssuche.

## Regeln
- Die KI ist nur Generator. Akzeptiert wird ausschließlich über Gate, Statistik oder Lean.
- Die KI sieht Ausbeuten nur über `Lab.run`. Kein direkter Zugriff auf die Daten (Leckschutz).
- Kein Satz im Paper ohne `claim_id` mit Beleg. Kein Zitat ohne Tool-Beleg, sonst `UNVERIFIED`.
- Eine Pipeline, ein Demo-Pfad. Alles, was gezeigt wird, lässt sich aus Code neu erzeugen. Seeds sind fest (1000–1019).
- Lean 4 lokal einsetzen, wo möglich, zum Beispiel für das Lemma $\mathbb E[N_{\text{random}}]=\frac{n+1}{k+1}$. Lean prüft, die KI schreibt den Beweis.
- Bewusst nicht verwendet: e-Werte (es wird nicht adaptiv gestoppt), Conformal (die Garantie bricht bei aktiver Suche), EVPI, Sobol, Pooling.

## Checkpoints
- **23:15:** Hybrid läuft einmal komplett auf 3 Seeds. `gates` reproduziert die Tabelle oben.
- **06:35:** Hybrid schlägt GP + EI nach Pflicht-Prüfung 1. Sonst Fallback: Hybrid bleibt als erklärbares Laborbuch, und das Paper zeigt ehrlich den Speedup der BO. Erster Paper-Entwurf geht an die Forscher.
- **10:50:** Feature-Stopp, danach nur noch Videos, Paper und README.
- **14:00–15:00:** Upload.

**Schlaf** (C und D nie gleichzeitig): B 00:30–03:30 · D 03:30–06:30 · A 03:45–06:15 · C 07:00–10:00
