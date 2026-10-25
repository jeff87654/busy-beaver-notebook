import os, sys, collections

WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
from step5_analyze_probe_919 import rows

# Load blank_detail_919.tsv
bdet = {}
with open(os.path.join(WORKDIR, "blank_detail_919.tsv"), "r") as f:
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

other_d = [r for r in rows if not r["in_cls53"] and r["D_type"].startswith("OTHER_D")]
print(f"Total rescued OTHER_D: {len(other_d)}")

active_other_d = []
for r in other_d:
    bd = r["bdet"]
    st = bd["st"]
    nK = bd["nK"]
    maxL = bd["maxlen"]
    if st.startswith("H:"):
        continue
    if nK == 0:
        continue
    if nK >= 80 and maxL >= 80 and bd["nE"] <= 2:
        continue
    active_other_d.append(r)

print(f"Total active_other_d: {len(active_other_d)}")

# Let's group and print every single machine in active_other_d with full details
def fmt_cell(c):
    if c[0] == "K":
        return f"K:{c[4]};{c[2]}"
    return c[0]

groups = collections.defaultdict(list)
for r in active_other_d:
    key = (
        r["tag"],
        tuple(fmt_cell(x) for x in r["D"][:4]),
        tuple(fmt_cell(x) for x in r["B1"][:4]),
        tuple(fmt_cell(x) for x in r["B2"][:4]),
        tuple(fmt_cell(x) for x in r["LB1"][:4]),
        tuple(fmt_cell(r["E"][a]) for a in range(1, 9)),
    )
    groups[key].append(r)

sorted_groups = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0][0], kv[1][0]["m"]))
with open(os.path.join(WORKDIR, "step7s_all_122_detail.txt"), "w", encoding="utf-8") as out:
    for idx, (key, grp) in enumerate(sorted_groups, 1):
        tag, d_s, b1_s, b2_s, lb1_s, e_s = key
        r0 = grp[0]
        out.write(f"=== Group #{idx:02d} (count={len(grp)}) tag=[{tag}] ===\n")
        out.write(f"  D(1..6)  : {[fmt_cell(x) for x in r0['D']]}\n")
        out.write(f"  B1(3..8) : {[fmt_cell(x) for x in r0['B1']]}\n")
        out.write(f"  B2(5..10): {[fmt_cell(x) for x in r0['B2']]}\n")
        out.write(f"  B3(7..12): {[fmt_cell(x) for x in r0['B3']]}\n")
        out.write(f"  LB1(3..8): {[fmt_cell(x) for x in r0['LB1']]}\n")
        out.write(f"  LB2(5..10): {[fmt_cell(x) for x in r0['LB2']]}\n")
        out.write(f"  E(1..16) : {[(a, fmt_cell(r0['E'][a])) for a in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]]}\n")
        for r in grp:
            bd = r["bdet"]
            out.write(f"  m={r['m']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}'\n")
            out.write(f"    first='{bd['first_ks']}' | last='{bd['last_k']}'\n")
print("Wrote step7s_all_122_detail.txt")
