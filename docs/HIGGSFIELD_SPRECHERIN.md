# Script: Probatum with an AI presenter (Higgsfield, 90 s)

A presenter generated in Higgsfield explains Probatum straight to camera. Lip-synced clips of her alternate with real screen recordings. The presenter is an **AI character**, not a team member. Say so in the credits ("Presenter: AI-generated with Higgsfield"), and keep the real team for the team video.

**Numbers:** only from `results/FROZEN.json` (25 paired seeds, frozen 2026-10-04 06:47).

---

## 1 · The presenter (build her once, reuse her in every clip)

**Character prompt** (generate her as an image first with Higgsfield Soul, save her as a character / reference so she looks the same in every clip):

```
portrait of a woman in her early thirties, a calm and confident science communicator, shoulder-length dark brown hair tucked behind one ear,
light olive skin, minimal makeup, small silver stud earrings, wearing a charcoal blazer over a plain off-white t-shirt,
natural expression with a slight smile, looking directly into the camera, soft north-window daylight, shallow depth of field,
editorial photograph, 50mm, realistic skin texture
```

- **Negative prompt:** `celebrity likeness, heavy makeup, lab coat, safety goggles, glowing hologram, text, logos, extra fingers`
- **Voice:** a warm, clear English voice, calm pace (~150 words per minute), no hype. Pick a voice in Higgsfield's lip-sync/talking feature or upload your own recording. The same voice in every clip.
- **Makeup / outfit:** identical in every clip (always use the same character reference).

## 2 · Three sets (backgrounds), reused

| Set | Background prompt (combine with the character reference) |
|---|---|
| **A · Study** | `standing in a quiet study with a dark walnut desk, an open laboratory notebook and a fountain pen on the desk, tall window with soft daylight, muted off-white walls, bookshelves softly out of focus` |
| **B · Wall of tiles** | `standing in front of a gallery wall of small square paper tiles in a grid, some deep blue, some dark red, many blank off-white, soft gallery light` |
| **C · Window** | `seated on a stool by a large window, plain off-white wall, a single small deep blue square print framed behind her, late morning light` |

**Look of every clip:** 16:9, 1080p, color world paper white / graphite / one deep blue (`#23408E`), no neon, no purple gradients, nothing in her hands that looks like a screen showing data.

---

## 3 · Script

Each **presenter clip** is ≤ 10 s, because lip-sync stays clean on short clips. **Screen** means a real screen recording (see section 4).

| # | Time | Picture | What she says (English) | On-screen text |
|---|---|---|---|---|
| 1 | 0:00–0:07 | **Presenter, set A**, medium shot, camera *slow dolly in* | "AI can now write scientific claims faster than anyone can check them." | – |
| 2 | 0:07–0:14 | **Presenter, set A**, she lays her hand on the notebook | "So we built a lab where an AI is never allowed to decide what's true. Only a program is." | **∎ Probatum** |
| 3 | 0:14–0:23 | **Screen** S1: start page, a claim is rejected, the next confirmed, ∎ appears | (voiceover) "Agents propose a claim. A verifier with exact arithmetic checks it. This one fails, one rate is out of range. The next one passes." | – |
| 4 | 0:23–0:31 | **Presenter, set C**, close-up, slight *arc right* | "Seven agents work together, orchestrated by Omnigent. Policies decide what each of them may touch." | – |
| 5 | 0:31–0:38 | **Screen** S2: run page, event stream, amber DENY row | (voiceover) "Write to the lab state directly? Denied. Publish a paper? A human has to approve." | – |
| 6 | 0:38–0:46 | **Presenter, set C**, she leans forward a little | "And a red team attacks every result. We tested it: we planted two false claims." | – |
| 7 | 0:46–0:52 | **Screen** S3: `pytest tests/test_redteam.py` → 3 passed | (voiceover) "Both were brought down. The real ones survived." | "2 of 2 planted false claims refuted" |
| 8 | 0:52–1:00 | **Presenter, set B**, medium wide, *pan right* along the tile wall | "Is it faster? We preregistered a benchmark and ran it on twenty-five paired seeds." | – |
| 9 | 1:00–1:08 | **Screen** S4: results page, dot plot | (voiceover) "The lab needs about four times fewer verifier calls than a hand-written heuristic, and five times fewer than random search." | "3.96× vs heuristic (95% CI 3.34–4.80) · 5.26× vs random · 25 paired seeds" |
| 10 | 1:08–1:14 | **Presenter, set B**, she points at the wall | "On a real biophysics question it settled sixty-four of eighty-eight designs, each with a proof or an exact counterexample." | "50 proved · 14 counterexamples · 24 open" |
| 11 | 1:14–1:22 | **Screen** S5: "Re-verify" → PASS ∎, "Tamper and re-verify" → FAIL | (voiceover) "You don't have to trust us. The check runs in your browser. Change one number, and it fails." | – |
| 12 | 1:22–1:30 | **Presenter, set A**, she closes the notebook, *slow dolly out* | "Probatum. Claims you can check." | **∎ Probatum** · github.com/alizema700/Daddys-Project |

Spoken words: about 200 in total, about 95 of them by the presenter on camera.

**Optional if you have 10 s more:** before shot 12, insert a presenter clip in set C: "It also runs inside your own Claude, as an MCP server, and every run lands in Delta tables and MLflow on Databricks." Only include the Databricks half once the export has really run in the workspace.

---

## 4 · Higgsfield steps per presenter clip

1. **Image:** character reference + set prompt (section 2) + framing from the table (medium shot / close-up / medium wide), generated in Soul.
2. **Motion:** image-to-video with the camera motion from the table (Dolly In, Arc Right, Pan Right, Dolly Out). Keep it subtle; no crash zooms with a talking person.
3. **Lip-sync:** feed her line as text or audio into Higgsfield's talking/lip-sync feature. One clip per line, ≤ 10 s.
4. **Check:** watch every clip for mouth sync, hands (fingers!), eyes (no flicker) and identical clothing. Regenerate if anything is off.

Prompt add-on for every presenter clip: `same woman as reference, same charcoal blazer and off-white t-shirt, natural blinking, subtle head movement, speaking calmly to camera`.

## 5 · Screen recordings (identical to the other script)

| # | What | How |
|---|---|---|
| S1 | Start page from load to ∎ | `python -m http.server -d frontend 8000` → `http://localhost:8000`, 1920×1080, light theme |
| S2 | Run with a DENY row | `run.html?run=2026-10-04b`, "Replay run", speed "Fast", stop at the amber row |
| S3 | Red-team positive control | `pytest -q tests/test_redteam.py` in the terminal, large font |
| S4 | Acceleration | `results.html#acceleration`, scroll slowly |
| S5 | Re-verify / tamper | `run.html?run=2026-10-04b&claim=proofreading-O19#evidence`, cut out the Pyodide loading time |

## 6 · Sound and editing

- Quiet piano or string pulse around 80 BPM, under her voice at −18 dB.
- A soft "stamp" sound when ∎ appears (shots 2, 3, 11, 12).
- Hard cuts between her and the screen; burn in the subtitles.
- Credits: "Presenter: AI-generated (Higgsfield). All numbers: results/FROZEN.json. All screen recordings are real."

## 7 · Before upload

- [ ] Every number matches `results/FROZEN.json` exactly.
- [ ] She never says "10× faster" or "proves everything": say "about four times fewer verifier calls than a hand-written heuristic".
- [ ] No presenter clip shows data, charts or a UI; those are only in the screen recordings.
- [ ] Credits name the AI presenter.
- [ ] Databricks is only mentioned if the export really ran in the workspace.
