"""paper.md -> paper.pdf ohne LaTeX: Markdown -> HTML (Preprint-Satz) -> Chromium headless (print-to-pdf).
  python -m asd.pdf projects/bell/paper.md"""
import html, os, re, shutil, subprocess, sys, tempfile
import markdown

CSS = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm; @bottom-center { content: counter(page); } }
body { font-family: "Latin Modern Roman", "Times New Roman", Times, serif; font-size: 10.5pt; line-height: 1.38; color: #111; }
h1 { font-size: 17pt; text-align: center; line-height: 1.25; margin: 0 0 6pt 0; font-weight: bold; }
.authors { text-align: center; font-size: 11pt; margin-bottom: 18pt; color: #222; }
h2 { font-size: 12.5pt; margin: 16pt 0 5pt 0; }
h2#abstract + p, .abstract { margin: 0 6% 10pt 6%; font-size: 10pt; text-align: justify; }
p, li { text-align: justify; hyphens: auto; }
ul { padding-left: 18pt; margin: 4pt 0 6pt 0; }
table { border-collapse: collapse; margin: 8pt auto 10pt auto; font-size: 8.8pt; }
th, td { padding: 2.5pt 6pt; text-align: left; }
thead th { border-top: 1.2pt solid #000; border-bottom: 0.6pt solid #000; }
tbody tr:last-child td { border-bottom: 1.2pt solid #000; }
code { font-size: 9pt; }
.cit { font-size: 7.5pt; color: #666; white-space: nowrap; }
hr { border: none; border-top: 0.5pt solid #999; margin-top: 18pt; }
hr + p { font-size: 8.5pt; color: #444; }
"""


def render(md_path):
    md = open(md_path).read().split("\n")
    title = md[0].lstrip("# ").strip(); authors = md[2].strip(); body = "\n".join(md[4:])
    body = re.sub(r"(?<=\S)\n(- )", r"\n\n\1", body)                          # Listen nach Absatz-Zeile
    h = markdown.markdown(body, extensions=["tables", "toc"])
    h = re.sub(r"\[(C-[^\]]+)\]", lambda m: f'<span class="cit">[{m.group(1)}]</span>', h)
    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{CSS}</style></head>"
           f"<body><h1>{html.escape(title)}</h1><div class='authors'>{html.escape(authors)}</div>{h}</body></html>")
    out_html = md_path[:-3] + ".html"; open(out_html, "w").write(doc)
    exe = os.environ.get("CHROME") or shutil.which("chromium") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
    pdf = os.path.abspath(md_path[:-3] + ".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([exe, "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-data-dir={tmp}", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", "file://" + os.path.abspath(out_html)], capture_output=True, timeout=120)
    return pdf if os.path.exists(pdf) else None


if __name__ == "__main__":
    print(render(sys.argv[1]))
