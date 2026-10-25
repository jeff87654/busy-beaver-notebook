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

print(f"Total other_d in rescued_866: {len(other_d)}")

def fmt_cell(x):
    if x[0] == "K":
        return f"K:{x[4]};{x[2]};{x[3]}"
    return x[0]

groups = collections.defaultdict(list)
for r in other_d:
    d_sig = tuple(fmt_cell(x) for x in r["D"][:4])
    b1_sig = tuple(fmt_cell(x) for x in r["B1"][:2])
    e_sig = tuple(fmt_cell(r["E"][a]) for a in range(1, 7))
    bd = r["bdet"]
    key = (r["tag"], d_sig, b1_sig, e_sig)
    groups[key].append(r)

print(f"Unique groups in other_d: {len(groups)}")
out = []
for idx, (k, grp) in enumerate(sorted(groups.items(), key=lambda x: (-len(x[1]), x[0][0]))):
    tag, d_sig, b1_sig, e_sig = k
    r0 = grp[0]
    bd = r0["bdet"]
    out.append(f"=== OtherD #{idx+1:03d} (count={len(grp)}) tag=[{tag}] sample={r0['m']} ===")
    out.append(f"  D(1..4) : {d_sig}")
    out.append(f"  B1(3..4): {b1_sig}")
    out.append(f"  E(1..6) : {e_sig}")
    out.append(f"  Blank   : st={bd.get('st')} nK={bd.get('nK')} nE={bd.get('nE')} maxL={bd.get('maxlen')} e_rebs='{bd.get('e_rebs')}'")
    out.append(f"    first='{bd.get('first_ks')}' | last='{bd.get('last_k')}'")

with open(os.path.join(AUDIT_DIR, "step7a_other_d.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("Wrote step7a_other_d.txt")
