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
