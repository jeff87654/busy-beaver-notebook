import os, glob, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"

# 1. Inspect noinv_leaves.txt and noinv_blank.tsv
noinv_leaves = []
with open(os.path.join(FW1_DIR, "noinv_leaves.txt"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4:
            # m, tag, t, c0..c9 (for AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16])
            noinv_leaves.append((parts[0], parts[1], parts[2], parts[3:]))

print(f"Total rows in noinv_leaves.txt: {len(noinv_leaves)}")

noinv_blank = {}
with open(os.path.join(FW1_DIR, "noinv_blank.tsv"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 6:
            # tag, m, st, nK, nE, maxlen, evs
            tag, m, st, nK, nE, maxlen = parts[0], parts[1], parts[2], int(parts[3]), int(parts[4]), int(parts[5])
            evs = parts[6].strip() if len(parts) > 6 else ""
            noinv_blank[(tag, m)] = (st, nK, nE, maxlen, evs)
            noinv_blank[m] = (tag, st, nK, nE, maxlen, evs)

print(f"Total rows in noinv_blank.tsv: {len(noinv_blank)//2}")

# Let's see how the 4,423 leaves in noinv_leaves.txt break down by E-map outcomes!
AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]
has_halt = []
has_halt_and_k = []
no_halt = []

for m, tag, slot, cols in noinv_leaves:
    kinds = [c[0] for c in cols]
    if 'H' in kinds:
        has_halt.append((m, tag, slot, cols))
        if 'K' in kinds:
            has_halt_and_k.append((m, tag, slot, cols))
    else:
        no_halt.append((m, tag, slot, cols))

print(f"noinv_leaves with 'H' in E-map (has_halt): {len(has_halt)}")
print(f"noinv_leaves with BOTH 'H' and 'K' in E-map (has_halt + has_rebuild): {len(has_halt_and_k)}")
print(f"noinv_leaves without 'H' in E-map: {len(no_halt)}")

# Check how cls53.txt was selected from has_halt!
cls53_machines = set()
with open(os.path.join(FW1_DIR, "cls53.txt"), "r") as f:
    for line in f:
        if line.startswith("== "):
            p = line.strip().split()
            cls53_machines.add(p[2])

print(f"Total machines in cls53.txt: {len(cls53_machines)}")

# For each of the 919 has_halt leaves, inspect its noinv_blank.tsv entry!
by_blank_cat = collections.Counter()
discarded_866 = []
in_cls53 = []

for m, tag, slot, cols in has_halt:
    b = noinv_blank.get(m)
    if b is None:
        by_blank_cat["missing_blank"] += 1
        continue
    _, st, nK, nE, maxlen, evs = b
    in53 = (m in cls53_machines)
    if in53:
        in_cls53.append((m, tag, slot, cols, b))
    else:
        discarded_866.append((m, tag, slot, cols, b))
    # Parse E->len from evs
    import re
    rebuilds = [int(x) for x in re.findall(r'E\d+->(\d+)', evs)]
    max_reb = max(rebuilds) if rebuilds else -1
    by_blank_cat[(in53, st[0], nE > 0, max_reb >= 10, maxlen >= 10)] += 1

print("\nBreakdown of 919 has_halt leaves by (in_cls53, blank_st, nE>0, max_E_rebuild>=10, maxlen>=10):")
for k, v in sorted(by_blank_cat.items()):
    print(f"  {k}: {v}")

print(f"\nCount in_cls53: {len(in_cls53)}, discarded_866: {len(discarded_866)}")

# Also check ALL h_*.tsv files to see total modified K-like leaves!
all_h_files = sorted(glob.glob(os.path.join(FW1_DIR, "h_*.tsv")))
seen_m = set()
tot_mod_k = 0
tot_mod_phi0 = 0
tot_mod_phi1 = 0
tot_mod_noinv = 0
for fn in all_h_files:
    eng = {}
    inv = {}
    if os.path.exists(fn + ".eng"):
        for l in open(fn + ".eng"):
            p = l.rstrip("\n").split("\t")
            eng[p[0]] = (p[1] == "1")
    if os.path.exists(fn + ".inv"):
        for l in open(fn + ".inv"):
            p = l.rstrip("\n").split("\t")
            if len(p) == 5:
                inv[p[0]] = (int(p[1]), int(p[2]), int(p[3]), float(p[4]))
    for l in open(fn):
        if l.startswith("#"): continue
        p = l.rstrip("\n").split("\t")
        if len(p) < 3: continue
        m = p[1]
        if m in seen_m: continue
        seen_m.add(m)
        if p[2][0] != 'T': continue
        if not eng.get(m, True):
            iv = inv.get(m)
            if iv and iv[3] >= 0.5:
                tot_mod_k += 1
                nK, o0, o1, kf = iv
                if o1 == nK: tot_mod_phi1 += 1
                elif o0 == nK: tot_mod_phi0 += 1
                else: tot_mod_noinv += 1

print(f"\nTotal modified K-like leaves across all h_*.tsv: {tot_mod_k} (Phi_1: {tot_mod_phi1}, Phi_0: {tot_mod_phi0}, noinv: {tot_mod_noinv})")
