#!/usr/bin/env bash
# Statische Replay-Seite für GitHub Pages: web/tour.html + die versiegelten Laufprotokolle (ohne Session-Rohdaten).
#   scripts/build_pages.sh [--push]     -> _site/ ; mit --push auf den Branch gh-pages
set -euo pipefail
ROOT=$(git rev-parse --show-toplevel); S="$ROOT/_site"; rm -rf "$S"; mkdir -p "$S/web"
cp "$ROOT/web/tour.html" "$S/web/"
for r in "$ROOT"/runs/omnigent/*/; do
  rel=${r#"$ROOT/"}; mkdir -p "$S/$rel"
  for f in record.jsonl state.json decisions.md prereg.md HIGHLIGHTS.md README.md trace.json beats.json CHAIN.json origin.json; do
    [[ -f "$r/$f" ]] && cp "$r/$f" "$S/$rel/"; done
done
cat > "$S/index.html" <<'HTML'
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Verifier-gated lab</title><meta http-equiv="refresh" content="0; url=web/tour.html"></head>
<body><p><a href="web/tour.html">Guided tour of the recorded Omnigent run</a></p></body></html>
HTML
touch "$S/.nojekyll"; echo "built $S"
if [[ "${1:-}" == "--push" ]]; then
  W=$(mktemp -d); git -C "$ROOT" worktree add -q --detach "$W"; cd "$W"
  git checkout -q --orphan gh-pages; git rm -rq --cached . >/dev/null 2>&1 || true; find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  cp -r "$S"/. .; git add -A; git commit -qm "Replay-Seite (generiert von scripts/build_pages.sh)"; git push -q -f origin gh-pages
  cd "$ROOT"; git worktree remove --force "$W"; echo "pushed gh-pages"
fi
