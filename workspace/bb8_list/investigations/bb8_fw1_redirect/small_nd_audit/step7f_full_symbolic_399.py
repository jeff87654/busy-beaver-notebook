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

def get_d_aff(r):
    a_outs = [x[2] for x in r["D"]]
    m = a_outs[1] - a_outs[0]
    c = a_outs[0] - m * 1
    return m, c

def apply_d_n(m, c, a, n):
    # Apply a -> m*a + c, n times
    for _ in range(n):
        a = m * a + c
    return a

# Let's inspect all 150 groups of std_399 from step6 and trace each machine!
# First, let's see what E-halt patterns exist across std_399:
e_pats = collections.Counter()
for r in std_399:
    ep = "".join(r["E"][a][0] for a in range(1, 17))
    e_pats[ep] += 1

print("E(1..16) patterns across std_399:")
for ep, cnt in e_pats.most_common():
    print(f"  {ep} : {cnt}")

# Let's check for each of the 399 machines:
# What happens on the blank tape?
# Let's parse the first K moment in blank_detail_919.tsv:
def parse_k_str(ks):
    # @step:[ds];a;b
    m = re.match(r"^@(\d+):\[([^\]]*)\];(-?\d+);(-?\d+)$", ks.strip())
    if not m:
        return None
    step = int(m.group(1))
    ds = expand_ds(m.group(2))
    a = int(m.group(3))
    b = int(m.group(4))
    return step, ds, a, b

# Let's check if any machine in std_399 has nK == 0 on blank tape:
nk0 = [r for r in std_399 if r["bdet"]["nK"] == 0]
print(f"\nstd_399 with nK == 0 on blank tape: {len(nk0)}")
for r in nk0:
    print(f"  [{r['tag']}] {r['m']} st={r['bdet']['st']}")
