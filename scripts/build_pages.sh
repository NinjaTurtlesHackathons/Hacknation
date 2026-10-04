#!/usr/bin/env bash
# Statische Seite für GitHub Pages: Probatum Lab (frontend/) als Startseite, dazu web/tour.html und die versiegelten Laufprotokolle.
#   scripts/build_pages.sh [--push]     -> _site/ ; mit --push auf den Branch gh-pages
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel); S="$ROOT/_site"; rm -rf "$S"; mkdir -p "$S/web"
cp "$ROOT/web/tour.html" "$S/web/"
for r in "$ROOT"/runs/omnigent/*/; do
  rel=${r#"$ROOT/"}; mkdir -p "$S/$rel"
  for f in record.jsonl state.json decisions.md prereg.md HIGHLIGHTS.md README.md trace.json beats.json CHAIN.json origin.json; do
    [[ -f "$r/$f" ]] && cp "$r/$f" "$S/$rel/"; done
done
python "$ROOT/frontend/build_data.py"                                   # Probatum Lab (frontend/) ist die Startseite
cp "$ROOT"/frontend/*.html "$S/"; cp -r "$ROOT/frontend/assets" "$ROOT/frontend/data" "$S/"
touch "$S/.nojekyll"; echo "built $S"
if [[ "${1:-}" == "--push" ]]; then
  W=$(mktemp -d); git -C "$ROOT" worktree add -q --detach "$W"; cd "$W"
  git checkout -q --orphan gh-pages; git rm -rq --cached . >/dev/null 2>&1 || true; find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  cp -r "$S"/. .; git add -A; git commit -qm "Replay-Seite (generiert von scripts/build_pages.sh)"; git push -q -f origin gh-pages
  cd "$ROOT"; git worktree remove --force "$W"; echo "pushed gh-pages"
fi
