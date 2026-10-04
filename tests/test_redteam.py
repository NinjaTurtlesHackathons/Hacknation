"""Positivkontrolle für das Red Team: zwei absichtlich falsche, als bestätigt eingepflanzte Claims muss `redteam --auto` zu Fall bringen;
ein echter Claim muss stehen bleiben, und seine Gegenprüfungen müssen gültig UND relevant sein (also ein wirksames Votum)."""
import copy, json, os, shutil, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PJ = "_redteam_test"


@pytest.fixture(scope="module")
def projekt():
    src = os.path.join(ROOT, "projects", "omni_parallel"); dst = os.path.join(ROOT, "projects", PJ)
    shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst, ignore=shutil.ignore_patterns("certificates", "paper*"))
    st = json.load(open(f"{dst}/state.json")); vorlage = next(c for c in st["claims"] if c["id"] == "proofreading-O21")
    falsch = [("FALSCH-B", {"typ": "schranke_familie", "familie": "gebunden<=2", "ausdruck": "1/D**2", "mitglieder": ["fam2_9"]}),   # fam2_9 unterschreitet 1e-4
              ("FALSCH-A", {"typ": "erreichbar", "topologie": "fam2_1", "params": {}, "eta_max": 1e-5})]                          # fam2_1 ist bewiesen >= 1e-4
    for cid, p in falsch:
        c = copy.deepcopy(vorlage); c.update(id=cid, pruefung=p, red_team=[], status="bestätigt", text="eingepflanzt (falsch)"); st["claims"].append(c)
    json.dump(st, open(f"{dst}/state.json", "w"), ensure_ascii=False)
    yield dst
    shutil.rmtree(dst, ignore_errors=True)


def rt(cid):
    r = subprocess.run([sys.executable, "-m", "asd.cli", "redteam", "--domain", "proofreading", "--projekt", PJ, "--agent", "test", "--claim", cid, "--auto"],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800)
    line = next(l for l in r.stdout.splitlines() if l.startswith("REDTEAM "))
    return json.loads(line[len("REDTEAM "):].split(" HINWEIS")[0])


@pytest.mark.parametrize("cid", ["FALSCH-B", "FALSCH-A"])
def test_redteam_widerlegt_falschen_claim(projekt, cid):
    out = rt(cid)
    assert out["status"] == "angefochten", out
    assert any(g["widerspruch"] for g in out["gegenpruefungen"])


def test_redteam_echter_claim_bleibt_mit_wirksamem_votum(projekt):
    out = rt("proofreading-O19")
    assert out["status"] == "bestätigt" and out["wirksame_gegenpruefungen"] >= 1, out
    assert all(g["gueltig"] for g in out["gegenpruefungen"])
