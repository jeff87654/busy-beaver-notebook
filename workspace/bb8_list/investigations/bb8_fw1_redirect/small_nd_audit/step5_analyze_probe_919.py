import os, re, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AUDIT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"

def expand_ds(s):
    if not s:
        return []
    out = []
    for x in s.split(","):
        if not x: continue
        if "^" in x:
            v, n = x.split("^")
            out.extend([int(v)] * int(n))
        else:
            out.append(int(x))
    return out

def parse_cell(c):
    if c.startswith("K:"):
        body = c[2:]
        # body could have :steps at the end if from henum, or just ds;a;b from kmap2
        if ":" in body:
            body = body.split(":")[0]
        ds_s, a_s, b_s = body.split(";")
        return ("K", expand_ds(ds_s), int(a_s), int(b_s), ds_s)
    elif c.startswith("H"):
        return ("H", c)
    else:
        return (c[0], c)

cls53_set = set()
with open(os.path.join(FW1_DIR, "cls53.txt"), "r") as f:
    for line in f:
        if line.startswith("== "):
            cls53_set.add(line.strip().split()[2])

noinv_blank = {}
with open(os.path.join(FW1_DIR, "noinv_blank.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            noinv_blank[p[1]] = (p[2], int(p[3]), int(p[4]), int(p[5]), p[6].strip() if len(p) > 6 else "")

rows = []
with open(os.path.join(AUDIT_DIR, "probe_919.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        idx, tag, slot, m = int(p[0]), p[1], p[2], p[3]
        as_cols = p[4:14]
        d_cols  = p[14:20]
        b1_cols = p[20:26]
        b2_cols = p[26:32]
        b3_cols = p[32:38]
        b4_cols = p[38:44]
        lb1_cols = p[44:50]
        lb2_cols = p[50:56]
        lb3_cols = p[56:62]
        e9_14_cols = p[62:68]
        # Combine E(1..16):
        # AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]
        e_all = {}
        for A, c in zip([1, 2, 3, 4, 5, 6, 7, 8, 15, 16], as_cols):
            e_all[A] = parse_cell(c)
        for A, c in zip([9, 10, 11, 12, 13, 14], e9_14_cols):
            e_all[A] = parse_cell(c)
        rows.append({
            "idx": idx, "tag": tag, "slot": slot, "m": m,
            "in_cls53": (m in cls53_set),
            "blank": noinv_blank.get(m),
            "D": [parse_cell(c) for c in d_cols],
            "B1": [parse_cell(c) for c in b1_cols],
            "B2": [parse_cell(c) for c in b2_cols],
            "B3": [parse_cell(c) for c in b3_cols],
            "B4": [parse_cell(c) for c in b4_cols],
            "LB1": [parse_cell(c) for c in lb1_cols],
            "LB2": [parse_cell(c) for c in lb2_cols],
            "LB3": [parse_cell(c) for c in lb3_cols],
            "E": e_all,
        })

print(f"Parsed {len(rows)} rows from probe_919.tsv")

# Let's classify the D rule of each machine on ([2, 3], a=1..6)!
d_types = collections.Counter()
for r in rows:
    D = r["D"]
    if all(x[0] == "K" and x[1] == [2, 2] for x in D):
        # Standard decrement [2, 3] -> [2, 2]! Check affine rule a -> m*a + c
        a_outs = [x[2] for x in D]
        diffs = [a_outs[i+1] - a_outs[i] for i in range(5)]
        if len(set(diffs)) == 1:
            slope = diffs[0]
            inter = a_outs[0] - slope * 1
            r["D_type"] = f"STD_D(a->{slope}a+{inter})"
        else:
            r["D_type"] = f"STD_D_NONAFF({a_outs})"
    elif all(x[0] == "T" for x in D):
        r["D_type"] = "D_ALL_T (likely b_acc or broken D)"
    else:
        shapes = [x[0] if x[0] != "K" else f"K(len={len(x[1])},ds={x[4]})" for x in D]
        r["D_type"] = "OTHER_D: " + " ".join(shapes[:4])
    d_types[(r["in_cls53"], r["D_type"][:35])] += 1

print("\nBreakdown by (in_cls53, D_type):")
for k, v in sorted(d_types.items()):
    print(f"  {str(k[0]):5s} | {k[1]:38s} : {v}")
