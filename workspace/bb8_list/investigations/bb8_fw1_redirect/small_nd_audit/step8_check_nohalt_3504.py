import os, sys, collections, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# 1. Inspect the 3,504 no_halt leaves in noinv_leaves.txt
no_halt = []
with open(os.path.join(FW1_DIR, "noinv_leaves.txt"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4:
            m, tag, slot, cols = parts[0], parts[1], parts[2], parts[3:]
            if not any(c.startswith("H") for c in cols):
                no_halt.append((m, tag, slot, cols))

print(f"Total no_halt leaves in noinv_leaves.txt: {len(no_halt)}")

# Classify E-map patterns across AS = [1, 2, 3, 4, 5, 6, 7, 8, 15, 16]
pat_counter = collections.Counter()
has_T_or_X = []
all_K = []

for m, tag, slot, cols in no_halt:
    kinds = "".join(c[0] for c in cols)
    pat_counter[kinds] += 1
    if "T" in kinds or "X" in kinds:
        has_T_or_X.append((m, tag, slot, cols))
    else:
        all_K.append((m, tag, slot, cols))

print("\nE-map kind patterns on AS = [1..8, 15, 16] for the 3,504 no_halt leaves:")
for k, v in pat_counter.most_common():
    print(f"  {k}: {v}")

# For all_K leaves (where all 10 probed E(a) return K:...), check if the E(a) rules are periodic mod 1 or mod 2!
# And for ANY leaf in no_halt (all 3,504, or let's check both all_K and has_T_or_X), can we probe E(9..14) and E(17..24) with kmap2.exe?!
# Wait: 3,504 leaves * 14 E-configs (a = 9..14, 17..24) at max_steps=50000 in kmap2.exe takes only ~8 seconds!
# Let's probe ALL 3,504 no_halt leaves on E(9..14, 17..24) right now!
by_tag = collections.defaultdict(list)
for idx, (m, tag, slot, cols) in enumerate(no_halt):
    by_tag[tag].append((idx, m, slot, cols))

extra_A = [9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24]
found_halts = []

for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, f"tmp_nh_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, A in enumerate(extra_A):
            w = word(tag, [], A, B0)
            f.write(f"e{A} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, f"tmp_nh_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for idx, m, slot, cols in mlist:
            f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "50000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    lines = res.stdout.strip().split("\n")
    for (idx, m, slot, cols), line in zip(mlist, lines):
        pcols = line.split("\t")[1:]
        if any(c.startswith("H") for c in pcols):
            found_halts.append((tag, slot, m, cols, pcols))

print(f"\nProbed all {len(no_halt)} no_halt leaves on E({extra_A}):")
print(f"Leaves that HALT on E({extra_A}): {len(found_halts)}")
for tag, slot, m, cols, pcols in found_halts:
    h_as = [extra_A[i] for i, c in enumerate(pcols) if c.startswith("H")]
    print(f"  [{tag}] {slot} {m} | halts at A={h_as} | orig={cols[:4]} | new={[pcols[i] for i in range(len(extra_A)) if pcols[i].startswith('H')]}")
