import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR

bdet = {}
with open(os.path.join(AUDIT_DIR, "blank_detail_919.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            bdet[p[1]] = {
                "st": p[2], "nK": int(p[3]), "nE": int(p[4]), "maxlen": int(p[5]),
                "first_ks": p[6] if len(p) > 6 else "",
                "e_rebs": p[7] if len(p) > 7 else "",
                "last_k": p[8] if len(p) > 8 else ""
            }

for r in rows:
    r["bdet"] = bdet.get(r["m"], {})

std_399 = [r for r in rows if not r["in_cls53"] and all(x[0] == "K" and x[1] == [2, 2] for x in r["D"])]

# First let's inspect the 8 leaves with D = 5a+4!
print("=== 8 leaves with D = 5a+4 ===")
for r in std_399:
    a_outs = [x[2] for x in r["D"]]
    if a_outs[1] - a_outs[0] == 5 and a_outs[0] == 9:
        bd = r["bdet"]
        e_s = [f"{a}:{r['E'][a][4]};{r['E'][a][2]}" if r["E"][a][0]=="K" else f"{a}:{r['E'][a][0]}" for a in range(1, 9)]
        b1_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["B1"][:4]]
        b2_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["B2"][:4]]
        b3_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["B3"][:4]]
        lb1_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["LB1"][:4]]
        lb2_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["LB2"][:4]]
        print(f"  [{r['tag']}] {r['m']}")
        print(f"    E(1..8) : {e_s}")
        print(f"    B1(3..6): {b1_s}")
        print(f"    B2(5..8): {b2_s}")
        print(f"    B3(7..10): {b3_s}")
        print(f"    LB1(3..6): {lb1_s}")
        print(f"    LB2(5..8): {lb2_s}")
        print(f"    blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' first='{bd['first_ks']}'")
