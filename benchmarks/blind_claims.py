"""Blinder Gegentest der frozen harness: 20 zufällige/konstante Claim-JSONs -> der Verifier darf KEINEN akzeptieren.
python -m benchmarks.blind_claims   (schreibt nach projects/_blindtest_*, nicht in echte Projekte)"""
import json, os, random, shutil, subprocess, sys, tempfile

rng = random.Random(20261004)
L = [  # lattice: Müll, Konstanten, Typ-Verwechslung, Toleranz-Schlupfloch, Selbstbestätigung, falsche Werte
    {}, {"bestanden": True}, {"pruefung": "ok"}, {"pruefung": {"typ": "wahr"}}, {"pruefung": {"typ": "argmin2d"}},
    {"pruefung": {"typ": "argmin2d", "nu": 5, "erwartet": "hexagonal"}},
    {"pruefung": {"typ": "grenzwert", "groesse": "y_inf", "erwartet": 1.0, "toleranz": 10}},
    {"pruefung": {"typ": "grenzwert", "groesse": "y_inf", "erwartet": round(rng.uniform(0.5, 2), 4)}},
    {"pruefung": {"typ": "grenzwert", "groesse": "kappa", "erwartet": round(rng.uniform(-5, 5), 3)}},
    {"pruefung": {"typ": "vorzeichenwechsel", "groesse": "diff_hex_quadrat", "nu_lo": 1, "nu_hi": 100}},
    {"pruefung": {"typ": "vorzeichenwechsel", "groesse": "diff_hex_quadrat", "nu_lo": 6.0, "nu_hi": 6.04}},
    {"pruefung": {"typ": "argmin3d", "nu": 5, "erwartet": "fcc"}},
    {"antwort": "quadratisch", "zahl": 99, "pruefung": {"typ": "grenzwert", "groesse": "y_inf", "erwartet": 99}},
]
PR = [  # proofreading
    {}, {"bestanden": True, "level": "proved_lean"}, {"pruefung": {"typ": "erreichbar"}},
    {"pruefung": {"typ": "untere_schranke", "topologie": "hopfield_n1", "ausdruck": "1"}},
    {"pruefung": {"typ": "erreichbar", "topologie": "hopfield_n1", "eta_max": 1e-12}},
    {"pruefung": {"typ": "unbekannt", "x": rng.random()}},
    {"pruefungen": [{"typ": "erreichbar", "topologie": "hopfield_n1", "eta_max": 1e-9}, {}]},
]
assert len(L) + len(PR) == 20
akz = 0
for dom, claims in (("lattice", L), ("proofreading", PR)):
    proj = f"_blindtest_{dom}"; shutil.rmtree(f"projects/{proj}", ignore_errors=True)
    for i, c in enumerate(claims):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); json.dump(c, f); f.close()
        out = subprocess.run([sys.executable, "-m", "asd.cli", "prüfe", "--domain", dom, "--projekt", proj, "--agent", "blindtest", "--claim-json", f.name],
                             capture_output=True, text=True).stdout
        line = next((l for l in out.splitlines() if l.startswith("RESULT ")), 'RESULT {"bestanden": "FEHLER"}')
        r = json.loads(line[7:]); akz += r["bestanden"] is True
        print(f"{dom:12s} #{i:2d} bestanden={r['bestanden']!s:5s} {r.get('grund', '')[:90]}")
    shutil.rmtree(f"projects/{proj}", ignore_errors=True)
print(f"\nAkzeptiert: {akz}/20  ->  {'GRÜN' if akz == 0 else 'ROT'}")
sys.exit(1 if akz else 0)
