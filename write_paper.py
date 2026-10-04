"""Schreibt paper/paper.md aus der Tabelle claims mit dem Halluzinations-Gate (asd/writer.py).
Am Ende ein Prüfprotokoll: wie viele Sätze, wie viele Belege, was entfernt wurde."""
import json, os, re
from asd import tables as T
from asd.writer import write, check

TITLE = "Ein KI-Labor mit Prüfschicht: Nachentdeckung eines neuen Preprints, offene Fragen und ehrliche Benchmarks"
OUTLINE = """1. Zusammenfassung (5-7 Sätze): Ziel, Methode (Forscher-Agenten + Code-Prüfer + Präregistrierung), Hauptbefunde mit Zahlen.
2. Methode: Lab als einziger Zugang zur Wahrheit; Gitter-Labor und seine Validierung gegen Suleman 2026; Code-Prüfer statt LLM-Urteil; Präregistrierung; Negativkontrollen.
3. Ergebnis 1, Benchmark-Nachentdeckung (H3): Trefferquote und Fehlerquote der drei Bedingungen, Tests.
4. Ergebnis 2, offene Fragen (Entdeckungsmodus): jede geprüfte Antwort einzeln; ausdrücklich als numerischer Befund (Level observed), nicht als Beweis.
5. Ergebnis 3, Buchwald-Hartwig-Validierung: Bayes'sche Optimierung vs. Zufall, H1 (KI-Vorwissen) nicht belegt, Negativkontrolle, Lean-Lemma.
6. Grenzen und offene Punkte: was nicht belegt ist (Claims mit Status offen/widerlegt) offen benennen.
Nutze nur Claims aus der Liste. Kurze Absätze."""

if __name__ == "__main__":
    C = T.read("claims").fillna("").to_dict("records")
    C = [c for c in C if not c["claim_id"].startswith("C-hyp-")] + [c for c in C if c["claim_id"].startswith("C-hyp-") and c["status"] == "bestätigt"][:6]
    md, log = write(TITLE, OUTLINE, C, salt="paper-v1")
    sents = [s for s in re.split(r"(?<=[.!?])\s+", md) if s.strip()]
    cited = len(set(re.findall(r"C-[\w\-*.]+", md)))
    proto = (f"\n\n---\n**Prüfprotokoll (automatisch):** {len(sents)} Sätze, {cited} verschiedene Claims zitiert, "
             f"Korrekturrunden: {json.dumps(log['runden'], ensure_ascii=False)}, entfernte unbelegte Sätze: {len(log['entfernt'])}. "
             f"Verbleibende Verstöße laut Prüfer: {len(check(md, C))}.\n")
    os.makedirs("paper", exist_ok=True); open("paper/paper.md", "w").write(f"# {TITLE}\n\n" + md + proto)
    json.dump(log, open("paper/paper_pruefprotokoll.json", "w"), ensure_ascii=False, indent=1)
    print(proto)
