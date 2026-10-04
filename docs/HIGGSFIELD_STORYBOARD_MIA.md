# Storyboard "Mia": Higgsfield production script (75 s)

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

## Scenes and clips

| # | Time | Clip (Higgsfield) | Camera motion | Overlay in the edit | Voiceover / sound |
|---|---|---|---|---|---|
| **1 Despair** | | | | | |
| 1a | 0–4 s | **Mia** at night in a library, alone at a long table, laptop, paper cup of coffee, stack of printed papers, warm desk lamp, dark shelves; `the laptop screen glows red, no readable text` | Dolly In (slow) | – | Rain, a clock ticking |
| 1b | 4–8 s | Close-up of Mia's face lit by the screen glow, she takes off her glasses and rubs her eyes | Static, slight handheld | Red error lines as an abstract overlay (blurred, illegible) | **„Monate Arbeit. Und nichts davon hält."** |
| **2 The bottleneck** | | | | | |
| 2a | 8–10 s | **PhD student** in a corridor staring at his laptop, shaking his head | Whip Pan into the next clip | – | – |
| 2b | 10–12 s | **Professor** in her office, red pen hovering over a printed manuscript, frowning | Whip Pan | – | – |
| 2c | 12–14 s | **Lab head** in a bright lab, holding a sheet of results up to the light, sceptical | Crash Zoom In (short) | – | **„Forschung scheitert nicht an Ideen, sondern am Prüfen."** |
| **3 First contact** | | | | | |
| 3a | 14–18 s | Mia in the library, morning light now, she sits up straight and types; `laptop screen shows a plain off-white page, blank, no text` | Arc Right (slow) | **Overlay:** her question appears as a chat bubble on the laptop, e.g. "Which of the open designs can beat the proofreading limit?" | – |
| 3b | 18–22 s | Over-the-shoulder shot of Mia, screen out of focus, she leans in expectantly | Dolly In | **Overlay:** a small ∎ blinks on, then text in the UI style: "Ask your question." | **„Stell deine Frage."** |
| **4 The lab at work (key moment)** | | | | | |
| 4a | 22–28 s | **Pure motion design, no Higgsfield clip:** four bubbles with icons (Scout 🔍, Planner 🧭, Researchers 🧪🧪, Red team 🛡), arrows between them, two experiment lanes running in parallel. Or a **real screen recording** of the run page (event stream with agent lanes) as the background | – | Bubbles on paper white `#F6F7F5`, ink `#1C2430`, accent `#23408E` | **„Agenten schlagen vor."** |
| 4b | 28–33 s | Motion design: a claim card ("rate within bounds for 15 designs") is **struck through in red**, label "Rejected: one rate out of range". Use the **real reason** from run 2026-10-04b | – | Red line drawn in over 300 ms, soft dull sound | **„Ein Prüfprogramm entscheidet …"** |
| 4c | 33–38 s | Motion design: the next card ("10 designs below the limit") gets a **blue ∎ / ✓ certified**, small stamp effect; the red-team shield bounces off it | – | Stamp at 280 ms, a gentle "thud" | **„… und ein Red Team greift jedes Ergebnis an."** |
| **5 Others use it** | | | | | |
| 5a | 38–41 s | **Professor** at her desk, now nodding while she reads a printout, laptop beside her (screen blank) | Dolly In | **Overlay card:** "0 of 20 random claims accepted" | Music picks up |
| 5b | 41–44 s | **PhD student** looks surprised at his laptop, points at the screen | Static | **Overlay card:** "Result changed the plan" (in the run, a confirmed result really did overturn a preregistered assumption) | – |
| 5c | 44–48 s | Cards fly in one after another over a blurred library background (no Higgsfield clip needed; or 1a softly blurred) | – | **Cards:** "2 of 2 planted false claims caught" · "3.96× fewer verifier calls than a hand-written heuristic (25 seeds)" · "64 of 88 designs decided" | – |
| **6 Breakthrough** | | | | | |
| 6a | 48–52 s | Mia laughs with relief, leans back, sunlight in the library | Dolly Out (slow) | – | – |
| 6b | 52–55 s | **Professor** stands behind Mia, looks at the screen, nods with approval | Arc Left | – | – |
| 6c | 55–58 s | Close-up of printed paper pages on the table (blank, no text) | Crane Down onto the paper | **Overlay:** "Result 1" + a short line + ∎ + "claim proofreading-O19" | **„Bewiesen statt behauptet."** |
| **7 Graduation** | | | | | |
| 7a | 58–63 s | Graduation outdoors, Mia in gown with friends (PhD student among them), all throwing their caps in the air, golden-hour light | **Slow Motion** / Bullet Time | – | Music swells |
| 7b | 63–68 s | Low angle: caps spinning against a blue sky | Crane Up (slow, slow motion) | – | – |
| **8 Logo** | | | | | |
| 8a | 68–72 s | A single cap flies straight toward the camera and fills the frame | FPV / Follow | **Transition in the edit:** the dark cap fills the frame and morphs into the blue square (shape morph in AE / CapCut "Morph") | – |
| 8b | 72–75 s | Paper-white background (no Higgsfield clip needed) | – | **∎ Probatum**, below it "Proved, not claimed." / "Claims you can check." and `github.com/alizema700/Daddys-Project` | Music ends on one note |

---

## Higgsfield prompts ready to copy (the most important clips)

**1a** — `[Mia reference] sitting alone at a long wooden library table at night, laptop open with a red glow on her face, paper coffee cup, tall stack of printed papers, single warm desk lamp, dark bookshelves behind, rain on the tall window` + style suffix · Motion: **Dolly In** · Video: `slow push in, she stares at the screen, exhales, rain streaks on the window`

**2c** — `[lab head reference] in a bright modern lab corridor holding a sheet of paper up to the light, sceptical frown` + style suffix · Motion: **Crash Zoom In** · Video: `quick zoom onto his face as he lowers the paper and shakes his head`

**3a** — `[Mia reference] at the same library table in early morning light, sitting up straight and typing, laptop screen plain off-white and blank` + style suffix · Motion: **Arc Right** · Video: `camera arcs slowly around her, she types with focus, morning light grows`

**6a** — `[Mia reference] laughing with relief, leaning back in her chair, sunlight flooding the library` + style suffix · Motion: **Dolly Out** · Video: `she laughs and covers her mouth, camera pulls back slowly`

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
- "5.26× fewer than random search"
- "64 of 88 designs decided: 50 proved, 14 exact counterexamples"

## Before upload

- [ ] No Higgsfield clip contains readable text; all text comes from overlays.
- [ ] Every number matches a card above exactly.
- [ ] The wording follows the table above: "a verifier decides, a red team attacks", not "two checkers"; "certified" or "∎", not "✓✓ proved".
- [ ] Credits: "Characters and scenes AI-generated with Higgsfield. All numbers from results/FROZEN.json."
