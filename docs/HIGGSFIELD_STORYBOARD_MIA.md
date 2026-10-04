# Storyboard "Mia": Higgsfield production script (60 s)

Based on the team storyboard (despair → bottleneck → first contact → the lab at work → others use it → breakthrough → graduation → logo).
Each scene comes as **Higgsfield clips** (start frame + camera motion + video prompt) plus **overlays**, which are added in the edit.

## Three rules that save the video

1. **No text from Higgsfield.** AI video garbles letters. Chat bubbles, "Rejected", ✓, number cards, the paper title and the logo are all **overlays in the edit** (CapCut, Premiere, After Effects). In the prompts: `no text, no letters, blank screen`.
2. **Real numbers only, from `results/FROZEN.json`** (see the cards in scene 5). Mia, the professor and the PhD student are fictional characters. Don't imply that real users exist.
3. **The same characters in every clip:** generate each person once as an image in Higgsfield Soul and save them as a character reference.

## Wording that matches the project exactly

| In the storyboard | Correct for the project | Why |
|---|---|---|
| "Two independent checkers decide." | **"Agents propose. A verifier decides, and a red team attacks every result."** (German: „Agenten schlagen vor. Ein Prüfprogramm entscheidet, ein Red Team greift jedes Ergebnis an.") | A verifier decides; the red team attacks. "Two checkers" would be wrong. |
| "✓✓ proved" | **"✓ certified"** or "∎ verified" | Most claims are exact certificates or symbolic proofs, not Lean proofs. "Certified" holds every time. |
| "0 false claims accepted" | **"0 of 20 random claims accepted"** and **"2 of 2 planted false claims caught"** | Only with the reference size is the number true and checkable. |
| Paper with "Theorem" | Paper with **"Result 1 … ∎"** and a claim ID underneath | The paper writes only verified claims; each carries an ID. |

---

## Characters (create once in Soul)

**Mia** (main character):
```
young woman, about 24, master's student, warm brown skin, curly dark hair in a loose bun, round thin-framed glasses,
oversized dark green knit sweater, tired but determined eyes, natural look, cinematic photograph, 35mm
```
**Professor:** `woman in her late fifties, short silver hair, dark navy blazer, reading glasses on a chain, kind but sharp expression, cinematic photograph`
**PhD student:** `man about 28, short black hair, light stubble, grey hoodie, laptop under his arm, cinematic photograph`
**Lab head:** `man in his forties, rolled-up shirt sleeves, lab badge on a lanyard, standing in a bright lab corridor, cinematic photograph`

**Style suffix (every clip):** `cinematic, 35mm film look, soft natural light, muted palette with one deep blue accent (#23408E), shallow depth of field, no text, no letters, no logos`
**Negative prompt:** `text, letters, numbers, watermark, logo, garbled screen text, extra fingers, distorted hands, neon, purple gradient`

---

## Scenes and clips (60 s, 17 clips)

Higgsfield always generates 5 s; cut each clip down to the time given in the edit.

| # | Time | Clip (Higgsfield) | Camera motion | Overlay in the edit | Voiceover / sound |
|---|---|---|---|---|---|
| **1 Despair** | | | | | |
| 1a | 0–3 s | **Mia** at night in a library, laptop with a red glow, coffee cup, stack of papers, desk lamp | Dolly In | – | Rain, a clock ticking |
| 1b | 3–6 s | Close-up: Mia takes off her glasses and rubs her eyes | Static | Red error lines (blurred, illegible) | **"Months of work. And none of it holds up."** |
| **2 The bottleneck** | | | | | |
| 2a | 6–7.5 s | **PhD student** in a corridor, shaking his head at his laptop | Whip Pan | – | – |
| 2b | 7.5–9 s | **Professor**, red pen over a manuscript, frowning | Whip Pan | – | – |
| 2c | 9–10 s | **Lab head** holds a sheet up to the light, sceptical | Crash Zoom In | – | **"Research doesn't fail for lack of ideas. It fails at checking."** (runs over 2a–2c) |
| **3 First contact** | | | | | |
| 3a | 10–13 s | Mia in morning light, sitting up straight and typing; screen blank | Arc Right | **Overlay:** her question as a chat bubble | – |
| 3b | 13–16 s | Over the shoulder, she leans in | Dolly In | **Overlay:** ∎ blinks, "Ask your question." | **"Ask your question."** |
| **4 The lab at work** | | | | | |
| 4a | 16–20 s | **Motion design:** bubbles Scout, Planner, 2× Researcher, Red team; arrows, two parallel lanes | – | – | **"Agents propose."** |
| 4b | 20–25 s | **Motion design:** claim card struck through in red, "Rejected: one rate out of range" | – | Strike-through 300 ms, a dull "thunk" | **"A verifier decides …"** |
| 4c | 25–30 s | **Motion design:** next card gets the blue ∎ "certified", the red-team shield bounces off it | – | Stamp 280 ms, a warm "thud" | **"… and a red team attacks every result."** |
| **5 Others use it** | | | | | |
| 5a | 30–32.5 s | **Professor** nods while reading | Dolly In | **Card:** "0 of 20 random claims accepted" | Music picks up |
| 5b | 32.5–35 s | **PhD student** looks surprised at his laptop | Static | **Card:** "Result changed the plan" | – |
| 5c | 35–38 s | Blurred library background | – | **Card:** "3.96× fewer verifier calls than a hand-written heuristic · 25 seeds" | – |
| **6 Breakthrough** | | | | | |
| 6a | 38–42 s | Mia laughs with relief, the **professor** behind her nods (both in one clip) | Dolly Out | – | – |
| 6b | 42–46 s | Printed pages on the table (blank) | Crane Down | **Overlay:** "Result 1 … ∎", "claim proofreading-O19" | **"Proved, not claimed."** |
| **7 Graduation** | | | | | |
| 7a | 46–50 s | Graduation, caps thrown, golden hour | Bullet Time / slow motion | – | Music swells |
| 7b | 50–53 s | Low angle, caps against a blue sky | Crane Up, slow motion | – | – |
| **8 Logo** | | | | | |
| 8a | 53–56 s | A cap flies into the lens and fills the frame | FPV / Follow | **Morph:** the cap becomes the blue square | – |
| 8b | 56–60 s | Paper white | – | **∎ Probatum**, "Proved, not claimed.", github.com/alizema700/Daddys-Project | Music ends on one note |

**Voiceover:** about 30 words, enough for 60 s with breathing room. If you want German instead:
- Szene 1: „Monate Arbeit. Und nichts davon hält."
- Szene 2: „Forschung scheitert nicht an Ideen, sondern am Prüfen."
- Szene 3: „Stell deine Frage."
- Szene 4: „Agenten schlagen vor. Ein Prüfprogramm entscheidet, ein Red Team greift jedes Ergebnis an."
- Szene 6: „Bewiesen statt behauptet."

## Higgsfield prompts ready to copy (the most important clips)

**1a** — `[Mia reference] sitting alone at a long wooden library table at night, laptop open with a red glow on her face, paper coffee cup, tall stack of printed papers, single warm desk lamp, dark bookshelves behind, rain on the tall window` + style suffix · Motion: **Dolly In** · Video: `slow push in, she stares at the screen, exhales, rain streaks on the window`

**2c** — `[lab head reference] in a bright modern lab corridor holding a sheet of paper up to the light, sceptical frown` + style suffix · Motion: **Crash Zoom In** · Video: `quick zoom onto his face as he lowers the paper and shakes his head`

**3a** — `[Mia reference] at the same library table in early morning light, sitting up straight and typing, laptop screen plain off-white and blank` + style suffix · Motion: **Arc Right** · Video: `camera arcs slowly around her, she types with focus, morning light grows`

**6a** — `[Mia reference] laughing with relief, leaning back in her chair, [professor reference] standing behind her nodding with approval, sunlight flooding the library` + style suffix · Motion: **Dolly Out** · Video: `she laughs and covers her mouth, camera pulls back slowly`

**7a** — `[Mia reference] with friends in graduation gowns on a sunny lawn, all throwing their caps into the air, golden hour` + style suffix · Motion: **Bullet Time** or slow motion · Video: `caps leave their hands in slow motion, gowns flutter, everyone laughing`

**8a** — `a single black graduation cap spinning toward the camera against a deep blue sky` + style suffix · Motion: **FPV Drone / Follow** · Video: `the cap flies straight into the lens until it fills the frame`

---

## Motion-design notes (scene 4, overlays)

- **Fonts:** Instrument Sans 600 for labels, numbers with tabular figures. No ALL-CAPS labels.
- **Colors:** paper `#F6F7F5`, ink `#1C2430`, accent `#23408E`; red `#9B2C2C` only for "rejected", green `#1E6B47` only if you want ✓ in addition to ∎.
- **Timing:** bubbles pop in staggered (80 ms apart). Arrows draw in (300 ms). Strike-through 300 ms. ∎ stamp 280 ms with a slight overshoot.
- **Sound:** soft pop per bubble, dull "thunk" at the strike-through, warm "thud" at ∎.

## Number cards (copy them as they are; source `results/FROZEN.json`)

- "0 of 20 random claims accepted"
- "2 of 2 planted false claims caught by the red team"
- "3.96× fewer verifier calls than a hand-written heuristic · 25 paired seeds"
- Reserve cards (if you want to swap one): "2 of 2 planted false claims caught by the red team" · "5.26× fewer than random search" · "64 of 88 designs decided"

## Before upload

- [ ] No Higgsfield clip contains readable text; all text comes from overlays.
- [ ] Every number matches a card above exactly.
- [ ] The wording follows the table above: "a verifier decides, a red team attacks", not "two checkers"; "certified" or "∎", not "✓✓ proved".
- [ ] Credits: "Characters and scenes AI-generated with Higgsfield. All numbers from results/FROZEN.json."
