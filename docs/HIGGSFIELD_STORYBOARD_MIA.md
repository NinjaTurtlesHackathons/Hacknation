# Storyboard "Mia": Higgsfield production script (60 s, with 40 s "How it works")

**Structure:** 8 s problem → **40 s: the lab at work, as it really runs** → 12 s breakthrough and logo.
The 40-second middle shows, inside Mia's research world, every step the system actually takes, in the real order. It's made more dramatic in look, but the order and content match run `2026-10-04b`.

## Rules

1. **No text from Higgsfield.** Labels, numbers and the logo are overlays in the edit. Every prompt includes `no text, no letters`.
2. **The steps are real:** each shot below names its real counterpart in the run. Take overlay texts from the shot list as they are.
3. **The agents always look the same:** "light agents" (see below). They stay faceless, so nobody takes them for real people.
4. **Mia and the professor** are fictional characters. In the credits: "Characters and scenes AI-generated with Higgsfield."

## Look

- **Style suffix (every clip, matches the prob website):** `cinematic, 35mm film look, dark deep-navy night palette with teal and cyan light accents, soft concentric light ripples and fine star-like dust in the air, volumetric light, shallow depth of field, calm and precise, no text, no letters, no logos`
- **Negative prompt:** `text, letters, numbers, watermark, logo, garbled writing, faces on the light figures, extra fingers, distorted hands, purple neon, cartoon`
- **Light agents (always identical):** `a faceless humanoid figure made of soft translucent teal-cyan light and thin floating paper ribbons, calm and precise movements`
  - Red team, as the variant: `the same light figure but in dark smoky graphite with a thin red edge`
- **Mia:** `young woman about 24, warm brown skin, curly dark hair in a loose bun, round thin-framed glasses, oversized dark green knit sweater`
- **Professor:** `woman in her late fifties, short silver hair, dark navy blazer, reading glasses on a chain`
- **Setting:** an old university library at night that turns into a lab, with a round reading room under a dome, map tables, desks, and a massive brass gate (the verifier).

---

## Shot list

| # | Time | Picture (Higgsfield) | Camera | Real counterpart in the run | Overlay (edit) | Voiceover |
|---|---|---|---|---|---|---|
| **Problem** | | | | | | |
| 1 | 0–4 s | Mia at night at a library table, laptop with a red glow, stack of papers, coffee | Dolly In | – | – | *(rain, clock)* |
| 2 | 4–8 s | Close-up: she takes off her glasses, rubs her eyes, then sets her jaw and starts typing | Static → slight push | – | – | "Months of work. And none of it holds up." |
| **How it works (40 s)** | | | | | | |
| 3 | 8–12 s | Her question rises off the screen as glowing paper ribbons, drifts up through the dark library; the shelves light up one after another | Crane Up | Question F26 is posed, preregistration sealed | "Her question: which designs beat the proofreading limit?" | "Her question goes to a lab of AI agents." |
| 4 | 12–16 s | Round reading room under a dome: a tall light agent in the center sends threads of light out to six stations | Orbit (slow, 180°) | The lead (Omnigent) dispatches scout and planner in parallel | "Orchestrator: Omnigent" | "An orchestrator splits up the work." |
| 5 | 16–20 s | A small light agent reaches for a locked archive door; a brass lock flashes amber, the door stays shut, the agent turns back | Dolly In → stop | Policy DENY (`harness_only`): agents may only use the verified tools | "Denied by policy" (amber) | "Rules decide what each agent may touch." |
| 6 | 20–24 s | A light agent at a huge old map table; two routes of light spread across the map and split in two directions | Top Down → tilt | The planner chooses two rival experiments: O1 broad scan, O2 deep computation | "Two rival experiments" | "A planner picks two rival experiments …" |
| 7 | 24–28 s | Two light agents at two desks facing each other, mirror-symmetric; sheets of calculations swirl above both at the same time | Arc Left | Two researchers in parallel, experiments E11–E13 | "Running in parallel" | "… and runs them at the same time." |
| 8 | 28–32 s | A paper card glides on a beam of light into a massive brass gate full of gears; the gears lock, red light, the card is thrown back and tears | Crash Zoom In | Verifier rejects: "passed for 13 of 15 cases; fam2_13: rate out of range" | "Rejected: one rate out of range" (red) | "Every claim has to get past a verifier. Exact arithmetic. No opinion." |
| 9 | 32–36 s | The next card glides into the gate; gears turn smoothly, a heavy blue stamp comes down: a solid square burns into the paper | Dolly In, slow motion at the stamp | Verifier confirms proofreading-O19: "10 of 10 cases" | "∎ Confirmed · 10 of 10 cases" | "This one holds." |
| 10 | 36–40 s | Back at the map table: a pin (the old assumption) topples, one route of light goes out, a new route is drawn | Snorricam / slight handheld | O20 contradicts preregistered assumption A1 → the planner reopens A1, the plan changes to F27 | "Surprise: assumption overturned → plan changes" | "When a result surprises, the plan changes." |
| 11 | 40–44 s | Dark red-team figures strike at the stamped card with light hammers; sparks, the card stays whole | Whip Pan in, then static | The red team attacks O19/O20 with counter-checks: the claim stands | "Red team: claim stands" | "A red team attacks every result." |
| 12 | 44–48 s | Every page and every step links up into a glowing chain of small blocks that runs across the dome and locks shut | Crane Up into the dome | Hash chain sealed: 63 links | "63 links · every step sealed" | "Every step is sealed. Anyone can check it." |
| **Breakthrough and logo** | | | | | | |
| 13 | 48–52 s | Morning light, Mia laughs with relief, the professor behind her nods | Dolly Out | – | – | – |
| 14 | 52–56 s | Printed pages on the table (blank); a solid blue square is stamped onto the top sheet | Crane Down | The paper contains only verified claims | "Result 1 … ∎ · claim proofreading-O19" | "Proved, not claimed." |
| 15 | 56–60 s | A single blue square of light lifts off the paper, flies into the lens and fills the frame | FPV / Follow | – | Morph → **∎ Probatum**, "Claims you can check.", github.com/alizema700/Daddys-Project | *(music ends)* |

**Voiceover:** about 75 words. That fits comfortably in 60 s with pauses.

German, if you'd rather:
- 2: „Monate Arbeit. Und nichts davon hält."
- 3: „Ihre Frage geht an ein Labor aus KI-Agenten."
- 4: „Ein Orchestrator verteilt die Arbeit."
- 5: „Regeln bestimmen, was jeder Agent anfassen darf."
- 6–7: „Ein Planer wählt zwei rivalisierende Experimente … und lässt sie gleichzeitig laufen."
- 8: „Jede Behauptung muss durch ein Prüfprogramm. Exakte Rechnung, keine Meinung."
- 9: „Diese hält."
- 10: „Überrascht ein Ergebnis, ändert sich der Plan."
- 11: „Ein Red Team greift jedes Ergebnis an."
- 12: „Jeder Schritt ist versiegelt. Jeder kann nachprüfen."
- 14: „Bewiesen statt behauptet."

## Making it more dramatic without bending the truth

- **Pace:** shots 3–7 flow (orbits, cranes); shots 8–9 are the beat (crash zoom, slow motion at the stamp); shots 10–12 speed up again.
- **Sound design:**
  - Shot 5: a dull lock clack.
  - Shot 8: gears grind, then a hard "clank" at the rejection.
  - Shot 9: deep "thud" of the stamp, with a short silence before it.
  - Shot 11: metallic sparks.
  - Shot 12: a rising tone as the chain locks.
- **Music:** low pulse from shot 3, swells at shot 9, drops at 10 and builds into shot 12, resolves at shot 13.
- **Overlays:** Instrument Sans 600, white on a semi-transparent ink bar, lower left, 2–3 s per shot. Red only in shot 8, amber only in shots 5 and 10, blue ∎ in shots 9 and 14.

## Rendering

`python scripts/higgsfield_render.py --run` renders exactly these 15 shots (start frame with Soul, then Kling 2.5 image-to-video, 5 s, trimmed in the edit).
For identical faces, put your own start frames into `video/frames/<shot>.png`; the script then animates only those. Details are in the script header.

## Before upload

- [ ] No clip contains readable text.
- [ ] Overlays as they are in the table; numbers only from there.
- [ ] Order of shots 3–12 = order in the real run (question → dispatch → policy → plan → parallel → rejection → confirmation → surprise/new plan → red team → sealing).
- [ ] Credits: "Characters and scenes AI-generated with Higgsfield. Process and numbers from the real run 2026-10-04b."
