#!/usr/bin/env bash
# Renders the Higgsfield clips with your API key. Usage: bash scripts/video.sh        (all 15 shots)
#                                                    bash scripts/video.sh 09     (only shot 09)
set -e
cd "$(dirname "$0")/.."
git pull -q 2>/dev/null || true
python3 -m pip install -q --disable-pip-version-check higgsfield-client
if [ -z "$HF_KEY" ]; then
  read -rsp "Paste your Higgsfield key (KEY-ID:SECRET) and press Enter: " HF_KEY; echo; export HF_KEY
fi
python3 scripts/higgsfield_render.py --run ${1:+--only $1}
open video/clips 2>/dev/null || xdg-open video/clips 2>/dev/null || echo "Clips are in: $(pwd)/video/clips"
