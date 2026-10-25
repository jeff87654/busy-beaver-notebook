import os, collections, re
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR

bdet = {}
with open(os.path.join(AUDIT_DIR, "blank_detail_919.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            tag, m, st, nK, nE, maxlen = p[0], p[1], p[2], int(p[3]), int(p[4]), int(p[5])
            first_ks = p[6] if len(p) > 6 else ""
            e_rebs   = p[7] if len(p) > 7 else ""
            last_k   = p[8] if len(p) > 8 else ""
            bdet[m] = {
                "st": st, "nK": nK, "nE": nE, "maxlen": maxlen,
                "first_ks": first_ks, "e_rebs": e_rebs, "last_k": last_k
            }

for r in rows:
    r["bdet"] = bdet.get(r["m"], {})

std_or_bacc = [r for r in rows if not r["in_cls53"] and all(x[0] == "K" and x[1] == [2, 2] for x in r["D"][1:])]
print(f"Total std_or_bacc rescued leaves: {len(std_or_bacc)}")

# Let's check b_acc leaves first (where D[0] != [2, 2] or b changes instead of a)
bacc_leaves = [r for r in std_or_bacc if not (r["D"][0][0] == "K" and r["D"][0][1] == [2, 2])]
std_leaves  = [r for r in std_or_bacc if (r["D"][0][0] == "K" and r["D"][0][1] == [2, 2])]
print(f"  std_leaves (D[0..5] all [2,2]): {len(std_leaves)}")
print(f"  bacc_leaves (D[0] != [2,2], D[1..5] == [2,2]): {len(bacc_leaves)}")

# Let's inspect all 26 bacc_leaves!
print("\n--- Inspecting 26 bacc_leaves ---")
def fmt_e(x):
    return x[0] if x[0] != "K" else f"[{x[4]}];{x[2]};{x[3]}"

for r in bacc_leaves:
    bd = r["bdet"]
    e_str = " ".join(f"E{a}:{fmt_e(r['E'][a])}" for a in [1,2,3,4,5,6,7,8,15,16])
    print(f"  [{r['tag']}] {r['m']} | st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}'")
    print(f"    first='{bd['first_ks']}' | last='{bd['last_k']}'")
    print(f"    {e_str}")
