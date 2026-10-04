"""Tests der Framework-Erweiterungen (CEGIS, Formel-Finder, TMS, eigenständige Zertifikate, Lean).  pytest -q tests/test_extensions.py"""
import json, os, random, shutil, subprocess, sys
import pytest


# ---------------------------------------------------------------- 1 CEGIS ----------------------------------------------------------
def test_cegis_zu_starke_allaussage_wird_verfeinert(monkeypatch):
    from asd import discovery
    from asd.domains.base import get_domain
    D = get_domain("proofreading"); prompts = []
    def forscher(kontext, frage, strategie, lab, salt, max_ops=8, model=None):
        prompts.append(frage)
        k = 2 if "VERMUTUNG v1" in frage else 1                       # v1 zu stark (eta >= e^-Delta), nach Gegenbeispiel v2 (eta >= e^-2Delta)
        return {"strategie": strategie, "final": {"antwort": "ja", "pruefung": {"typ": "untere_schranke", "topologie": "hopfield_n1", "c": 1, "k": k}}}
    monkeypatch.setattr(discovery, "forscher", forscher)
    res = discovery.solve_cascade("", "Welche untere Schranke gilt für hopfield_n1?", salt="t", domain=D, staerkung=0)
    cg = res["cegis"]
    assert res["level"].startswith("computed") and len(cg) == 2
    assert cg[0]["bestanden"] is False and cg[0]["gegenbeispiel"]["art"] == "zertifiziertes_gegenbeispiel"
    assert cg[0]["gegenbeispiel"]["berechnet"] < 0.01 and cg[1]["bestanden"] is True
    assert "GEGENBEISPIEL" in prompts[1].upper() or "Gegenbeispiel" in prompts[1]


# ---------------------------------------------------------------- 2 Formel-Finder -------------------------------------------------
def _punkte_quadratisch():
    import mpmath as mp
    from fractions import Fraction
    mp.mp.dps = 60; out = []
    for p in [Fraction(k, 7) for k in (1, 2, 3, 5, 8, 11, 13)]:
        pf = mp.mpf(p.numerator) / p.denominator; q = (pf + mp.sqrt(pf ** 2 + 4)) / 2      # Q^2 - p Q - 1 = 0
        out.append((str(p), mp.nstr(q - mp.mpf("1e-30"), 45), mp.nstr(q + mp.mpf("1e-30"), 45)))
    return out


def test_identify_findet_formel_und_bestaetigt_an_holdout():
    from asd.tools.identify import identify
    r = identify(_punkte_quadratisch())
    assert r["bestanden"] and "Q^2" in r["relation"] and r["holdout_punkte"] == 2 and "an 2" in r["level"]


def test_identify_bestaetigt_nichts_bei_zufall():
    from asd.tools.identify import identify
    from fractions import Fraction
    rnd = random.Random(1); pts = [(str(Fraction(k, 7)), str(x - 1e-12), str(x + 1e-12)) for k, x in zip((1, 2, 3, 5, 8, 11, 13), [rnd.uniform(1, 3) for _ in range(7)])]
    assert identify(pts)["bestanden"] is False


def test_identify_lehnt_zu_wenige_punkte_ab():
    from asd.tools.identify import identify
    assert identify(_punkte_quadratisch()[:3])["bestanden"] is False


# ---------------------------------------------------------------- 3 Wahrheitspflege ------------------------------------------------
def test_tms_widerruf_stuft_abhaengige_herab_und_stellt_wieder_her():
    from asd import tms
    st = {"claims": [{"id": "L1", "status": "bestätigt"}, {"id": "T1", "status": "bestätigt", "benutzt": ["L1"]},
                     {"id": "K1", "status": "bestätigt", "benutzt": ["T1"]}, {"id": "X", "status": "bestätigt"}]}
    assert tms.widerrufen(st, "L1", "Gegenbeispiel") == ["K1", "T1"]
    s = {c["id"]: c["status"] for c in st["claims"]}
    assert s == {"L1": "widerrufen", "T1": "abhängig_ungültig", "K1": "abhängig_ungültig", "X": "bestätigt"} and st["tms_log"]
    assert sorted(tms.bestaetigen(st, "L1")) == ["K1", "T1"] and all(c["status"] == "bestätigt" for c in st["claims"])
    assert [c["id"] for c in tms.reihenfolge([st["claims"][2], st["claims"][1], st["claims"][0]])] == ["L1", "T1", "K1"]


# ---------------------------------------------------------------- 4 Eigenständige Zertifikate -------------------------------------
def test_zertifikat_eigenstaendig_pass_und_verfaelscht_fail(tmp_path):
    from asd.certificates import _fall, VORLAGE
    from fractions import Fraction
    from asd.domains.base import get_domain
    p = next(pp for pp, w in get_domain("proofreading").selftest() if w and pp.get("typ") == "erreichbar")
    (tmp_path / "check.py").write_text(open(VORLAGE).read())
    cert = {"claim_id": "T", "faelle": [_fall(p)]}; (tmp_path / "certificate.json").write_text(json.dumps(cert))
    run = lambda: subprocess.run([sys.executable, "-I", "check.py"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    assert run() == "PASS"
    cert["faelle"][0]["eta_max"] = "1e-12"; (tmp_path / "certificate.json").write_text(json.dumps(cert))
    assert run().startswith("FAIL") and "eta" in run()
    assert "import asd" not in open(VORLAGE).read() and "from asd" not in open(VORLAGE).read()
