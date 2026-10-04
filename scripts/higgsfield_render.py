"""Render the Higgsfield clips of the "Mia" storyboard (docs/HIGGSFIELD_STORYBOARD_MIA.md) through the Higgsfield API.

Per shot: a start frame (Soul, 16:9), then image-to-video (Kling 2.5 Turbo Pro, 5 s). Output lands in video/clips/<shot>.mp4,
start frames in video/frames/<shot>.jpg. If your own start frame already exists in video/frames/<shot>.(png|jpg)
(for example made in the web app with a Soul character reference, for identical faces), it is uploaded and used instead.

  pip install higgsfield-client
  export HF_KEY="<key-id>:<key-secret>"            # from console.higgsfield.ai, never commit
  python scripts/higgsfield_render.py               # dry run: shows what would be generated, costs nothing
  python scripts/higgsfield_render.py --run --only 1a,7a     # generate just these shots (costs credits)
  python scripts/higgsfield_render.py --run                  # all 14 shots

Endpoints as in docs.higgsfield.ai (OpenAPI): higgsfield-ai/soul/standard, kling-video/v2.5-turbo/pro/image-to-video."""
import argparse, json, os, sys, urllib.request

BILD = "higgsfield-ai/soul/standard"
VIDEO = "kling-video/v2.5-turbo/pro/image-to-video"
STIL = ("cinematic, 35mm film look, soft natural light, muted palette with one deep blue accent, shallow depth of field, "
        "no text, no letters, no logos")
NEG = "text, letters, numbers, watermark, logo, garbled screen text, extra fingers, distorted hands, neon, purple gradient"
MIA = ("young woman about 24, warm brown skin, curly dark hair in a loose bun, round thin-framed glasses, "
       "oversized dark green knit sweater")
PROF = "woman in her late fifties, short silver hair, dark navy blazer, reading glasses on a chain"
DOK = "man about 28, short black hair, light stubble, grey hoodie"
LEITER = "man in his forties, rolled-up shirt sleeves, lab badge on a lanyard"

SHOTS = {   # shot: (start frame, motion/video prompt), from the storyboard (60 s version)
    "1a": (f"{MIA} sitting alone at a long wooden library table at night, laptop with a red glow on her face, paper coffee cup, "
           "tall stack of printed papers, warm desk lamp, dark bookshelves, rain on a tall window",
           "slow dolly in toward her, she stares at the screen and exhales, rain streaks on the window"),
    "1b": (f"close-up of {MIA} lit by a laptop screen at night in a library",
           "static camera, she takes off her glasses and rubs her eyes, tired"),
    "2a": (f"{DOK} standing in a university corridor staring at a laptop", "he shakes his head slowly, camera whip pans right at the end"),
    "2b": (f"{PROF} in her office holding a red pen over a printed manuscript, frowning", "she taps the pen on the page, camera whip pans right at the end"),
    "2c": (f"{LEITER} in a bright modern lab corridor holding a sheet of paper up to the light, sceptical",
           "quick crash zoom onto his face as he lowers the paper and shakes his head"),
    "3a": (f"{MIA} at the same library table in early morning light, sitting up straight and typing, laptop screen plain off-white and blank",
           "camera arcs slowly to the right around her, she types with focus, morning light grows"),
    "3b": (f"over-the-shoulder shot of {MIA} at a laptop with a blank off-white screen, morning library",
           "slow dolly in over her shoulder as she leans forward expectantly"),
    "5a": (f"{PROF} at her desk reading a printout, laptop beside her with a blank screen", "slow dolly in, she reads and nods with approval"),
    "5b": (f"{DOK} at a desk looking at his laptop with a blank screen", "static camera, he looks surprised and points at the screen"),
    "6a": (f"{MIA} laughing with relief in a sunlit library, {PROF} standing behind her looking at the laptop",
           "slow dolly out, Mia laughs and covers her mouth, the professor nods"),
    "6b": ("close-up of a few blank printed paper pages on a wooden library table, sunlight", "slow crane down onto the pages"),
    "7a": (f"{MIA} with friends in graduation gowns on a sunny lawn throwing their caps into the air, golden hour",
           "slow motion, the caps leave their hands, gowns flutter, everyone laughing"),
    "7b": ("low angle of graduation caps spinning in the air against a clear deep blue sky", "slow crane up in slow motion"),
    "8a": ("a single black graduation cap spinning toward the camera against a deep blue sky",
           "the cap flies straight into the lens until it fills the whole frame"),
}


def laden(url, ziel):
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as r, open(ziel, "wb") as f: f.write(r.read())
    return ziel


def shot(hc, sid, bild_prompt, video_prompt, dauer):
    eigen = next((p for p in (f"video/frames/{sid}.png", f"video/frames/{sid}.jpg") if os.path.exists(p)), None)
    if eigen:
        bild_url = hc.upload_file(eigen); print(f"[{sid}] own start frame {eigen} uploaded")
    else:
        r = hc.subscribe(BILD, arguments={"prompt": f"{bild_prompt}, {STIL}", "aspect_ratio": "16:9", "resolution": "2K"},
                         on_enqueue=lambda rid: print(f"[{sid}] start frame queued ({rid})"))
        bild_url = r["images"][0]["url"]; laden(bild_url, f"video/frames/{sid}.jpg")
    r = hc.subscribe(VIDEO, arguments={"prompt": f"{video_prompt}, {STIL}", "image_url": bild_url, "duration": dauer, "negative_prompt": NEG},
                     on_enqueue=lambda rid: print(f"[{sid}] video queued ({rid})"))
    if r.get("status") not in (None, "completed"): raise RuntimeError(f"{sid}: status {r.get('status')} {r.get('error')}")
    pfad = laden(r["video"]["url"], f"video/clips/{sid}.mp4"); print(f"[{sid}] done -> {pfad}"); return pfad


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true", help="really generate (costs credits)")
    ap.add_argument("--only", default="", help="e.g. 1a,7a"); ap.add_argument("--dauer", type=int, default=5, choices=[5, 10]); a = ap.parse_args()
    auswahl = [s for s in SHOTS if not a.only or s in a.only.split(",")]
    if not a.run:
        for s in auswahl: print(f"{s}: image <- {SHOTS[s][0][:90]}...\n    video <- {SHOTS[s][1]}")
        print(f"\nDry run: {len(auswahl)} shots, each 1 image + 1 video of {a.dauer} s. Generate with --run (needs HF_KEY)."); return
    if not os.environ.get("HF_KEY") and not (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET")):
        sys.exit('HF_KEY missing: export HF_KEY="<key-id>:<key-secret>" (console.higgsfield.ai)')
    import higgsfield_client as hc
    fertig, fehler = [], []
    for s in auswahl:
        try: fertig.append(shot(hc, s, *SHOTS[s], a.dauer))
        except Exception as e: fehler.append(s); print(f"[{s}] ERROR {type(e).__name__}: {e}")
    print(json.dumps({"done": len(fertig), "errors": fehler}, ensure_ascii=False))


if __name__ == "__main__":
    main()
