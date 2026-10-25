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
print(f"Loaded {len(std_399)} std_d rescued leaves")

# Let's parse the blank-tape initial K-configuration or E1 configuration for each of the 399 leaves
def parse_k_moment(s):
    # format: @step:[ds];a;b
    if not s or ":" not in s:
        return None
    step_s, rest = s.split(":", 1)
    step = int(step_s[1:])
    ds_part, a_s, b_s = rest.split(";")
    ds_str = ds_part[1:-1]
    return step, expand_ds(ds_str), int(a_s), int(b_s), ds_str

# Let's inspect the D, B1..B4, LB1..LB3, E rules of each of the 399 leaves
# Specifically, let's check:
# 1. What is the E-halt condition? (e.g. A even, A odd, A == 0 mod 3, A == 1 mod 3, A == 1,2 mod 4, A == 1 only, etc.)
# 2. Does B_k or LB_k ever HALT directly?
# 3. For each round, given the list [d_L, ..., d_1]; a, does the reduction halt mid-round (via LB_k=H or B_k=H), or reach []; A_{r+1}?
# 4. And what is the parity / mod-3 / mod-4 residue of A_{r+1}?

def get_d_aff(r):
    a_outs = [x[2] for x in r["D"]]
    m = a_outs[1] - a_outs[0]
    c = a_outs[0] - m * 1
    assert all(a_outs[i] == m*(i+1) + c for i in range(6))
    return m, c

# Let's check what m_D values exist in std_399:
m_counts = collections.Counter(get_d_aff(r) for r in std_399)
print("D affine rules (m, c) in std_399:", m_counts)

# Notice:
# When m_D is ODD (m_D in {1, 3, 5, 7}) and c_D is EVEN (c_D in {2, 4, 6, 8}):
#   Then a -> m_D * a + c_D PRESERVES PARITY of a at every D step (Phi_0(a) == a mod 2)!
#   Wait: there is 1 leaf with (3, 5): a -> 3a + 5, which FLIPS parity of a at every D step!
#   And there are 5 leaves with (4, 3): a -> 4a + 3, which forces a' ODD (and mod 3: 4a+3 == a mod 3, PRESERVES a mod 3!)
#   And there are 8 leaves with (5, 4): a -> 5a + 4, which FLIPS parity of a at every D step, and mod 3: 5a+4 == 2a+1 mod 3!

# Let's print the 14 leaves where (m_D % 2 == 0 or c_D % 2 == 1):
print("\n--- Leaves in std_399 where D does NOT simply preserve a mod 2 ---")
for r in std_399:
    m, c = get_d_aff(r)
    if m % 2 == 0 or c % 2 == 1:
        bd = r["bdet"]
        e_pat = "".join(r["E"][a][0] for a in range(1, 17))
        b1_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["B1"][:3]]
        b2_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["B2"][:3]]
        lb1_s = [f"{x[4]};{x[2]}" if x[0]=="K" else x[0] for x in r["LB1"][:3]]
        print(f"  [{r['tag']}] {r['m']} D={m}a+{c} E(1..16)={e_pat}")
        print(f"    B1={b1_s} B2={b2_s} LB1={lb1_s}")
        print(f"    blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' first='{bd['first_ks']}'")
