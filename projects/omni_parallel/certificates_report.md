# Certificates report (omni_parallel)

| Claim | Type | Export | check.py (fresh process, `python -I`) |
|---|---|---|---|
| proofreading-R1 | erreichbar | nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb) | – |
| proofreading-R2 | erreichbar | nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb) | – |
| proofreading-R3 | erreichbar | exportiert | PASS |
| proofreading-R4 | erreichbar | exportiert | PASS |
| proofreading-R6 | schranke_familie | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |
| proofreading-R7 | schranke_familie | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |
| proofreading-R8 | erreichbar | nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb) | – |
| proofreading-R9 | untere_schranke | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |
| proofreading-R10 | erreichbar | nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb) | – |
| proofreading-R11 | schranke_familie | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |
| proofreading-R12 | erreichbar_liste | exportiert | PASS |
| proofreading-O14 | erreichbar_liste | exportiert | PASS |
| proofreading-O15 | schranke_familie | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |
| proofreading-O16 | erreichbar | nicht eigenständig (sigma-Schranke braucht rigorose Logarithmen/arb) | – |
| proofreading-O19 | erreichbar_liste | exportiert | PASS |
| proofreading-O20 | erreichbar_liste | exportiert | PASS |
| proofreading-O21 | schranke_familie | nicht eigenständig (symbolischer Beweis, braucht Computeralgebra; reproduzierbar mit python -m asd.recheck) | – |

Tamper test (one rate of proofreading-R3 multiplied by 1.001): **FAIL: hopfield_n1: W rates of bind do not follow from the R branch**

Exported 6, PASS 6, not standalone 11.
