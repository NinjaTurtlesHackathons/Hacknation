"""Tests für den MCP-Server probatum (Domäne proofreading).  pytest -q tests/test_mcp_server.py"""
import json, os, re, tempfile
import pytest

os.environ["PROBATUM_HOME"] = tempfile.mkdtemp(prefix="probatum-test-")
from asd import mcp_server as M  # noqa: E402

PARAMS = {"bind+": 5.345, "bind-": 9.248, "akt0+": -1.038, "verw1+": 3.299, "verw1-": 5.857, "prod+": -7.902, "mu": 10.212, "muP": 0.0}


@pytest.fixture(scope="module")
def eta():
    """Exakter Wert (7 signifikante Stellen) aus dem Verifier für den Referenzpunkt."""
    r = M.selftest("proofreading"); assert r["ergebnis"] == "PASS", r
    out = M.submit_claim("proofreading", {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": 1.0})
    assert out["bestanden"], out
    return float(re.search(r"eta = ([0-9.eE+-]+)", out["grund"]).group(1))


def test_gate_vor_selbsttest():
    M._SELFTEST_OK.pop("lattice", None)
    assert "fehler" in M.run_experiment("lattice", {"op": "energy2d", "args": {"tau": [0, 1], "nu": 5}})


def test_selftest_und_describe(eta):
    d = M.describe("proofreading"); assert "erreichbar" in d["claim_schemas"] and "optimize" in d["experiment_schemas"]
    assert M.list_domains()["proofreading"]["selbsttest_bestanden"] is True


def test_gueltiger_claim_bestaetigt(eta):
    out = M.submit_claim("proofreading", {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": eta * (1 + 1e-6)})
    assert out["bestanden"] and out["level"] == "computed_rigorous" and out["claim_id"]


def test_um_1e6_verschoben_abgelehnt(eta):
    out = M.submit_claim("proofreading", {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": eta * (1 - 1e-6)})
    assert not out["bestanden"] and out["claim_id"] is None


def test_eigene_toleranz_ignoriert(eta):
    out = M.submit_claim("proofreading", {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": eta * (1 - 1e-6), "toleranz": 0.5})
    assert not out["bestanden"] and out["toleranz_ignoriert"] == ["toleranz"]


def test_unbekanntes_feld_abgelehnt(eta):
    out = M.submit_claim("proofreading", {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": 1.0, "befehl": "rm -rf /"})
    assert not out["bestanden"] and "unbekanntes Feld 'befehl'" in out["grund"]
    assert "fehler" in M.run_experiment("proofreading", {"op": "evaluate", "args": {"topologie": "hopfield_n1", "params": PARAMS, "pfad": "/etc/passwd"}})
    assert "fehler" in M.run_experiment("proofreading", {"op": "__import__", "args": {}})


def test_experiment_und_record(eta):
    r = M.run_experiment("proofreading", {"op": "evaluate", "args": {"topologie": "hopfield_n1", "params": PARAMS}})
    assert r["experiment_id"].startswith("E") and "eta" in r["ergebnis"]
    rec = M.research_record("proofreading", 50)["eintraege"]; assert any(x["tool"] == "submit_claim" for x in rec)


def test_challenge_und_listen(eta):
    cid = M.list_claims("proofreading")["claims"][0]["claim_id"]
    out = M.challenge_claim("proofreading", cid, {"typ": "erreichbar", "topologie": "hopfield_n1", "params": PARAMS, "eta_max": eta * 0.5})
    assert out["status"] == "bestätigt" and out["gegenpruefung_bestanden"] is False
    assert M.list_claims("proofreading", "abgelehnt")["abgelehnt"]
    p = M.build_paper("proofreading", "T", "A"); assert p["claims"] and p["regeln"]


def test_timeout_greift(eta):
    alt = M.TIMEOUT; M.TIMEOUT = 3
    try: r = M.run_experiment("proofreading", {"op": "optimize", "args": {"topologie": "hopfield_n2", "starts": 200}})
    finally: M.TIMEOUT = alt
    assert "Zeitlimit" in json.dumps(r["ergebnis"], ensure_ascii=False)
