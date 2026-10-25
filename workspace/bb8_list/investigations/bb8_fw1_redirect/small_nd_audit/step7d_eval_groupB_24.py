import os, sys
from step5_analyze_probe_919 import rows, expand_ds, AUDIT_DIR
sys.path.insert(0, r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53")
from resid_groupB import eval_list, M

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

# Find all leaves with the Group B D-signature: D(1..4) = [2^2];5, [2,0];46, [2^2];9, [2,0];62
gb_leaves = []
for r in rows:
    D = r["D"]
    if len(D) >= 4 and D[0][:3] == ("K", [2, 2], 5) and D[1][:3] == ("K", [2, 0], 46):
        gb_leaves.append(r)

print(f"Total Group-B engine leaves in probe_919 (cls53 + rescued): {len(gb_leaves)}")
for r in gb_leaves:
    bd = bdet[r["m"]]
    first_k = bd["first_ks"].split(" -> ")[0] if bd["first_ks"] else ""
    # Wait: in kblank_detail, B0 was fixed (1 for n, 0 for o, 3 for p), which corresponds to b_rel = 0 in resid_groupB!
    # Let's check: for #17 in cls53, E1(45) -> [3, 2^44]; 3; B0 (Wait: after E(odd), a=8, b_rel=0! Because in resid_groupB, E(3) -> [3, 2, 1]; 8; b_rel=1? Let's check line 96 of resid_groupB: ([3, 2, 1], 8, 1) -> HALT!)
    print(f"  in_cls53={int(r['in_cls53'])} [{r['tag']}] {r['m']} | e_rebs='{bd['e_rebs']}' | first='{bd['first_ks']}'")
