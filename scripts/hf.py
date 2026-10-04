"""Higgsfield from the terminal: your own prompt, your own photo, your own video. Results land in video/out/.

  export HF_KEY="<key-id>:<key-secret>"

  python3 scripts/hf.py bild  "a woman in a library at night, cinematic"            # image from text
  python3 scripts/hf.py video "slow dolly in, she looks up" --foto mia.png          # animate your own photo (local file or URL)
  python3 scripts/hf.py video "rain on a window, cinematic"                         # video from text only
  python3 scripts/hf.py video "..." --foto mia.png --dauer 10 --modell hailuo      # 10 s, other model
  python3 scripts/hf.py roh <model-path> prompt="..." video_url=@clip.mp4           # any model; @file is uploaded automatically

Models (docs.higgsfield.ai): image higgsfield-ai/soul/standard; video kling = kling-video/v2.5-turbo/pro, hailuo = minimax/hailuo-2.3/standard.
For other models (e.g. motion transfer with your own video) take the model path from console.higgsfield.ai and use `roh`."""
import argparse, json, os, sys, time, urllib.request

VIDEO = {"kling": "kling-video/v2.5-turbo/pro", "hailuo": "minimax/hailuo-2.3/standard"}
OUT = "video/out"


def client():
    if not os.environ.get("HF_KEY") and not (os.environ.get("HF_API_KEY") and os.environ.get("HF_API_SECRET")):
        sys.exit('HF_KEY missing. First: export HF_KEY="<key-id>:<key-secret>"')
    import higgsfield_client
    return higgsfield_client


def datei_oder_url(hc, x):
    """Local file -> upload, return the public URL; URL -> unchanged."""
    if x.startswith(("http://", "https://")): return x
    if not os.path.exists(x): sys.exit(f"File not found: {x}")
    print(f"uploading {x} ..."); return hc.upload_file(x)


def speichern(r, name):
    os.makedirs(OUT, exist_ok=True); pfade = []
    medien = [m["url"] for m in r.get("images") or []] + ([r["video"]["url"]] if r.get("video") else [])
    for k, url in enumerate(medien):
        endung = os.path.splitext(url.split("?")[0])[1] or (".mp4" if "video" in str(r) else ".png")
        ziel = f"{OUT}/{name}{'_' + str(k + 1) if len(medien) > 1 else ''}{endung}"
        urllib.request.urlretrieve(url, ziel); pfade.append(ziel)
    if not medien: print(json.dumps(r, indent=1, ensure_ascii=False)[:1500])
    for p in pfade: print("saved:", p)
    return pfade


def los(hc, modell, args, name):
    print(f"-> {modell}  {json.dumps({k: (v[:60] + '…' if isinstance(v, str) and len(v) > 60 else v) for k, v in args.items()}, ensure_ascii=False)}")
    r = hc.subscribe(modell, arguments=args, on_enqueue=lambda rid: print(f"queued ({rid}), please wait ..."))
    if r.get("status") not in (None, "completed"): sys.exit(f"Failed: {r.get('status')} {r.get('error') or ''}")
    return speichern(r, name)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bild"); b.add_argument("prompt"); b.add_argument("--format", default="16:9"); b.add_argument("--anzahl", type=int, default=1)
    v = sub.add_parser("video"); v.add_argument("prompt"); v.add_argument("--foto", help="start image: local file or URL")
    v.add_argument("--dauer", type=int, default=5); v.add_argument("--modell", default="kling", choices=list(VIDEO)); v.add_argument("--negativ", default="text, letters, watermark, distorted hands")
    r = sub.add_parser("roh"); r.add_argument("modell"); r.add_argument("felder", nargs="*", help="key=value; value @file.ext is uploaded")
    for p in (b, v, r): p.add_argument("--name", default=None, help="file name of the result")
    a = ap.parse_args(); hc = client(); name = a.name or time.strftime("%H%M%S")
    if a.cmd == "bild":
        los(hc, "higgsfield-ai/soul/standard", {"prompt": a.prompt, "aspect_ratio": a.format, "num_images": a.anzahl}, name)
    elif a.cmd == "video":
        args = {"prompt": a.prompt, "duration": a.dauer}
        if a.modell == "kling": args["negative_prompt"] = a.negativ
        if a.foto: args["image_url"] = datei_oder_url(hc, a.foto)
        los(hc, f"{VIDEO[a.modell]}/{'image-to-video' if a.foto else 'text-to-video'}", args, name)
    else:
        args = {}
        for f in a.felder:
            k, _, w = f.partition("=")
            if w.startswith("@"): w = datei_oder_url(hc, w[1:])
            elif w.lstrip("-").replace(".", "", 1).isdigit(): w = float(w) if "." in w else int(w)
            args[k] = w
        los(hc, a.modell, args, name)


if __name__ == "__main__":
    main()
