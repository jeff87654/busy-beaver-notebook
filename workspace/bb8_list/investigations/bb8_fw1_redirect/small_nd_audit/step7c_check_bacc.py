import os
from step5_analyze_probe_919 import rows, AUDIT_DIR

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

print("--- cls53 leaves where D is not all [2,2] ---")
for r in rows:
    if r["in_cls53"] and not all(x[0] == "K" and x[1] == [2, 2] for x in r["D"]):
        d_str = [x[0] if x[0]!="K" else f"[{x[4]}];{x[2]};{x[3]}" for x in r["D"]]
        print(f"  [{r['tag']}] {r['m']} D={d_str}")

print("\n--- rescued leaves where D[0] == [2,2] and D[1] == [2,2] but not all D == [2,2] ---")
for r in rows:
    if not r["in_cls53"] and not all(x[0] == "K" and x[1] == [2, 2] for x in r["D"]):
        if r["D"][0][0] == "K" and r["D"][0][1] == [2, 2] and r["D"][1][0] == "K" and r["D"][1][1] == [2, 2]:
            bd = r["bdet"]
            d_str = [x[0] if x[0]!="K" else f"[{x[4]}];{x[2]};{x[3]}" for x in r["D"]]
            e_str = [r["E"][a][0] if r["E"][a][0]!="K" else f"[{r['E'][a][4]}];{r['E'][a][2]};{r['E'][a][3]}" for a in range(1, 9)]
            print(f"  [{r['tag']}] {r['m']} D={d_str}")
            print(f"    E(1..8)={e_str}")
            print(f"    blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' first='{bd['first_ks']}'")
