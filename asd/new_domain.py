"""Gerüst für eine neue Domäne: python -m asd.new_domain <name>  ->  asd/domains/<name>_domain.py + projects/<name>/"""
import os, re, sys

name = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Aufruf: python -m asd.new_domain <name>")
if not re.fullmatch(r"[a-z][a-z0-9_]*", name): sys.exit("Name: Kleinbuchstaben, Ziffern, Unterstrich")
dst = f"asd/domains/{name}_domain.py"
if os.path.exists(dst): sys.exit(f"{dst} existiert schon")
open(dst, "w").write(open("templates/domain_template.py").read().replace("{{NAME}}", name))
os.makedirs(f"projects/{name}", exist_ok=True)
print(f"angelegt: {dst}\nNächste Schritte:\n  1. check() + selftest() ausfüllen, dann: python -m asd.selftest {name}\n"
      f"  2. run_op(), kontext, primitive_doc, claim_doc ausfüllen\n  3. python -m asd.lab_loop --domain {name} --recherche --runden 4\n"
      f"  4. python -m asd.paper --domain {name} --titel \"...\" --autoren \"...\"")
