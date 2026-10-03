"""Hypothesen-Agent. Die KI ist nur Generator: sie sieht Komponenten (Namen/SMILES oder Codes/Deskriptoren),
nie Ausbeuten, und keine Hypothese akzeptiert sich selbst (Status wird nur über `asd.hyptest` gesetzt).

Aufruf:
  python -m asd.hypotheses prompt named|neutral        # Prompt ausgeben (für jedes LLM/jeden Subagenten)
  python -m asd.hypotheses ingest named|neutral FILE --generator "..."   # Antwort parsen, prüfen, speichern
  python -m asd.hypotheses generate named|neutral      # direkt über die Anthropic-API (braucht ANTHROPIC_API_KEY)
"""
from dataclasses import dataclass, asdict, field
import argparse, hashlib, json, os, re, sys, time
import numpy as np
from .data import FACT, load, component_view, design_keys

HYP_DIR = "hypotheses"


@dataclass
class Hypothesis:
    id: str
    text: str
    effect: dict            # {"faktor=stufe": Effekt in Standardabweichungen der Ausbeute}
    status: str = "offen"   # offen | bestätigt | widerlegt
    view: str = ""
    meta: dict = field(default_factory=dict)


TASK = {
    "named": ("Pd-katalysierte Buchwald-Hartwig-Aminierung von Arylhalogeniden mit p-Toluidin "
              "(Pd-Präkatalysator, DMSO, 60 °C). Variiert werden Ligand, Base, Arylhalogenid und ein Additiv "
              "(Isoxazole als mögliche Störstoffe). Komponenten mit Namen und SMILES:"),
    "neutral": ("Eine katalytische Kupplungsreaktion mit vier variablen Komponenten: ligand, base, aryl_halide "
                "(Substrat) und additive. Die Komponenten sind nur mit neutralen Codes und berechneten "
                "DFT-Deskriptoren angegeben (Ladungen in e, Orbitalenergien in Hartree, Dipol in Debye, "
                "NMR-Verschiebungen in ppm, Volumen in Å³, Masse in g/mol):"),
}

INSTRUCTIONS = """
Aufgabe: Formuliere 6 bis 12 überprüfbare Hypothesen, welche Faktorstufen die Ausbeute erhöhen oder senken.
Du kennst keine Messwerte. Stütze dich nur auf chemisches Vorwissen und die Angaben oben.

Antworte ausschließlich mit JSON in genau diesem Format, ohne weiteren Text:
{"hypotheses": [
  {"id": "H1", "text": "<ein Satz mit Begründung>", "effect": {"<faktor>=<stufe>": <zahl>, ...}},
  ...
]}
Regeln für "effect":
- Schlüssel exakt als "<faktor>=<stufe>" mit faktor aus {ligand, base, aryl_halide, additive} und einer Stufe aus der Liste oben.
- Zahl = erwartete Änderung der Ausbeute in Standardabweichungen gegenüber dem Durchschnitt, zwischen -2 und 2.
- Eine Hypothese darf mehrere Stufen umfassen (z. B. alle Arylchloride negativ).
"""


def build_prompt(view: str, ds=None) -> str:
    ds = ds or load()
    comp = component_view(ds, view)
    return TASK[view] + "\n" + json.dumps(comp, ensure_ascii=False, indent=1) + "\n" + INSTRUCTIONS


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m: raise ValueError("keine JSON-Antwort gefunden")
    return json.loads(m.group(0))


def parse(text: str, view: str, ds=None) -> list:
    """Antwort parsen und gegen die erlaubten Stufen prüfen. Ungültige Schlüssel werden verworfen und protokolliert."""
    ds = ds or load()
    valid = set(design_keys(ds, view).ravel())
    hyps = []
    for j, h in enumerate(_extract_json(text)["hypotheses"]):
        eff, dropped = {}, []
        for key, v in h.get("effect", {}).items():
            key = key.replace(" ", "")
            (eff.__setitem__(key, float(np.clip(float(v), -2, 2))) if key in valid else dropped.append(key))
        if not eff: continue
        hyps.append(Hypothesis(id=f"{view}-{h.get('id', f'H{j + 1}')}", text=h.get("text", ""), effect=eff,
                               view=view, meta={"verworfene_schluessel": dropped} if dropped else {}))
    return hyps


def save(hyps, view, prompt, raw, generator):
    os.makedirs(HYP_DIR, exist_ok=True)
    out = {"view": view, "generator": generator, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "prompt": prompt, "raw_response": raw,
           "hypotheses": [asdict(h) for h in hyps]}
    json.dump(out, open(f"{HYP_DIR}/{view}.json", "w"), ensure_ascii=False, indent=1)


def load_hypotheses(view: str) -> list:
    d = json.load(open(f"{HYP_DIR}/{view}.json"))
    return [Hypothesis(**h) for h in d["hypotheses"]]


def prior_mean(hyps, keys: np.ndarray) -> np.ndarray:
    """Vorwissen als Funktion über alle Kandidaten: Summe der Effekte aller passenden Hypothesen.
    keys: (n x 4) Schlüssel 'faktor=stufe' in derselben Sicht wie die Hypothesen."""
    m = np.zeros(len(keys))
    for h in hyps:
        for key, v in h.effect.items():
            m += v * (keys == key).any(1)
    return m


def generate_anthropic(view, model="claude-opus-5-5"):
    import anthropic                                   # pip install anthropic
    prompt = build_prompt(view)
    msg = anthropic.Anthropic().messages.create(model=model, max_tokens=4000,
                                                 messages=[{"role": "user", "content": prompt}])
    raw = "".join(b.text for b in msg.content if b.type == "text")
    save(parse(raw, view), view, prompt, raw, f"anthropic-api:{model}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prompt", "ingest", "generate"])
    ap.add_argument("view", choices=["named", "neutral"]); ap.add_argument("file", nargs="?")
    ap.add_argument("--generator", default="unbekannt"); ap.add_argument("--model", default="claude-opus-5-5")
    a = ap.parse_args()
    if a.cmd == "prompt":
        sys.stdout.write(build_prompt(a.view))
    elif a.cmd == "ingest":
        raw = open(a.file).read(); hyps = parse(raw, a.view); save(hyps, a.view, build_prompt(a.view), raw, a.generator)
        print(f"{len(hyps)} Hypothesen gespeichert in {HYP_DIR}/{a.view}.json")
    else:
        generate_anthropic(a.view, a.model)
