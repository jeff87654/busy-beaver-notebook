import os, collections
from step5_analyze_probe_919 import rows, parse_cell, expand_ds, AUDIT_DIR
from step7h_simulate_all_399 import std_399, get_d_aff, analyze_borrow

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

for r in std_399:
    r["bdet"] = bdet.get(r["m"], {})

# Let's check for each of the 399 leaves:
# 1. What is the E-halt condition?
# 2. What are the output parities (or mod-3 residues) of B1..B4 and LB1..LB3?
def summarize_leaf(r):
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
    return m_D, c_D, ep, b1, b2, b3, b4, lb1, lb2, lb3

# Let's check how many of the 399 leaves have:
# - D preserves parity (m_D odd, c_D even)
# - E(even) = H, E(odd) = K (i.e. ep == "KHKHKHKHKHKHKHKH")
# And among those, what are the parities of a_out in B1, B2, B3, B4, LB1, LB2, LB3?
for idx, r in enumerate(std_399):
    m_D, c_D, ep, b1, b2, b3, b4, lb1, lb2, lb3 = summarize_leaf(r)
    r["sum"] = (m_D, c_D, ep, b1, b2, b3, b4, lb1, lb2, lb3)

# Let's check if ANY leaf in std_399 has mixed/parity-flipping borrows (like cls53 Group A/C/D where B1/B2 are odd and B3 is even, or where LB1 is odd and LB2 is even)!
print("=== Checking for borrow-parity flips or multi-round candidates in std_399 ===")
candidates = []
for r in std_399:
    m_D, c_D, ep, b1, b2, b3, b4, lb1, lb2, lb3 = r["sum"]
    bd = r["bdet"]
    # Collect all a_par sets across b1..b4, lb1..lb3
    pars = []
    for name, b in [("B1",b1),("B2",b2),("B3",b3),("B4",b4),("LB1",lb1),("LB2",lb2),("LB3",lb3)]:
        if isinstance(b, dict):
            for p_in in ("odd", "even"):
                v = b[p_in]
                if v[0] == "K":
                    pars.append((name, p_in, v[2], v[3], v[5], v[6])) # name, p_in, len, tail, a_par, a_mod3
                else:
                    pars.append((name, p_in, v[0]))
        else:
            pars.append((name, "all", b[0]))
    r["pars"] = pars

# Print summary of all 150 structural groups of std_399 with their exact borrow parities and blank trace!
groups = collections.defaultdict(list)
for r in std_399:
    m_D, c_D, ep, *_ = r["sum"]
    key = (r["tag"], m_D, c_D, ep, str(r["pars"]))
    groups[key].append(r)

print(f"Total unique (tag, D, E, borrow-parity) groups in std_399: {len(groups)}")
out = []
for g_idx, (k, grp) in enumerate(sorted(groups.items(), key=lambda x: (x[0][0], -len(x[1])))):
    tag, m_D, c_D, ep, pars_str = k
    r0 = grp[0]
    out.append(f"=== Group #{g_idx+1:03d} (count={len(grp)}) tag=[{tag}] D={m_D}a+{c_D} E={ep} ===")
    for p_item in r0["pars"]:
        out.append(f"  {p_item}")
    for rr in grp:
        bd = rr["bdet"]
        e1_8 = " ".join(f"E{a}:{rr['E'][a][4]};{rr['E'][a][2]}" if rr["E"][a][0]=="K" else f"E{a}:{rr['E'][a][0]}" for a in range(1, 7))
        out.append(f"  m={rr['m']} | st={bd['st']} nK={bd['nK']} nE={bd['nE']} maxL={bd['maxlen']} e_rebs='{bd['e_rebs']}' | first='{bd['first_ks']}' | {e1_8}")

with open(os.path.join(AUDIT_DIR, "step7i_groups_399.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("Wrote step7i_groups_399.txt")
