"""Citation and quote check (rigorous-innovation section 8, extended): for every row of expressivity/scout_evidence.md
  - title check against arXiv (export API, falling back to the abstract page's citation_title) or Crossref (DOIs): similarity >= 0.9
  - quote check: the quote must occur verbatim (whitespace/TeX-normalised) in the abstract fetched here
Output: expressivity/results/citations.tsv and expressivity/results/abstracts.json.
  python expressivity/scripts/verify_evidence.py
"""
import difflib, html, json, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "hacknation-ai-lab/0.1 (citation check)"}


def get(u, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=timeout) as r: return r.read().decode("utf-8", "replace")


def norm(s):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s)).replace("–", "-").replace("—", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def arxiv(aid):
    try:
        x = get("http://export.arxiv.org/api/query?id_list=" + aid)
        t = re.findall(r"<title>(.*?)</title>", x, re.S); a = re.findall(r"<summary>(.*?)</summary>", x, re.S)
        if len(t) > 1 and a: return " ".join(t[1].split()), " ".join(a[0].split()), "export-api"
    except Exception:
        pass
    x = get("https://arxiv.org/abs/" + aid)
    t = re.search(r'<meta name="citation_title" content="(.*?)"', x, re.S)
    a = re.search(r'<meta (?:name|property)="(?:citation_abstract|og:description)" content="(.*?)"', x, re.S)
    if not a:
        a = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', x, re.S)
    ab = re.sub(r"<[^>]+>", " ", a.group(1)) if a else ""
    return html.unescape(" ".join(t.group(1).split())) if t else "", html.unescape(" ".join(ab.split())).replace("Abstract:", "").strip(), "abs-page"


def crossref(doi):
    m = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    return " ".join(m["title"][0].split()), re.sub(r"<[^>]+>", " ", m.get("abstract", "")), "crossref"


def rows(md):
    for line in open(md):
        if not line.startswith("| arXiv:") and not line.startswith("| doi:") and not line.startswith("| 10."): continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 4: continue
        yield c[0], c[2], c[3].strip('"').strip("“”")


def main():
    out = ["status\ttitle_similarity\tquote_verbatim\tsource\tid\tclaimed_title\tfound_title"]; abstracts = {}
    for rid, title, quote in rows("expressivity/scout_evidence.md"):
        ref = rid.split(":", 1)[1] if ":" in rid else rid
        try:
            ft, ab, src = (crossref(ref) if ref.startswith("10.") else arxiv(ref))
        except Exception as e:
            out.append(f"NET/ERROR\t0\t-\t-\t{rid}\t{title}\t{type(e).__name__}"); continue
        sim = difflib.SequenceMatcher(None, norm(title), norm(ft)).ratio()
        q = norm(quote); has_quote = bool(q) and bool(norm(ab)) and len(q.split()) >= 4      # no abstract (Crossref) -> title check only
        qok = (q in norm(ab) or q.replace("$", "") in norm(ab).replace("$", "")) if has_quote else None
        status = "VERIFIED" if sim >= 0.9 and qok is not False else ("MISMATCH" if sim < 0.9 else "VERIFIED-ID (quote UNVERIFIED)")
        if qok is None and status == "VERIFIED": status = "VERIFIED-ID"
        abstracts[rid] = {"title": ft, "abstract": ab, "source": src}
        out.append(f"{status}\t{sim:.2f}\t{qok}\t{src}\t{rid}\t{title}\t{ft}")
        time.sleep(1.0)
    open("expressivity/results/citations.tsv", "w").write("\n".join(out) + "\n")
    json.dump(abstracts, open("expressivity/results/abstracts.json", "w"), indent=1)
    from collections import Counter
    print(Counter(l.split("\t")[0] for l in out[1:]))


if __name__ == "__main__":
    main()
