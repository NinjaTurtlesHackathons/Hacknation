"""Datensatz rxnpredict (Buchwald-Hartwig, Ahneman et al. 2018) und die zwei Sichten für die KI.

Die KI bekommt nur `component_view(...)` zu sehen: Namen + SMILES ("named") oder neutrale Codes
+ Deskriptoren ("neutral"). Ausbeuten tauchen dort nie auf; die gibt es nur über `Lab.run`.
"""
from dataclasses import dataclass
import numpy as np, pandas as pd

FACT = ["base", "ligand", "aryl_halide", "additive"]
CODE_PREFIX = {"base": "B", "ligand": "L", "aryl_halide": "H", "additive": "A"}
DATA = "rxnpredict/data_table.csv"
DESC_DIR = "rxnpredict/R"
SEEDS = list(range(1000, 1020))
NEUTRAL_SEED = 4242          # feste Zuordnung Name -> Code, unabhängig von der alphabetischen Ordnung

# Kompakte Deskriptor-Auswahl je Komponente (DFT-Deskriptoren aus rxnpredict/R/*.csv)
DESC_COLS = {
    "base": ["*N1_electrostatic_charge", "E_HOMO", "E_LUMO", "dipole_moment", "molecular_volume", "molecular_weight"],
    "ligand": ["*P1_electrostatic_charge", "*C1_NMR_shift", "*C1_electrostatic_charge", "dipole_moment"],
    "aryl_halide": ["*C1_NMR_shift", "*C1_electrostatic_charge", "E_HOMO", "E_LUMO", "dipole_moment", "molecular_volume", "molecular_weight"],
    "additive": ["*N1_electrostatic_charge", "*O1_electrostatic_charge", "E_HOMO", "E_LUMO", "dipole_moment", "molecular_volume", "molecular_weight"],
}


@dataclass
class Dataset:
    X: np.ndarray            # One-hot-Merkmale (n x p), identisch zu lab.py
    y: np.ndarray            # versteckte Ground Truth; nur Lab und Evaluator greifen darauf zu
    table: pd.DataFrame      # Faktorstufen je Kandidat (ohne Ausbeute)
    smiles: dict             # {faktor: {stufe: smiles}}

    @property
    def n(self): return len(self.y)


def load(path=DATA) -> Dataset:
    raw = pd.read_csv(path).dropna(subset=FACT)
    d = raw.groupby(FACT, as_index=False)["yield"].mean()            # Duplikate mitteln (Leakage-Schutz)
    X = pd.get_dummies(d[FACT]).to_numpy(float)
    smiles = {f: raw.drop_duplicates(f).set_index(f)[f"{f}_smiles"].to_dict() for f in FACT}
    return Dataset(X, d["yield"].to_numpy(float), d[FACT].reset_index(drop=True), smiles)


def hits(y, q=0.01):
    """Treffer = Top-q der Ausbeute. Gibt (Maske, k) zurück."""
    k = max(1, int(round(q * len(y)))); thr = np.sort(y)[-k]; hit = y >= thr
    return hit, int(hit.sum())


def neutral_codes(ds: Dataset) -> dict:
    """{faktor: {name: code}}; Codes zufällig, aber fest (NEUTRAL_SEED) zugeordnet."""
    rng = np.random.default_rng(NEUTRAL_SEED); out = {}
    for f in FACT:
        levels = sorted(ds.table[f].unique()); perm = rng.permutation(len(levels))
        out[f] = {lv: f"{CODE_PREFIX[f]}{perm[j] + 1}" for j, lv in enumerate(levels)}
    return out


def descriptors(factor: str) -> pd.DataFrame:
    t = pd.read_csv(f"{DESC_DIR}/{factor}.csv")
    cols = [f"{factor}_{c}" for c in DESC_COLS[factor]]
    t = t.set_index("name")[cols]; t.columns = DESC_COLS[factor]
    return t


def component_view(ds: Dataset, view: str) -> dict:
    """Was die KI über die Komponenten erfährt. view = 'named' | 'neutral'."""
    out = {}
    codes = neutral_codes(ds)
    for f in FACT:
        levels = sorted(ds.table[f].unique())
        if view == "named":
            out[f] = [{"level": lv, "smiles": ds.smiles[f].get(lv, "")} for lv in levels]
        else:
            desc = descriptors(f)
            rows = []
            for lv in levels:
                r = {"level": codes[f][lv]}
                if lv in desc.index:
                    r.update({c: float(v) for c, v in desc.loc[lv].items()})
                else:
                    r["hinweis"] = "keine Deskriptoren verfügbar"
                rows.append(r)
            out[f] = sorted(rows, key=lambda r: int(r["level"][1:]))
    return out


def level_key(factor: str, level: str) -> str:
    return f"{factor}={level}"


def design_keys(ds: Dataset, view: str) -> np.ndarray:
    """Pro Kandidat die Liste der Schlüssel 'faktor=stufe' in der jeweiligen Sicht (für Hypothesen-Effekte)."""
    codes = neutral_codes(ds)
    cols = []
    for f in FACT:
        col = ds.table[f] if view == "named" else ds.table[f].map(codes[f])
        cols.append((f + "=" + col).to_numpy())
    return np.stack(cols, 1)
