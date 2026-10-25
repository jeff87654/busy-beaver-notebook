import os, re, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AUDIT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"

from step5_analyze_probe_919 import rows, parse_cell, expand_ds

# Load blank_detail_919.tsv
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

# First, inspect all rescued leaves (in_cls53 == False) where D maps [2, 3] -> [2, 2] for all a=1..6 (includes STD_D and b_acc!)
std_or_bacc = []
other_d = []
for r in rows:
    if r["in_cls53"]:
        continue
    D = r["D"]
    # Also include b_acc where D[1:] (a=2..6) or all D have x[1] == [2, 2]
    if all(x[0] == "K" and x[1] == [2, 2] for x in D[1:]):
        std_or_bacc.append(r)
    else:
        other_d.append(r)

out_f = open(os.path.join(AUDIT_DIR, "step6_utf8.txt"), "w", encoding="utf-8")
def pr(*args):
    print(*args, file=out_f)

pr(f"Rescued 866 breakdown: {len(std_or_bacc)} preserve D ([2,3]->[2,2] for a>=2), {len(other_d)} modify/break D")

# Let's analyze the 425 rescued leaves that preserve D ([2,3] -> [2,2])!
def summarize_bk(B_list, prefix_expected):
    # B_list is 6 outcomes for a = 2k+1 .. 2k+6 (odd, even, odd, even, odd, even)
    if not all(x[0] == "K" for x in B_list):
        return "NON_K(" + ",".join(x[0] for x in B_list) + ")"
    # Check if all start with prefix_expected
    tails = []
    a_outs = []
    for x in B_list:
        ds = x[1]
        if ds[:len(prefix_expected)] != prefix_expected:
            return f"BAD_PRE({x[4]};a={x[2]})"
        tails.append(ds[len(prefix_expected):])
        a_outs.append(x[2])
    # Separate odd a (indices 0, 2, 4) and even a (indices 1, 3, 5)
    len_odd = [len(tails[i]) for i in (0, 2, 4)]
    len_evn = [len(tails[i]) for i in (1, 3, 5)]
    if len(set(len_odd)) > 1 or len(set(len_evn)) > 1:
        return f"VAR_LEN(odd={len_odd},evn={len_evn})"
    lo, le = len_odd[0], len_evn[0]
    p_odd = sorted(set(a_outs[i] % 2 for i in (0, 2, 4)))
    p_evn = sorted(set(a_outs[i] % 2 for i in (1, 3, 5)))
    a_set = sorted(set(a_outs))
    # Also check constant suffix of tail (after first element of tail which grows with a)
    suf_o = tails[0][1:] if lo >= 1 else []
    suf_e = tails[1][1:] if le >= 1 else []
    return f"L={lo}/{le},suf={suf_o}/{suf_e},apar={p_odd}/{p_evn},a={a_set}"

def summarize_E(e_dict):
    # e_dict maps A in 1..16 -> parsed cell
    # Check pattern of H vs K vs T across A=1..16
    pat = "".join(e_dict[A][0] for A in range(1, 17))
    # Summarize K outputs
    k_info = []
    for A in (1, 2, 3, 4, 5, 6):
        c = e_dict[A]
        if c[0] == "K":
            k_info.append(f"E{A}:[{c[4]}];{c[2]}")
        else:
            k_info.append(f"E{A}:{c[0]}")
    return pat, " ".join(k_info)

groups = collections.defaultdict(list)
for r in std_or_bacc:
    D = r["D"]
    a_outs = [x[2] for x in D]
    diffs = [a_outs[i+1] - a_outs[i] for i in range(5)]
    if len(set(diffs)) == 1:
        d_str = f"D:{diffs[0]}a+{a_outs[0]-diffs[0]}"
    else:
        d_str = f"D_alt:{a_outs}"
    b1_s = summarize_bk(r["B1"], [2, 1])
    b2_s = summarize_bk(r["B2"], [2, 1])
    b3_s = summarize_bk(r["B3"], [2, 1])
    lb1_s = summarize_bk(r["LB1"], [])
    lb2_s = summarize_bk(r["LB2"], [])
    epat, einfo = summarize_E(r["E"])
    bd = r["bdet"]
    key = (r["tag"], d_str, b1_s, b2_s, b3_s, epat)
    groups[key].append((r, lb1_s, lb2_s, einfo))

pr(f"\nFound {len(groups)} distinct (tag, D, B1, B2, B3, E_pat) classes among the {len(std_or_bacc)} D-preserving rescued leaves:")
for idx_g, (key, items) in enumerate(sorted(groups.items())):
    tag, d_str, b1_s, b2_s, b3_s, epat = key
    r0, lb1_s, lb2_s, einfo = items[0]
    bd0 = r0["bdet"]
    pr(f"\n--- Group #{idx_g+1:02d} [{tag}] count={len(items)} | {d_str} | E_pat(1..16)={epat} | ex={r0['m']} ({r0['slot']}) ---")
    pr(f"  B1:  {b1_s}")
    pr(f"  B2:  {b2_s}")
    pr(f"  B3:  {b3_s}")
    pr(f"  LB1: {lb1_s} | LB2: {lb2_s}")
    pr(f"  E(1..6): {einfo}")
    # Show distinct blank trajectories in this group!
    b_sigs = collections.Counter()
    for r, _, _, _ in items:
        bd = r["bdet"]
        b_sigs[(bd.get("st",""), bd.get("nK",0), bd.get("nE",0), bd.get("maxlen",0), bd.get("e_rebs",""), bd.get("first_ks","")[:90])] += 1
    for bsig, cnt in sorted(b_sigs.items()):
        pr(f"  Blank ({cnt}x): st={bsig[0]} nK={bsig[1]} nE={bsig[2]} maxL={bsig[3]} e_rebs='{bsig[4]}' | first='{bsig[5]}'")
out_f.close()
