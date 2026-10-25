import os, collections, re
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

# Let's write a symbolic round reducer for std_399!
# Given a list (ds, a) at the start of a round (or after blank startup):
# Wait: what can happen to (ds, a) under D, B_k, LB_k?
# Let's check for each leaf r in std_399:
# Can we fit an exact function for B_k(a) and LB_k(a) for k=1,2,3 (and B_4)?
def fit_borrow_table(cells, k, is_lb=False):
    # cells has 6 entries for a_in = 2k+1 .. 2k+6
    # Fit separately for odd a_in (indices 0,2,4: a_in = 2k+1, 2k+3, 2k+5)
    # and even a_in (indices 1,3,5: a_in = 2k+2, 2k+4, 2k+6)
    rules = {}
    for par, idxs in [(1, [0, 2, 4]), (0, [1, 3, 5])]:
        a_ins = [2*k + 1 + i for i in idxs]
        sub = [cells[i] for i in idxs]
        kinds = [x[0] for x in sub]
        if all(x == "H" for x in kinds):
            rules[par] = ("H",)
            continue
        if all(x in ("T", "X") for x in kinds):
            rules[par] = ("T",)
            continue
        if not all(x == "K" for x in kinds):
            rules[par] = ("MIX", kinds)
            continue
        # Check prefix for B_k:
        if not is_lb:
            if all(x[1][:2] == [2, 1] for x in sub):
                # Standard borrow [2, 2, 0^k] -> [2, 1] + new_ds
                new_ds_list = [x[1][2:] for x in sub]
                mode = "STD"
            elif all(x[1] == [2, 0] for x in sub):
                # Consumes a zero and decrements 2->0? No, [2, 2, 0] -> [2, 0] means [2, 0] -> [0]!
                new_ds_list = [[0] for _ in sub]
                mode = "DROP_TO_ZERO"
            elif all(x[1] == [2] for x in sub):
                new_ds_list = [[] for _ in sub]
                mode = "DROP_EMPTY"
            else:
                rules[par] = ("NONSTD_PREF", [x[1] for x in sub])
                continue
        else:
            new_ds_list = [x[1] for x in sub]
            mode = "STD"
        # Check lengths of new_ds_list:
        lens = [len(d) for d in new_ds_list]
        a_outs = [x[2] for x in sub]
        da1 = a_outs[1] - a_outs[0]
        da2 = a_outs[2] - a_outs[1]
        a_aff = (da1 // 2, a_outs[0] - (da1 // 2) * a_ins[0]) if (da1 == da2 and da1 % 2 == 0) else None
        if len(set(lens)) == 1:
            L = lens[0]
            if L == 0:
                rules[par] = ("K0", mode, a_aff, a_outs)
            else:
                # Check if new_ds_list[i][0] is affine in a_in and tail is constant:
                c0s = [d[0] for d in new_ds_list]
                tails = [tuple(d[1:]) for d in new_ds_list]
                dc1 = c0s[1] - c0s[0]
                dc2 = c0s[2] - c0s[1]
                c_aff = (dc1 // 2, c0s[0] - (dc1 // 2) * a_ins[0]) if (dc1 == dc2 and dc1 % 2 == 0) else None
                if len(set(tails)) == 1 and c_aff is not None and a_aff is not None:
                    rules[par] = ("K_AFF", mode, L, c_aff, tails[0], a_aff, a_outs)
                else:
                    rules[par] = ("K_VAR", mode, L, new_ds_list, a_outs)
        else:
            rules[par] = ("K_VARLEN", mode, new_ds_list, a_outs)
    return rules

# Test fitting on all 399 leaves!
unusual = []
for r in std_399:
    r["fit_B"] = {}
    r["fit_LB"] = {}
    for k in (1, 2, 3, 4):
        r["fit_B"][k] = fit_borrow_table(r[f"B{k}"], k, False)
    for k in (1, 2, 3):
        r["fit_LB"][k] = fit_borrow_table(r[f"LB{k}"], k, True)
    for k in (1, 2, 3):
        for par in (0, 1):
            fb = r["fit_B"][k][par]
            flb = r["fit_LB"][k][par]
            if fb[0] not in ("H", "T", "K0", "K_AFF") or flb[0] not in ("H", "T", "K0", "K_AFF"):
                unusual.append((r["tag"], r["m"], f"B{k}/LB{k}(par={par})", fb, flb))

print(f"Total unusual (non-affine) B_k/LB_k entries across all 399 leaves: {len(unusual)}")
for u in unusual[:30]:
    print(" ", u)
