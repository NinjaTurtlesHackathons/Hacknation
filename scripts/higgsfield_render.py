"""Render the Higgsfield clips of the "Mia" storyboard (docs/HIGGSFIELD_STORYBOARD_MIA.md) through the Higgsfield API.

Per shot: a start frame (Soul, 16:9), then image-to-video (Kling 2.5 Turbo Pro, 5 s). Output lands in video/clips/<shot>.mp4,
start frames in video/frames/<shot>.jpg. If your own start frame already exists in video/frames/<shot>.(png|jpg)
(for example made in the web app with a Soul character reference, for identical faces), it is uploaded and used instead.

  pip install higgsfield-client
  export HF_KEY="<key-id>:<key-secret>"            # from console.higgsfield.ai, never commit
  python scripts/higgsfield_render.py               # dry run: shows what would be generated, costs nothing
  python scripts/higgsfield_render.py --run --only 08,09     # generate just these shots (costs credits)
  python scripts/higgsfield_render.py --run                  # all 15 shots

Endpoints as in docs.higgsfield.ai (OpenAPI): higgsfield-ai/soul/standard, kling-video/v2.5-turbo/pro/image-to-video."""
import argparse, json, os, sys, urllib.request

BILD = "higgsfield-ai/soul/standard"
VIDEO = "kling-video/v2.5-turbo/pro/image-to-video"
STIL = ("cinematic, 35mm film look, dramatic chiaroscuro light, warm library tones with cool deep-blue light accents, "
        "volumetric light through dust, shallow depth of field, no text, no letters, no logos")
NEG = "text, letters, numbers, watermark, logo, garbled writing, faces on the light figures, extra fingers, distorted hands, purple neon, cartoon"
MIA = ("young woman about 24, warm brown skin, curly dark hair in a loose bun, round thin-framed glasses, "
       "oversized dark green knit sweater")
PROF = "woman in her late fifties, short silver hair, dark navy blazer, reading glasses on a chain"
AGENT = "a faceless humanoid figure made of soft translucent deep-blue light and thin floating paper ribbons"
RED = "faceless humanoid figures made of dark smoky graphite light with a thin red edge"
ORT = "in an old university library at night that has become a laboratory"

SHOTS = {   # shot: (start frame, motion/video prompt), from docs/HIGGSFIELD_STORYBOARD_MIA.md (60 s, 40 s "How it works")
    "01": (f"{MIA} alone at a long wooden library table at night, laptop with a red glow on her face, stack of printed papers, coffee cup, rain on a tall window",
           "slow dolly in toward her, she stares at the screen and exhales"),
    "02": (f"close-up of {MIA} lit by a laptop screen at night", "she takes off her glasses, rubs her eyes, then sets her jaw and starts typing, slight push in"),
    "03": (f"glowing paper ribbons rising from a laptop screen into the dark air {ORT}, tall bookshelves", "crane up following the ribbons, the shelves light up one after another"),
    "04": (f"{AGENT} standing in the center of a round domed reading room {ORT}, six empty desks around it", "slow 180 degree orbit, the figure sends thin threads of blue light out to the six desks"),
    "05": (f"a small {AGENT} reaching for a heavy locked archive door with a brass lock {ORT}", "dolly in, the brass lock flashes amber, the door stays shut, the figure turns back"),
    "06": (f"{AGENT} leaning over a huge old map table {ORT}", "top down view tilting up, two routes of blue light spread across the map and split in two directions"),
    "07": (f"two copies of {AGENT} at two facing wooden desks, mirror symmetric composition {ORT}", "arc left, sheets of calculations swirl above both desks at the same time"),
    "08": (f"a single blank paper card floating on a beam of light toward a massive brass gate full of interlocking gears {ORT}",
           "crash zoom in, the gears lock with red light, the card is thrown back and tears"),
    "09": (f"a blank paper card sliding into a massive brass gate full of gears {ORT}, a heavy stamp above it",
           "dolly in, gears turn smoothly, slow motion as the heavy stamp presses a solid deep blue square into the paper"),
    "10": (f"{AGENT} at the old map table with a brass pin standing on the map {ORT}", "the pin topples, one route of light fades out and a new route is drawn, slight handheld camera"),
    "11": (f"{RED} around a paper card stamped with a solid blue square floating in the air {ORT}", "whip pan in, the figures strike the card with hammers of light, sparks fly, the card stays whole"),
    "12": (f"a chain of small glowing blue blocks forming across the underside of a library dome {ORT}", "crane up into the dome as the chain links up and locks shut"),
    "13": (f"{MIA} laughing with relief in a sunlit library, {PROF} standing behind her looking at the laptop", "slow dolly out, Mia laughs and covers her mouth, the professor nods"),
    "14": ("a few blank printed paper pages on a wooden library table in morning sunlight", "slow crane down, a solid deep blue square is stamped onto the top sheet"),
    "15": ("a single small solid deep blue square of light floating above a sheet of paper", "the blue square lifts off and flies straight into the lens until it fills the frame"),
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
