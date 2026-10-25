import os, re, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]

noinv_leaves = []
with open(os.path.join(FW1_DIR, "noinv_leaves.txt"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4:
            noinv_leaves.append((parts[0], parts[1], parts[2], parts[3:]))

noinv_blank = {}
with open(os.path.join(FW1_DIR, "noinv_blank.tsv"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 6:
            tag, m, st, nK, nE, maxlen = parts[0], parts[1], parts[2], int(parts[3]), int(parts[4]), int(parts[5])
            evs = parts[6].strip() if len(parts) > 6 else ""
            noinv_blank[m] = (tag, st, nK, nE, maxlen, evs)

cls53_machines = set()
with open(os.path.join(FW1_DIR, "cls53.txt"), "r") as f:
    for line in f:
        if line.startswith("== "):
            cls53_machines.add(line.strip().split()[2])

rescued_866 = []
for m, tag, slot, cols in noinv_leaves:
    kinds = [c[0] for c in cols]
    if 'H' in kinds and m not in cls53_machines:
        rescued_866.append((m, tag, slot, cols, noinv_blank.get(m)))

print(f"Total rescued has_halt leaves: {len(rescued_866)}")

by_tag = collections.Counter()
by_ekinds = collections.Counter()
by_blank_type = collections.Counter()

for m, tag, slot, cols, b in rescued_866:
    by_tag[tag] += 1
    ek = "".join(sorted(set(c[0] for c in cols)))
    by_ekinds[ek] += 1
    _, st, nK, nE, maxlen, evs = b
    rebs = [(int(x[0]), int(x[1])) for x in re.findall(r'E(-?\d+)->(\d+)', evs)]
    only_Es = [int(x) for x in re.findall(r'E(-?\d+)(?!->)', evs)]
    if st.startswith('H'):
        btype = f"BLANK_HALT ({st})"
    elif nK == 0:
        btype = "nK=0 (no K-moments on blank)"
    elif nE == 0:
        btype = f"nE=0, nK>0, maxlen={maxlen} (never reached E1 in 2M steps!)"
    else:
        max_reb = max((r[1] for r in rebs), default=0)
        btype = f"nE={nE}, max_reb={max_reb}, trailing_E={len(only_Es)>0}"
    by_blank_type[(ek, btype)] += 1

print("\nRescued 866 by base tag:")
for k, v in sorted(by_tag.items()):
    print(f"  {k}: {v}")

print("\nRescued 866 by E-map outcome kinds in AS=[1..8,15,16]:")
for k, v in sorted(by_ekinds.items()):
    print(f"  {k}: {v}")

print("\nRescued 866 by (E-map kinds, blank trace behavior in 2M steps):")
for k, v in sorted(by_blank_type.items()):
    print(f"  {k[0]:4s} | {k[1]:55s} : {v}")

# Print examples of interesting rescued leaves:
# 1) nE >= 1 with trailing_E or max_reb in 1..9 and ek == 'HK'
print("\n--- SAMPLE RESCUED LEAVES WITH nE >= 1 and 'HK' in E-map ---")
shown = 0
for m, tag, slot, cols, b in rescued_866:
    ek = "".join(sorted(set(c[0] for c in cols)))
    _, st, nK, nE, maxlen, evs = b
    if ek == 'HK' and nE >= 1 and not st.startswith('H'):
        if shown < 40:
            e_summary = " ".join(f"{A}:{c.split(':')[0] if not c.startswith('K:') else 'K('+c.split(':')[1].split(';')[0]+';'+c.split(':')[1].split(';')[1]+')'}" for A, c in zip(AS, cols))
            print(f"[{tag} {slot}] {m} | nK={nK} nE={nE} maxL={maxlen} evs='{evs}'")
            print(f"   E-map: {e_summary}")
            shown += 1

print("\n--- SAMPLE RESCUED LEAVES WITH nE == 0, nK > 0, maxlen >= 2 and 'HK' in E-map ---")
shown = 0
for m, tag, slot, cols, b in rescued_866:
    ek = "".join(sorted(set(c[0] for c in cols)))
    _, st, nK, nE, maxlen, evs = b
    if ek == 'HK' and nE == 0 and nK > 0 and maxlen >= 2 and not st.startswith('H'):
        if shown < 30:
            e_summary = " ".join(f"{A}:{c.split(':')[0] if not c.startswith('K:') else 'K('+c.split(':')[1].split(';')[0]+';'+c.split(':')[1].split(';')[1]+')'}" for A, c in zip(AS, cols))
            print(f"[{tag} {slot}] {m} | nK={nK} nE={nE} maxL={maxlen} evs='{evs}'")
            print(f"   E-map: {e_summary}")
            shown += 1
