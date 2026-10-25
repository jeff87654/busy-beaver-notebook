import os, collections
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

other_d = []
for r in rows:
    if r["in_cls53"]:
        continue
    D = r["D"]
    if all(x[0] == "K" and x[1] == [2, 2] for x in D[1:]):
        continue
    other_d.append(r)

cats = collections.Counter()
interesting = []
for r in other_d:
    bd = r["bdet"]
    st = bd["st"]
    nK = bd["nK"]
    nE = bd["nE"]
    maxL = bd["maxlen"]
    D = r["D"]
    if st.startswith("H:"):
        cats["1_Blank_Halted_1M"] += 1
    elif nK == 0:
        cats["2_Blank_Never_Reaches_K"] += 1
    elif nK >= 80 and maxL >= 80:
        cats["3_Poly_List_Grower_Broken_D"] += 1
    else:
        cats["4_Other_Active_K"] += 1
        interesting.append(r)

print("Summary of 441 other_d leaves:")
for k, v in sorted(cats.items()):
    print(f"  {k:32s}: {v}")

print(f"\nInspecting all {len(interesting)} '4_Other_Active_K' leaves (grouped by tag, D, B1, E):")
def fmt_cell(x):
    if x[0] == "K":
        return f"K:{x[4]};{x[2]};{x[3]}"
    return x[0]

igroups = collections.defaultdict(list)
for r in interesting:
    d_sig = tuple(fmt_cell(x) for x in r["D"][:4])
    b1_sig = tuple(fmt_cell(x) for x in r["B1"][:4])
    b2_sig = tuple(fmt_cell(x) for x in r["B2"][:4])
    lb1_sig = tuple(fmt_cell(x) for x in r["LB1"][:4])
    e_sig = tuple(fmt_cell(r["E"][a]) for a in range(1, 9))
    key = (r["tag"], d_sig, b1_sig, b2_sig, lb1_sig, e_sig)
    igroups[key].append(r)

out = []
for idx, (k, grp) in enumerate(sorted(igroups.items(), key=lambda x: (-len(x[1]), x[0][0]))):
    tag, d_sig, b1_sig, b2_sig, lb1_sig, e_sig = k
    r0 = grp[0]
    bd = r0["bdet"]
    out.append(f"=== ActiveOtherD #{idx+1:02d} (count={len(grp)}) tag=[{tag}] sample={r0['m']} ===")
    out.append(f"  D(1..4)  : {d_sig}")
    out.append(f"  B1(3..6) : {b1_sig}")
    out.append(f"  B2(5..8) : {b2_sig}")
    out.append(f"  LB1(3..6): {lb1_sig}")
    out.append(f"  E(1..8)  : {e_sig}")
    for rr in grp[:3]:
        bdr = rr["bdet"]
        out.append(f"  m={rr['m']} st={bdr['st']} nK={bdr['nK']} nE={bdr['nE']} maxL={bdr['maxlen']} e_rebs='{bdr['e_rebs']}'")
        out.append(f"    first='{bdr['first_ks']}' | last='{bdr['last_k']}'")

with open(os.path.join(AUDIT_DIR, "step7b_active_other_d.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {len(igroups)} groups ({len(interesting)} leaves) to step7b_active_other_d.txt")
