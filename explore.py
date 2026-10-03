"""Entdeckungsmodus: dieselbe Forscher-Schleife wie im Benchmark, aber auf Fragen, die Suleman 2026 offenlässt.
Hier dürfen die Agenten den Stand der Forschung kennen (Literatur-Kontext); geprüft wird wie immer per Code.
  python explore.py [E1,E3,...]  ->  results/explore/<id>.json
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from asd.discovery import solve

STAND = ("Stand der Forschung (Suleman 2026, Preprint): In 2D ist das hexagonale Gitter numerisch optimal für 2,2 <= nu < nu* = 3,9184, "
         "das quadratische für nu* < nu <= nu_2 = 8,606, danach rechteckig. Unter nu = 2 wurden nur vier Kandidaten (hexagonal, quadratisch, "
         "rechteckig y = 1,1, rhombisch 75°) bei nu = 1,4 ... 1,9 verglichen; zwischen 1,9 und 2,2 gab es keine globale Suche. "
         "In 3D ist BCC das beste Gitter einer globalen Suche für 3,2 <= nu <= 12; darunter wurden nur BCC, FCC und SC verglichen (2,2 <= nu <= 2,8). "
         "In 4D wurde nur der Grenzfall nu -> unendlich untersucht: D4 maximiert dort das kleinste Dreiecksprodukt (numerisch), ist für große nu "
         "ein strikt lokales Minimum, und Vermutung 2 lautet, dass D4 für alle großen nu global optimal ist. Für endliche nu in 4D ist nichts bekannt.")
KONTEXT = ("Betrachtet wird die Dreikörper-Energie T_nu(L) = Summe über alle Paare verschiedener Gittervektoren x != y, beide ungleich 0, "
           "von (|x| |y| |x-y|)^(-nu), für Bravais-Gitter L mit Kovolumen 1. In 2D: tau = x + i y im Fundamentalbereich. " + STAND)
FRAGEN = {
    "E1": "Welches 2D-Gitter minimiert T_nu bei nu = 2,0 global (Lücke der bisherigen Suche zwischen 1,9 und 2,2)?",
    "E2": "Welches 2D-Gitter minimiert T_nu bei nu = 1,6 global? Bisher wurden dort nur vier Kandidaten verglichen.",
    "E3": "Ist BCC auch bei nu = 3,0 das global optimale 3D-Bravais-Gitter (unterhalb des bisher global durchsuchten Bereichs)?",
    "E4": "Welches 4D-Bravais-Gitter minimiert T_nu bei nu = 5 global? Ist es D4, wie es Vermutung 2 für große nu nahelegt?",
    "E5": "Welches 4D-Bravais-Gitter minimiert T_nu bei nu = 8 global?",
    "E6": "Welches der Gitter Z4, D4, A4, A4* hat bei nu = 3,5 die niedrigste Energie T_nu (nahe der Konvergenzgrenze nu > 8/3 in 4D)?",
}

if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else list(FRAGEN)
    os.makedirs("results/explore", exist_ok=True)
    def run(i):
        path = f"results/explore/{i}.json"
        if os.path.exists(path): return
        r = solve(KONTEXT, FRAGEN[i], salt=f"explore-{i}"); r.update(id=i, frage=FRAGEN[i])
        json.dump(r, open(path, "w"), ensure_ascii=False, indent=1, default=str)
        print(i, r["level"], json.dumps(r["antwort"], ensure_ascii=False)[:300], flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(run, ids))
