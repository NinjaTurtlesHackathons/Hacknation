"""Certify (rationally, with the exact verifier) every atlas improvement found by the cover scans."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certify_cover import certify
W = [("8_4","16_4",3),("16_8","32_9",3),("16_9","32_14",3),("16_12","32_23",4),("16_13","32_28",3),("24_4","48_13",3),
     ("24_5","48_14",3),("32_4","64_17",5),("32_8","64_5",5),("32_10","64_21",4),("32_13","64_21",4),("32_19","64_38",3),
     ("32_20","64_47",3),("32_24","64_61",4),("32_26","64_59",5),("32_29","64_61",4),("32_30","64_75",4),("32_31","64_71",4),
     ("32_32","64_70",5),("32_33","64_77",4),("32_35","64_65",4),("32_40","64_95",4),("32_41","64_107",4),("32_42","64_147",3),
     ("32_44","64_98",5),("32_48","64_203",4),("32_50","64_218",5),("40_4","80_13",3),("40_5","80_14",3),("48_6","96_28",3),
     ("48_8","96_25",3),("48_11","96_38",4),("48_12","96_38",4),("48_16","96_39",4),("48_18","96_14",5),("48_34","96_132",4),
     ("48_37","96_137",3),("48_39","96_145",4),("48_40","96_98",5),("56_3","112_12",3),("56_4","112_13",3)]
done = set(f[2:].rsplit("_k", 1)[0] for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")))
for g, h, k in W:
    if g in done and g != "8_4": print(g, "already certified"); continue
    gn, gi = map(int, g.split("_")); hn, hi = map(int, h.split("_"))
    claim, why = certify(gn, gi, hn, hi, k)
    print(g, h, k, "CERTIFIED" if claim else "NOT", why if claim else why, flush=True)
    if claim:
        json.dump(claim, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", f"SG{g}_k{k}.json"), "w"))
