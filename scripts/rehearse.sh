#!/usr/bin/env bash
# Sauberer Probelauf: frischer Klon, frische venv laut README, Selbsttest, Ein-Minuten-Replay (nur LLM-Cache, keine Kosten),
# asd.metrics, asd.rubric, asd.freeze + asd.submission; zweimal; Ausgaben müssen identisch sein. Bericht: rehearsal_report.md
#   scripts/rehearse.sh [repo-pfad-oder-url] [ref]
set -uo pipefail
SRC=${1:-$(git rev-parse --show-toplevel)}; REF=${2:-$(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo HEAD)}
HERE=$(pwd); REPORT="$HERE/rehearsal_report.md"; UV=$(command -v uv || echo "$HOME/.local/bin/uv")
declare -A H
echo "# Rehearsal report" > "$REPORT"; echo "" >> "$REPORT"; echo "Source: \`$SRC\` @ \`$REF\` · $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$REPORT"; echo "" >> "$REPORT"
ALLES_OK=1
for LAUF in 1 2; do
  T=$(mktemp -d); echo "## Run $LAUF ($T)" >> "$REPORT"; echo "" >> "$REPORT"
  git clone -q "$SRC" "$T/repo" && cd "$T/repo" && git checkout -q "$REF" || { echo "- clone FAILED" >> "$REPORT"; ALLES_OK=0; continue; }
  "$UV" venv -q -p python3.11 .venv >/dev/null 2>&1 && "$UV" pip install -q -p .venv/bin/python -e ".[lab,test]" >/dev/null 2>&1
  PY=.venv/bin/python
  schritt () { local name=$1; shift; local t0=$(date +%s); if "$@" > "out_$name.txt" 2>&1; then r=PASS; else r="FAIL (exit $?)"; fi
               echo "- $name: $r ($(( $(date +%s) - t0 )) s)" >> "$REPORT"; [[ $r == PASS ]] || { [[ $name == rubric ]] || ALLES_OK=0; }; }
  schritt install test -x "$PY"
  schritt selftest "$PY" -m asd.selftest proofreading
  schritt replay env ASD_LLM=replay "$PY" -m benchmarks.replay_lattice --einzel LAB 1000
  schritt metrics "$PY" -m asd.metrics proofreading --run runs/omnigent/2026-10-04
  schritt rubric "$PY" -m asd.rubric
  schritt freeze "$PY" -m asd.freeze
  schritt submission "$PY" -m asd.submission
  # Vergleichsgrößen (zeit-/pfadabhängige Felder entfernt)
  H[$LAUF]=$( { "$PY" - <<'PY'
import json
r = json.load(open("results/replay_lattice/LAB_1000.json")); r.pop("sek", None); print(json.dumps(r, sort_keys=True))
print(json.dumps(json.load(open("results/metrics_proofreading.json")), sort_keys=True, default=str))
f = json.load(open("results/FROZEN.json")); [f.pop(k, None) for k in ("zeitpunkt",)]; print(json.dumps(f, sort_keys=True, default=str))
PY
              cat out_rubric.txt submission/summary.md; } | sha256sum | cut -c1-16)
  echo "- fingerprint (replay result, metrics, FROZEN without timestamp, rubric table, summary): \`${H[$LAUF]}\`" >> "$REPORT"
  grep -E "^\| .* \| ✗ \|" out_rubric.txt | sed 's/^/  - open: /' >> "$REPORT"; echo "" >> "$REPORT"
  cd "$HERE"; rm -rf "$T"
done
if [[ "${H[1]:-x}" == "${H[2]:-y}" && $ALLES_OK == 1 ]]; then echo "**Result: two identical green runs → ready to submit.**" >> "$REPORT"; ok=0
else echo "**Result: NOT ready (outputs differ or a step failed).**" >> "$REPORT"; ok=1; fi
cat "$REPORT"; exit $ok
