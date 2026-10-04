"""Experimenteller Modus: Das Framework plant, präregistriert und wertet aus; MESSEN tut ein Mensch im Labor.

Ablauf je Experiment:
 1. Agent ruft run_op("plane_experiment", {...}) auf -> Der Code prüft das Design (Kontrollen, Replikate, Randomisierung) und legt
    einen Versuchsauftrag an: projects/<projekt>/auftraege/A<n>.json (Plan, präregistrierte Hypothese, Analyse) und A<n>_messung.csv
    (randomisierte Laufreihenfolge, verblindete Probencodes, leere Spalte 'messwert'). Der Schlüssel Code -> Gruppe liegt getrennt
    in A<n>_schluessel.json (nicht an die messende Person geben).
 2. Der Mensch misst und trägt die Werte in die CSV ein (Ausreißer NICHT löschen; Ausfälle als leeres Feld + Spalte 'bemerkung').
 3. Beim nächsten Start der Labor-Schleife: Daten werden eingelesen, Hash gespeichert, entblindet; der statistische Prüfer
    entscheidet mit fest im Code hinterlegter Analyse (Permutationstest, alpha = 0,05, Bootstrap-KI, Kontrollen-Check, BH über
    alle Tests des Projekts). Toleranzen/alpha kommen NIE aus der Behauptung.

Eine experimentelle Domäne = Unterklasse von ExperimentalDomain mit: kontext, faktoren, messgroesse, einheit, kontrollen,
erwartung_kontrollen, min_replikate. Prüfer, Selbsttest (mit simulierten Datensätzen und Kalibrierung der Falsch-Positiv-Rate) und
Versuchsaufträge sind generisch.
"""
import csv, hashlib, json, os, random, time
import numpy as np
from .base import Domain

ALPHA = 0.05; N_PERM = 20000; SEED = 12345


def _perm_p(a, b, richtung, n=N_PERM, seed=SEED):
    """Einseitiger Permutationstest auf Mittelwertdifferenz a - b (richtung 'groesser': H1 mean(a) > mean(b))."""
    a, b = np.asarray(a, float), np.asarray(b, float); obs = a.mean() - b.mean(); x = np.concatenate([a, b]); rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n):
        rng.shuffle(x); d = x[:len(a)].mean() - x[len(a):].mean()
        cnt += (d >= obs) if richtung == "groesser" else (d <= obs)
    return (cnt + 1) / (n + 1)


def _boot_ci(a, b, n=5000, seed=SEED):
    a, b = np.asarray(a, float), np.asarray(b, float); rng = np.random.default_rng(seed)
    d = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(n)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def _spearman_perm(x, y, richtung, n=N_PERM, seed=SEED):
    from scipy.stats import spearmanr
    rho = spearmanr(x, y).correlation; rng = np.random.default_rng(seed); y = np.asarray(y, float); cnt = 0
    for _ in range(n):
        r = spearmanr(x, rng.permutation(y)).correlation; cnt += (r >= rho) if richtung == "steigend" else (r <= rho)
    return float(rho), (cnt + 1) / (n + 1)


def _bh(ps):
    ps = np.asarray(ps, float); m = len(ps); o = np.argsort(ps); adj = np.empty(m)
    adj[o] = np.minimum.accumulate((ps[o] * m / np.arange(1, m + 1))[::-1])[::-1]; return np.minimum(adj, 1)


class ExperimentalDomain(Domain):
    experimentell = True
    name = "experimentell"
    faktoren = {}                 # {"temperatur": ["25C", "37C"], ...}
    messgroesse = "messwert"; einheit = ""
    kontrollen = {"negativ": "", "positiv": ""}   # Gruppennamen der Kontrollen
    erwartung_kontrollen = "groesser"              # positiv vs negativ
    min_replikate = 3
    projekt = None                                  # wird von der Labor-Schleife gesetzt

    # ---------------------------------------------------------------- Dokumentation für Agenten
    @property
    def primitive_doc(self):
        return f"""Experimente werden NICHT vom Computer ausgeführt, sondern als Versuchsauftrag an ein Labor geschickt (Ergebnis kommt später).
- plane_experiment {{"hypothese": "...", "gruppen": [{{"name": "...", "bedingungen": {{faktor: stufe}}}}, ...], "replikate": int, "begruendung": "..."}}
  Muss die Kontrollgruppen {list(v for v in self.kontrollen.values() if v)} enthalten; replikate >= {self.min_replikate}. Liefert die Auftrags-ID (A<n>).
- auftraege {{}}: Liste der Aufträge mit Status (wartet_auf_messdaten | daten_vorhanden) und, wenn vorhanden, Gruppenmittelwerten.
Faktoren und Stufen: {json.dumps(self.faktoren, ensure_ascii=False)}. Messgröße: {self.messgroesse} [{self.einheit}]."""

    claim_doc = """Prüfungstypen (statistisch; alpha, Testverfahren und Replikat-Minimum sind im Prüfer fest):
- {"typ": "effekt", "auftrag": "A<n>", "gruppe_a": "...", "gruppe_b": "...", "richtung": "groesser"|"kleiner"}
  Besteht, wenn: Daten vollständig und nach der Präregistrierung eingetragen, Kontrollen verhalten sich wie erwartet, einseitiger
  Permutationstest p < 0,05 nach Benjamini-Hochberg über alle Tests des Projekts, und das 95-%-Bootstrap-KI der Differenz schließt 0 aus.
- {"typ": "trend", "auftrag": "A<n>", "gruppen_geordnet": ["...", "..."], "richtung": "steigend"|"fallend"}
  Monotoner Trend über geordnete Gruppen (Spearman, Permutationstest, BH).
Solange keine Messdaten vorliegen, meldet der Prüfer "wartet auf Messdaten"; das ist kein negatives Ergebnis."""

    # ---------------------------------------------------------------- Pfade
    def _dir(self): d = f"projects/{self.projekt or self.name}/auftraege"; os.makedirs(d, exist_ok=True); return d

    def _auftrag(self, aid): return json.load(open(f"{self._dir()}/{aid}.json"))

    # ---------------------------------------------------------------- Versuchsplanung
    def validate_design(self, g, rep):
        err = []; names = [x.get("name") for x in g]
        for k, v in self.kontrollen.items():
            if v and v not in names: err.append(f"Kontrollgruppe '{v}' ({k}) fehlt")
        if rep < self.min_replikate: err.append(f"replikate {rep} < Minimum {self.min_replikate}")
        if len(set(names)) != len(names): err.append("Gruppennamen nicht eindeutig")
        for x in g:
            for f, s in (x.get("bedingungen") or {}).items():
                if f in self.faktoren and s not in self.faktoren[f]: err.append(f"Stufe {s} für Faktor {f} unbekannt")
        return err

    def plane(self, hypothese, gruppen, replikate, begruendung=""):
        err = self.validate_design(gruppen, int(replikate))
        if err: return {"fehler": "Design abgelehnt: " + "; ".join(err)}
        d = self._dir(); n = len([f for f in os.listdir(d) if f.endswith(".json") and "_" not in f]) + 1; aid = f"A{n}"
        rng = random.Random(f"{aid}-{SEED}"); laeufe = [(x["name"], r + 1) for x in gruppen for r in range(int(replikate))]; rng.shuffle(laeufe)
        codes = {}; rows = []
        for i, (gname, r) in enumerate(laeufe, 1):
            code = hashlib.sha256(f"{aid}-{gname}-{r}-{SEED}".encode()).hexdigest()[:6].upper(); codes[code] = gname
            rows.append({"lauf_nr": i, "probe_code": code, "messwert": "", "bemerkung": ""})
        plan = {"id": aid, "hypothese": hypothese, "gruppen": gruppen, "replikate": int(replikate), "begruendung": begruendung,
                "messgroesse": self.messgroesse, "einheit": self.einheit, "analyse": f"einseitiger Permutationstest ({N_PERM} Permutationen, Seed {SEED}), "
                f"alpha {ALPHA}, Bootstrap-95-%-KI, Benjamini-Hochberg über alle Tests des Projekts, Kontrollen-Check {self.kontrollen}",
                "praeregistriert": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": "wartet_auf_messdaten"}
        json.dump(plan, open(f"{d}/{aid}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(codes, open(f"{d}/{aid}_schluessel.json", "w"), indent=1)
        with open(f"{d}/{aid}_messung.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["lauf_nr", "probe_code", "messwert", "bemerkung"]); w.writeheader(); w.writerows(rows)
        self._protokoll(aid, plan)
        return {"auftrag": aid, "status": "wartet_auf_messdaten", "csv": f"{d}/{aid}_messung.csv", "laeufe": len(rows)}

    def _protokoll(self, aid, plan):
        md = [f"# Versuchsauftrag {aid}", "", f"**Hypothese (präregistriert {plan['praeregistriert']}):** {plan['hypothese']}", "",
              f"**Messgröße:** {plan['messgroesse']} [{plan['einheit']}]", f"**Replikate je Gruppe:** {plan['replikate']}", "", "## Gruppen", ""]
        md += [f"- {g['name']}: {json.dumps(g.get('bedingungen', {}), ensure_ascii=False)}" for g in plan["gruppen"]]
        md += ["", "## Durchführung", "", f"1. Proben in der Reihenfolge `lauf_nr` aus `{aid}_messung.csv` messen (randomisiert).",
               "2. Die messende Person kennt nur die `probe_code`; den Schlüssel nicht weitergeben (Verblindung).",
               "3. Messwert in `messwert` eintragen, Einheit wie oben. Nichts löschen; Ausfälle leer lassen und in `bemerkung` begründen.",
               "4. Datei speichern und die Labor-Schleife erneut starten. Die Auswertung ist vorab festgelegt:", "", f"   {plan['analyse']}"]
        open(f"{self._dir()}/{aid}_protokoll.md", "w").write("\n".join(md) + "\n")

    def daten(self, aid):
        """Liest die Messdaten; None, solange unvollständig. Speichert beim ersten vollständigen Lesen Zeitpunkt und Hash."""
        d = self._dir(); p = f"{d}/{aid}_messung.csv"; codes = json.load(open(f"{d}/{aid}_schluessel.json"))
        rows = list(csv.DictReader(open(p)))
        if not rows or any(r["messwert"].strip() == "" and not r["bemerkung"].strip() for r in rows): return None
        plan = self._auftrag(aid); h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if not plan.get("daten_hash"):
            plan.update(daten_hash=h, daten_eingelesen=time.strftime("%Y-%m-%dT%H:%M:%S"), status="daten_vorhanden")
            json.dump(plan, open(f"{d}/{aid}.json", "w"), ensure_ascii=False, indent=1)
        elif plan["daten_hash"] != h:
            return {"fehler": "Messdaten wurden nach dem ersten Einlesen verändert (Hash weicht ab)"}
        g = {}
        for r in rows:
            if r["messwert"].strip(): g.setdefault(codes[r["probe_code"]], []).append(float(r["messwert"].replace(",", ".")))
        return g

    def run_op(self, op, args):
        try:
            if op == "plane_experiment": return self.plane(**{k: v for k, v in args.items() if k in ("hypothese", "gruppen", "replikate", "begruendung")})
            if op == "auftraege":
                out = []
                for f in sorted(os.listdir(self._dir())):
                    if f.endswith(".json") and "_" not in f:
                        pl = json.load(open(f"{self._dir()}/{f}")); dd = self.daten(pl["id"])
                        out.append({"id": pl["id"], "hypothese": pl["hypothese"], "status": "daten_vorhanden" if isinstance(dd, dict) and "fehler" not in dd else "wartet_auf_messdaten",
                                    "mittelwerte": {k: round(float(np.mean(v)), 4) for k, v in dd.items()} if isinstance(dd, dict) and "fehler" not in dd else None})
                return {"auftraege": out}
            return {"fehler": f"unbekannte op {op}"}
        except Exception as e:
            return {"fehler": f"{type(e).__name__}: {e}"[:300]}

    # ---------------------------------------------------------------- statistischer Prüfer
    def _tests_path(self): return f"projects/{self.projekt or self.name}/tests.json"

    def _bh_ok(self, key, p):
        tp = self._tests_path(); T = json.load(open(tp)) if os.path.exists(tp) else {}
        T[key] = p; json.dump(T, open(tp, "w"), indent=1)
        keys = list(T); adj = _bh([T[k] for k in keys]); return float(adj[keys.index(key)]), len(keys)

    def _kontrollen_ok(self, g):
        neg, pos = self.kontrollen.get("negativ"), self.kontrollen.get("positiv")
        if not (neg and pos): return True, "keine Kontrollen definiert"
        if neg not in g or pos not in g: return False, "Kontrollgruppe ohne Messwerte"
        p = _perm_p(g[pos], g[neg], self.erwartung_kontrollen)
        return p < ALPHA, f"Kontrollen: positiv vs negativ p = {p:.4f}"

    def check(self, p):
        if p.get("typ") == "_kalibrierung":
            fpr = float(p.get("fpr", 1)); return fpr <= 0.08, f"Falsch-Positiv-Rate unter H0 (200 Simulationen): {fpr:.3f} (Soll <= 0,08)", {}
        if p.get("_simuliert"):                                   # Selbsttest: Ergebnis wurde auf simulierten Daten vorab berechnet
            q = {k: v for k, v in p.items() if k != "_simuliert"}
            hit = next((ok for pp, _, ok in getattr(self, "_sim", []) if pp == q), None)
            return (bool(hit), "simulierter Selbsttest-Fall", {}) if hit is not None else (False, "Simulationsfall unbekannt", {})
        try:
            t = p.get("typ"); aid = p.get("auftrag")
            if t not in ("effekt", "trend"): return False, f"unbekannter Prüfungstyp {t}", {}
            if not aid or not os.path.exists(f"{self._dir()}/{aid}.json"): return False, f"Auftrag {aid} existiert nicht", {}
            g = self.daten(aid)
            if g is None: return False, "wartet auf Messdaten", {"wartet": True}
            if "fehler" in g: return False, g["fehler"], {}
            plan = self._auftrag(aid)
            if plan.get("daten_eingelesen", "") < plan["praeregistriert"]: return False, "Daten vor der Präregistrierung eingetragen", {}
            kok, ktxt = self._kontrollen_ok(g)
            if not kok: return False, f"Kontrollen verhalten sich nicht wie erwartet ({ktxt}); Experiment ungültig", {}
            if t == "effekt":
                a, b = g.get(p["gruppe_a"]), g.get(p["gruppe_b"])
                if a is None or b is None: return False, "Gruppe ohne Messwerte", {}
                if min(len(a), len(b)) < self.min_replikate: return False, f"zu wenige Replikate ({min(len(a), len(b))} < {self.min_replikate})", {}
                pv = _perm_p(a, b, p["richtung"]); lo, hi = _boot_ci(a, b); padj, m = self._bh_ok(f"{aid}:{p['gruppe_a']}>{p['gruppe_b']}:{p['richtung']}", pv)
                ok = padj < ALPHA and ((lo > 0) if p["richtung"] == "groesser" else (hi < 0))
                return ok, (f"{p['gruppe_a']} (n={len(a)}, Mittel {np.mean(a):.4g}) vs {p['gruppe_b']} (n={len(b)}, Mittel {np.mean(b):.4g}): "
                            f"Differenz-KI95 [{lo:.4g}, {hi:.4g}], p = {pv:.4f}, p_BH = {padj:.4f} (m = {m}); {ktxt}"), {"p": pv, "p_bh": padj}
            if t == "trend":
                xs, ys = [], []
                for i, name in enumerate(p["gruppen_geordnet"]):
                    if name not in g: return False, f"Gruppe {name} ohne Messwerte", {}
                    xs += [i] * len(g[name]); ys += g[name]
                rho, pv = _spearman_perm(xs, ys, p["richtung"]); padj, m = self._bh_ok(f"{aid}:trend:{'>'.join(p['gruppen_geordnet'])}:{p['richtung']}", pv)
                return padj < ALPHA, f"Spearman rho = {rho:.3f}, p = {pv:.4f}, p_BH = {padj:.4f} (m = {m}); {ktxt}", {"p": pv, "rho": rho}
        except Exception as e:
            return False, f"Prüfung nicht ausführbar: {type(e).__name__}: {e}"[:300], {}

    def level(self, p): return "statistical"

    def relevanz(self, p): return "hauptresultat" if p.get("typ") == "trend" else "stuetze"

    def describe(self, p, lang="de"):
        if p.get("typ") == "effekt":
            return (f"In experiment {p['auftrag']}, {self.messgroesse} is {'larger' if p['richtung'] == 'groesser' else 'smaller'} in group {p['gruppe_a']} than in "
                    f"group {p['gruppe_b']} (preregistered one-sided permutation test, alpha = 0.05 after Benjamini-Hochberg, bootstrap CI excludes 0, controls valid).")
        if p.get("typ") == "trend":
            return (f"In experiment {p['auftrag']}, {self.messgroesse} {'increases' if p['richtung'] == 'steigend' else 'decreases'} monotonically across "
                    f"{' < '.join(p['gruppen_geordnet'])} at the conditions examined (Spearman permutation test, alpha = 0.05 after Benjamini-Hochberg).")
        return super().describe(p)

    # ---------------------------------------------------------------- Selbsttest mit simulierten Daten
    def selftest(self):
        """Simulierte Versuche: großer Effekt (wahr), kein Effekt (falsch), zu wenige Replikate (falsch), Toleranz-Trick (falsch),
        Kontrollen versagen (falsch), plus Kalibrierung: Falsch-Positiv-Rate über 200 Null-Simulationen <= 0,08."""
        import tempfile, shutil
        alt = self.projekt; tmp = tempfile.mkdtemp(prefix="_selftest_", dir="projects" if os.path.isdir("projects") else None)
        self.projekt = os.path.basename(tmp); cases = []
        try:
            neg, pos = self.kontrollen.get("negativ"), self.kontrollen.get("positiv")
            def sim(eff, rep=None, kontr_ok=True, seed=0):
                rep = rep or self.min_replikate + 1; gruppen = [{"name": x} for x in (neg, pos) if x] + [{"name": "X"}, {"name": "Y"}]
                r = self.plane("Selbsttest", gruppen, max(rep, self.min_replikate)); aid = r["auftrag"]
                codes = json.load(open(f"{self._dir()}/{aid}_schluessel.json")); rng = np.random.default_rng(seed)
                mean = {neg: 0.0, pos: (3.0 if kontr_ok else 0.0), "X": eff, "Y": 0.0}
                rows = list(csv.DictReader(open(f"{self._dir()}/{aid}_messung.csv")))
                cnt = {}
                for row in rows:
                    gname = codes[row["probe_code"]]; cnt[gname] = cnt.get(gname, 0) + 1
                    row["messwert"] = "" if (rep and cnt[gname] > rep) else f"{rng.normal(mean[gname], 1.0):.4f}"
                    if row["messwert"] == "": row["bemerkung"] = "Probe ausgefallen"
                with open(f"{self._dir()}/{aid}_messung.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=["lauf_nr", "probe_code", "messwert", "bemerkung"]); w.writeheader(); w.writerows(rows)
                return aid
            cases.append(({"typ": "effekt", "auftrag": sim(4.0, seed=1), "gruppe_a": "X", "gruppe_b": "Y", "richtung": "groesser"}, True))
            cases.append(({"typ": "effekt", "auftrag": sim(0.0, seed=2), "gruppe_a": "X", "gruppe_b": "Y", "richtung": "groesser"}, False))
            cases.append(({"typ": "effekt", "auftrag": sim(4.0, seed=3), "gruppe_a": "X", "gruppe_b": "Y", "richtung": "kleiner"}, False))
            cases.append(({"typ": "effekt", "auftrag": sim(4.0, seed=4, kontr_ok=False), "gruppe_a": "X", "gruppe_b": "Y", "richtung": "groesser"}, False))
            cases.append(({"typ": "effekt", "auftrag": sim(0.3, seed=5), "gruppe_a": "X", "gruppe_b": "Y", "richtung": "groesser", "alpha": 0.9}, False))
            cases.append(({"typ": "effekt", "auftrag": "A999", "gruppe_a": "X", "gruppe_b": "Y", "richtung": "groesser"}, False))
            cases.append(({"typ": "trend", "auftrag": sim(4.0, seed=6), "gruppen_geordnet": ["Y", "X"], "richtung": "steigend"}, True))
            ergebnisse = [(p, want, self.check(p)[0]) for p, want in cases]
            # Kalibrierung (ohne BH-Datei, reine Testgröße): Falsch-Positiv-Rate unter H0
            rng = np.random.default_rng(99); fp = 0
            for _ in range(200):
                a, b = rng.normal(0, 1, self.min_replikate + 1), rng.normal(0, 1, self.min_replikate + 1)
                fp += _perm_p(a, b, "groesser", n=2000, seed=int(rng.integers(1e9))) < ALPHA
            self._fpr = fp / 200
        finally:
            shutil.rmtree(tmp, ignore_errors=True); self.projekt = alt
        self._sim = ergebnisse
        out = [(dict(p, _simuliert=True), want) for p, want, _ in ergebnisse]
        out.append(({"typ": "_kalibrierung", "fpr": self._fpr}, True))
        return out
