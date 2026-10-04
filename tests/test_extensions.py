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
