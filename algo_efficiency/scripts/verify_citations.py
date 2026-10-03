# Citation check from the rigorous-innovation skill (section 8). Input TSV: title<TAB>DOI-or-arXiv-ID; output: status, similarity, found title.
import re, sys, json, difflib, urllib.request, urllib.parse
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ri/1.0"}), timeout=20) as r: return r.read().decode()
def check(title, ref):
    try:
        t = (json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(ref)))["message"]["title"][0]
             if ref.lower().startswith("10.") else re.findall(r"<title>(.*?)</title>", get("http://export.arxiv.org/api/query?id_list=" + ref), re.S)[1])
        s = difflib.SequenceMatcher(None, title.lower(), " ".join(t.split()).lower()).ratio()
        return ("VERIFIED" if s >= 0.9 else "MISMATCH"), round(s, 2), " ".join(t.split())
    except Exception as e:
        return "NET/ERROR -> check via WebFetch", 0, type(e).__name__
for line in open(sys.argv[1]):
    if "\t" in line:
        title, ref = line.rstrip("\n").split("\t")[:2]; print(*check(title, ref.strip()), title, ref, sep="\t")
