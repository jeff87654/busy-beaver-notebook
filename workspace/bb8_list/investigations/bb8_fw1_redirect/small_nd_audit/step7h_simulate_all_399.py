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

# Let's analyze the borrow rules B1..B4 and LB1..LB3 for each of the 399 leaves!
# For a borrow table B_k (tested at a = 2k+1 .. 2k+6) or LB_k (tested at a = 2k+1 .. 2k+6):
# On B_k([2, 2, 0^k], a), standard prefix is [2, 1].
# If ds_out starts with [2, 1], then the replacement for [2, 0^k] is [1] + ds_out[2:].
# On LB_k([1, 0^k], a), the replacement for [1, 0^k] is ds_out.
def analyze_borrow(cells, is_lb=False):
    # cells is a list of 6 parsed cells for a0, a0+1, ..., a0+5
    # Check if all H or all T:
    kinds = [x[0] for x in cells]
    if all(k == "H" for k in kinds):
        return ("ALL_H",)
    if all(k in ("T", "X") for k in kinds):
        return ("ALL_T",)
    # Check by parity of a (indices 0,2,4 are odd a; indices 1,3,5 are even a since 2k+1 is odd):
    # Wait: 2k+1 is ALWAYS ODD! So indices 0, 2, 4 are ODD a, and indices 1, 3, 5 are EVEN a!
    res = {}
    for par_name, idxs in [("odd", [0, 2, 4]), ("even", [1, 3, 5])]:
        sub = [cells[i] for i in idxs]
        sk = [x[0] for x in sub]
        if all(k == "H" for k in sk):
            res[par_name] = ("H",)
        elif all(k in ("T", "X") for k in sk):
            res[par_name] = ("T",)
        elif all(k == "K" for k in sk):
            # Check ds structure and a_out
            ds_list = [x[1] if is_lb else x[1][2:] for x in sub]
            ok_pref = all(is_lb or x[1][:2] == [2, 1] for x in sub)
            a_outs = [x[2] for x in sub]
            lens = [len(d) for d in ds_list]
            tails = [tuple(d[1:]) if len(d) >= 1 else () for d in ds_list]
            c_vals = [d[0] if len(d) >= 1 else None for d in ds_list]
            # Check if a_outs is constant or affine:
            da1 = a_outs[1] - a_outs[0]
            da2 = a_outs[2] - a_outs[1]
            a_par = set(x % 2 for x in a_outs)
            a_mod3 = set(x % 3 for x in a_outs)
            res[par_name] = ("K", ok_pref, lens[0] if len(set(lens))==1 else lens,
                             tails[0] if len(set(tails))==1 else "VAR",
                             a_outs, a_par, a_mod3)
        else:
            res[par_name] = ("MIX", sk)
    return res

# Let's check for all 399 leaves:
# Can we classify each leaf's multi-round fate?
# Let's inspect all leaves where B1/B2/B3/B4 or LB1/LB2/LB3 do NOT simply lock into a non-halting parity/residue!
out_lines = []
verdict_counts = collections.Counter()

for r in std_399:
    m_D, c_D = get_d_aff(r)
    bd = r["bdet"]
    ep = "".join(r["E"][a][0] for a in range(1, 17))
    b1 = analyze_borrow(r["B1"], False)
    b2 = analyze_borrow(r["B2"], False)
    b3 = analyze_borrow(r["B3"], False)
    b4 = analyze_borrow(r["B4"], False)
    lb1 = analyze_borrow(r["LB1"], True)
    lb2 = analyze_borrow(r["LB2"], True)
    lb3 = analyze_borrow(r["LB3"], True)
    r["b_ana"] = (b1, b2, b3, b4, lb1, lb2, lb3)

# Let's group the 399 leaves by their exact behavior and print a detailed diagnostic of any leaf that might halt at E1, E2, E3, E4!
for idx, r in enumerate(std_399):
    m_D, c_D = get_d_aff(r)
    bd = r["bdet"]
    ep = "".join(r["E"][a][0] for a in range(1, 17))
    b1, b2, b3, b4, lb1, lb2, lb3 = r["b_ana"]
    out_lines.append(f"#{idx+1:03d} [{r['tag']}] {r['m']} | D={m_D}a+{c_D} | E={ep}")
    out_lines.append(f"  Blank: st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' first='{bd['first_ks']}'")
    out_lines.append(f"  B1={b1} | LB1={lb1}")
    out_lines.append(f"  B2={b2} | LB2={lb2}")
    out_lines.append(f"  B3={b3} | LB3={lb3}")

with open(os.path.join(AUDIT_DIR, "step7h_diag_399.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")
print("Wrote step7h_diag_399.txt")
