"""Full-text quote check for the closest prior work (abstracts do not state these results): fetch the arXiv HTML, strip markup
(MathML is rendered as spaced text, e.g. 'S 4'), and require the quote verbatim. Output: expressivity/results/body_quotes.json.
  python expressivity/scripts/body_quotes.py"""
import html, json, re, urllib.request

QUOTES = {
    "deltaproduct": ("2502.10297", "Unexpectedly, S 4 and A 5 can extrapolate robustly using only n h = 2 despite the theorem suggesting 3 and 4, respectively."),
    "deltaproduct-so3": ("2502.10297", "This efficiency arises from their isomorphism to subgroups of SO ⁡ ( 3 , ℝ ) , i.e. the group of 3D rotations"),
    "howe-law": ("2609.18966", "the minimal n h that length-generalizes equals the maximal generator reflection length rank ⁡ ( I − P ) in the representation pinned by the task format (parity 1, S 4 3, A 5 / S 5 4)"),
    "howe-format": ("2609.18966", "S 4 (transposition + 4-cycle), A 5 (3-cycle + 5-cycle; all-even), S 5 (transposition + 5-cycle; non-solvable)"),
    "rwkv7-swaps": ("2503.14456", "RWKV-7 can, by Lemma 2 , solve the problem of tracking swaps on five elements."),
    "grazzi-cd": ("2411.12537", "every n × n orthogonal matrix can be written as a product of n reflections, due to the Cartan–Dieudonné Theorem"),
}


def text(aid):
    req = urllib.request.Request(f"https://arxiv.org/html/{aid}", headers={"User-Agent": "hacknation-ai-lab/0.1 (quote check)"})
    s = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    s = re.sub(r"<(script|style|annotation)[^>]*>.*?</\1>", " ", s, flags=re.S); s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


cache, out = {}, {}
for key, (aid, q) in QUOTES.items():
    if aid not in cache: cache[aid] = text(aid)
    out[key] = {"id": f"arXiv:{aid}", "quote": q, "verified": q in cache[aid]}
    print(key, out[key]["verified"])
json.dump(out, open("expressivity/results/body_quotes.json", "w"), indent=1, ensure_ascii=False)
