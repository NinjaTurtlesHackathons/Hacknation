# Script: Probatum, 90-second video (Higgsfield + screen recordings)

**Idea in one sentence:** AI agents propose, only a program says "proved", and anyone can check that again in their own browser.

**Rule for the edit:** Higgsfield supplies only *atmosphere*: the notebook, light, the ∎ stamp, the gate. Everything that shows data, numbers or the UI is a **real screen recording** of our page or terminal. Never let a generated image show results, tables or a fake UI; the jury would rightly see that as a contradiction to "every claim is checked".

**Numbers:** all come from `results/FROZEN.json` (frozen 2026-10-04 06:47, 25 paired seeds). Don't round them or change them in the edit.

---

## Look and settings (same for every Higgsfield clip)

- **Format:** 16:9, 1080p, 5 s per clip (cut down to 3–4 s in the edit), 24 fps
- **Color world:** off-white paper `#F6F7F5`, dark ink `#1C2430`, one accent, proof blue `#23408E`. No purple/neon gradients, no glow.
- **Style suffix** (append to every prompt):
  `editorial still life, soft north-window daylight, shallow depth of field, matte paper texture, muted palette of off-white, graphite and one deep blue accent, no text, no logos, no people's faces, calm, precise, 35mm photograph`
- **Workflow:** first generate the start frame as an image (Higgsfield image model, e.g. Soul), then image-to-video with a camera motion. Motion names follow the Higgsfield presets; if a preset is named differently, use the closest one.
- **Negative prompt:** `text, letters, numbers, UI, screens with data, logos, hands with extra fingers, glowing particles, purple gradient, sci-fi hologram`

---

## Shot list

| # | Time | Picture | Source | Voiceover (English, calm, ~150 words/min) | On-screen text |
|---|---|---|---|---|---|
| 1 | 0:00–0:05 | Open lab notebook on a dark desk, a fountain pen beside it, morning light falls across the page | **Higgsfield** H1 | "Every lab notebook is full of claims." | – |
| 2 | 0:05–0:10 | Pages flip by themselves, ink lines run in, many handwritten-looking strokes (illegible) | **Higgsfield** H2 | "AI can now write them faster than anyone can check them." | – |
| 3 | 0:10–0:15 | Close-up: a single blue square printed onto paper, like a stamp | **Higgsfield** H3 | "We built a lab where only a program is allowed to say: proved." | **∎ Probatum** |
| 4 | 0:15–0:24 | Start page of our site, the live excerpt plays: a claim is rejected with a reason, the next is confirmed, ∎ appears | **Screen recording** S1 (`index.html`) | "Agents propose. A verifier with exact arithmetic decides. Here a claim fails on one rate out of range; the next one passes." | – |
| 5 | 0:24–0:29 | Seven identical brass gears on a white surface turning in sync, top-down | **Higgsfield** H4 | "Seven agents, orchestrated by Omnigent: scout, planner, researchers, red team, learner, scribe." | – |
| 6 | 0:29–0:37 | Run page, event stream with agent lanes; a policy DENY appears in amber | **Screen recording** S2 (`run.html?run=2026-10-04b`) | "Policies decide what each agent may touch. Write to the lab state directly? Denied. Publish? A human approves." | – |
| 7 | 0:37–0:42 | A heavy iron gate in a pale stone wall swings closed, slow | **Higgsfield** H5 | "And a red team attacks every result." | – |
| 8 | 0:42–0:50 | Terminal: `pytest tests/test_redteam.py`, 3 passed; then `redteam --auto` output with `"status": "angefochten"` for the planted false claim | **Screen recording** S3 | "We planted two false claims. The red team brought both down. The real ones survived." | "2 of 2 planted false claims refuted" |
| 9 | 0:50–1:00 | Results page, dot plot: lab vs heuristic vs random, 25 seeds | **Screen recording** S4 (`results.html#acceleration`) | "Is it faster? On a preregistered benchmark with twenty-five paired seeds, the lab needs about four times fewer verifier calls than a hand-written heuristic, and five times fewer than random search." | "3.96× vs heuristic (95% CI 3.34–4.80) · 5.26× vs random · 25 paired seeds" |
| 10 | 1:00–1:05 | Light sweeps across a wall of 88 small paper tiles, some blue, some dark red, some empty | **Higgsfield** H6 | "On a real question in biophysics it decided sixty-four of eighty-eight molecular proofreading designs: fifty proved, fourteen broken with an exact counterexample." | "50 proved · 14 counterexamples · 24 open" |
| 11 | 1:05–1:15 | Run page, certificate block: click "Re-verify" → PASS and ∎; then "Tamper and re-verify" → FAIL. Then hash chain "Tamper" → "Broken at link 20" | **Screen recording** S5 | "And you don't have to trust us. The certificate runs in your browser. Change one number by a tenth of a percent, and it fails. Change one log line, and the hash chain breaks." | – |
| 12 | 1:15–1:20 | Terminal: `claude mcp add probatum …`, then a question in your own Claude, answer with verdict | **Screen recording** S6 | "The same verifier runs as an MCP server in your own Claude." | `uvx --from git+https://github.com/alizema700/Daddys-Project probatum-mcp` |
| 13 | 1:20–1:25 | Databricks: the `experiments` table and the MLflow runs (once exported) | **Screen recording** S7 | "Every run lands in Delta tables and MLflow on Databricks." | – |
| 14 | 1:25–1:30 | The notebook from shot 1 closes slowly, the blue ∎ remains visible on the cover | **Higgsfield** H7 | "Probatum. Claims you can check." | **∎ Probatum** · github.com/alizema700/Daddys-Project |

Total: 90 s, about 205 spoken words.

---

## Higgsfield prompts (copy them as they are)

**H1, notebook, establishing shot**
- Start frame: `an open blank laboratory notebook on a dark walnut desk, a black fountain pen beside it, morning light raking across the paper` + style suffix
- Motion: **Dolly In** (slow), 5 s
- Video prompt: `slow push-in toward the open notebook, dust motes drift in the window light, the paper is perfectly still`

**H2, pages fill up**
- Start frame: the same notebook, pages slightly raised, illegible fine ink strokes on the pages + style suffix
- Motion: **Static** or **Crane Down** (minimal), 5 s
- Video prompt: `pages turn on their own one after another, faint illegible ink lines appear and fill each page quickly, a sense of too much writing too fast`

**H3, the stamp**
- Start frame: `macro shot of matte off-white paper fibers, a small solid deep blue square printed in the center like a fresh ink stamp` + style suffix
- Motion: **Crash Zoom In** (short) or **Dolly In**, 5 s
- Video prompt: `a solid deep blue square presses into the paper like a stamp, ink settles into the fibers, then everything is still`

**H4, seven agents**
- Start frame: `seven identical small brass gears arranged in a loose row on white paper, top-down view, soft shadows` + style suffix
- Motion: **Overhead** / **Top Down**, slight rotation, 5 s
- Video prompt: `the seven gears begin turning in sync, precise and quiet, the camera slowly rotates above them`

**H5, the gate**
- Start frame: `a heavy dark iron gate set in a pale limestone wall, overcast daylight, minimal composition` + style suffix
- Motion: **Arc Left** (slow), 5 s
- Video prompt: `the iron gate swings slowly shut and locks, a small cloud of stone dust, camera arcs gently to the left`

**H6, 88 tiles**
- Start frame: `a wall of 88 small square paper tiles in an 8 by 11 grid, about half of them deep blue, some dark red, the rest blank off-white, gallery lighting` + style suffix
- Motion: **Pan Right** (slow) with a passing light sweep, 5 s
- Video prompt: `a soft beam of light sweeps across the grid of tiles from left to right, the camera pans slowly with it`
- Note: the count and colors of the tiles are only a symbol. In the edit the real numbers (50/14/24) come in as text.

**H7, the closed notebook**
- Start frame: `a closed laboratory notebook with a plain grey cover on the dark walnut desk, one small solid deep blue square printed on the cover` + style suffix
- Motion: **Dolly Out** (slow), 5 s
- Video prompt: `the camera pulls back slowly from the closed notebook, the light dims slightly, calm ending`

---

## Screen recordings (record them before the edit)

| # | What | How |
|---|---|---|
| S1 | Start page, live excerpt from load to ∎ | `python -m http.server -d frontend 8000`, open `http://localhost:8000`, 1920×1080, light theme, browser in full screen |
| S2 | Run page mid-run with an amber DENY row | `run.html?run=2026-10-04b`, "Replay run", speed "Fast", stop around event 60 |
| S3 | Red-team positive control | `pytest -q tests/test_redteam.py`, then for the effect `python -m asd.cli redteam --domain proofreading --projekt _redteam_test --claim FALSCH-B --auto` (the test fixture creates the project; for the recording, comment out `shutil.rmtree` at the end of the fixture or copy it beforehand) |
| S4 | Results page, acceleration chart | `results.html#acceleration`, scroll slowly, mouse on the H8b row |
| S5 | Re-verify / tamper | `run.html?run=2026-10-04b&claim=proofreading-O19#evidence`: click "Re-verify" (Pyodide loads once, about 10 s, cut that out), then "Tamper and re-verify", then the "Tamper and re-verify" button under "Hash chain" |
| S6 | MCP in your own Claude | `claude mcp add --scope user probatum -- uvx --from git+https://github.com/alizema700/Daddys-Project probatum-mcp`, then ask in Claude: "Check with probatum: does fam2_9 reach eta ≤ 1e-4?" |
| S7 | Databricks | only after `python -m asd.databricks_export --catalog main --schema probatum` against the workspace; otherwise drop the shot and shorten shot 12 to 10 s |

---

## Sound and editing

- **Music:** quiet piano or a minimal string pulse, around 80 BPM, no drop. Slightly louder from shot 9 on, out in shot 14.
- **Sound design:**
  - a soft "stamp" thud each time ∎ appears (shots 3, 4, 11, 14);
  - a dull metallic clack when the gate closes (shot 7);
  - a short, low tone (not an alarm sound) at FAIL in shot 11.
- **Cuts:** hard cuts between Higgsfield and screen, no transitions. Show screen recordings at 100 % zoom or zoomed into the relevant area (2–3 s Ken Burns at most).
- **Subtitles:** burn in the voiceover text (many juries watch without sound).
- **Fonts for on-screen text:** Instrument Sans 600, ink color on paper or white on ink; numbers with tabular figures.

## Honesty check before upload (every point must hold)

- [ ] Every number in the video is exactly the one in `results/FROZEN.json` (H8b 3.96×, CI 3.34–4.80; H8a 5.26×; 25 seeds; 50/14/24).
- [ ] No Higgsfield clip shows numbers, tables or a UI.
- [ ] "about four times / five times fewer" is said alongside "preregistered benchmark" and "hand-written heuristic" or "random search". Never "10× faster science".
- [ ] Speak or show H8c (no significant effect vs the same agents without feedback) if there is time. If not, it must be in the technical video.
- [ ] Shot 13 is only included if the Databricks export really ran in the workspace.
