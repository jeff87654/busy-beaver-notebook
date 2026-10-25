import os, sys, subprocess, collections, time

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AUDIT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, FW1_DIR)
sys.path.insert(0, r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits")
import idle
from bcfg import BASES, T, targs, word

KMAP2 = os.path.join(FW1_DIR, "kmap2.exe")

# Load all 919 has_halt leaves from noinv_leaves.txt
noinv_has_halt = []
with open(os.path.join(FW1_DIR, "noinv_leaves.txt"), "r") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4:
            m, tag, slot, cols = parts[0], parts[1], parts[2], parts[3:]
            if any(c.startswith("H") for c in cols):
                noinv_has_halt.append((m, tag, slot, cols))

print(f"Loaded {len(noinv_has_halt)} has_halt leaves from noinv_leaves.txt")

# Build probe configuration list:
# 0..5:   D([2, 3], a=1..6)
# 6..11:  B1([2, 2, 0], a=3..8)
# 12..17: B2([2, 2, 0, 0], a=5..10)
# 18..23: B3([2, 2, 0, 0, 0], a=7..12)
# 24..29: B4([2, 2, 0, 0, 0, 0], a=9..14)
# 30..35: LB1([1, 0], a=3..8)
# 36..41: LB2([1, 0, 0], a=5..10)
# 42..47: LB3([1, 0, 0, 0], a=7..12)
# 48..53: E([], A=9..14)
test_cfgs = []
for a in range(1, 7):
    test_cfgs.append(("D", 0, [2, 3], a))
for k in (1, 2, 3, 4):
    for a in range(2*k + 1, 2*k + 7):
        test_cfgs.append((f"B{k}", k, [2, 2] + [0]*k, a))
for k in (1, 2, 3):
    for a in range(2*k + 1, 2*k + 7):
        test_cfgs.append((f"LB{k}", k, [1] + [0]*k, a))
for A in range(9, 15):
    test_cfgs.append(("E", A, [], A))

by_tag = collections.defaultdict(list)
for idx, (m, tag, slot, cols) in enumerate(noinv_has_halt):
    by_tag[tag].append((idx, m, slot, cols))

# Run at most 2 workers at Idle priority (0x40)
tags_todo = sorted(by_tag.keys())
running = []
out_files = {}

for tag in tags_todo:
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(AUDIT_DIR, f"starts_919_{tag}.txt")
    with open(sf, "w") as f:
        for i, (kind, k, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(AUDIT_DIR, f"mlist_919_{tag}.txt")
    with open(mf, "w") as f:
        for idx, m, slot, cols in by_tag[tag]:
            f.write(m + "\n")

while tags_todo or running:
    running = [(tag, p, fo) for (tag, p, fo) in running if p.poll() is None]
    while tags_todo and len(running) < 2:
        tag = tags_todo.pop(0)
        B0 = BASES[tag][2]
        sf = os.path.join(AUDIT_DIR, f"starts_919_{tag}.txt")
        mf = os.path.join(AUDIT_DIR, f"mlist_919_{tag}.txt")
        of = os.path.join(AUDIT_DIR, f"out_919_{tag}.tsv")
        fo = open(of, "w")
        cmd = [KMAP2, mf] + targs(tag) + [sf, "50000", str(B0)]
        p = subprocess.Popen(cmd, stdout=fo, creationflags=0x40)
        running.append((tag, p, fo))
        print(f"Started kmap2 for tag {tag} ({len(by_tag[tag])} machines)...")
    time.sleep(0.5)

for tag in by_tag:
    # Ensure all file handles closed
    pass

# Merge into a single TSV: probe_919.tsv
merged_rows = {}
for tag, mlist in by_tag.items():
    of = os.path.join(AUDIT_DIR, f"out_919_{tag}.tsv")
    lines = open(of, "r").read().splitlines()
    assert len(lines) == len(mlist), f"Tag {tag}: expected {len(mlist)} lines, got {len(lines)}"
    for (idx, m, slot, cols), line in zip(mlist, lines):
        pcols = line.split("\t")
        assert pcols[0] == m
        merged_rows[idx] = (m, tag, slot, cols, pcols[1:])

with open(os.path.join(AUDIT_DIR, "probe_919.tsv"), "w") as f:
    for idx in sorted(merged_rows):
        m, tag, slot, cols, pcols = merged_rows[idx]
        f.write("\t".join([str(idx), tag, slot, m] + cols + pcols) + "\n")

print(f"Successfully wrote {len(merged_rows)} rows to probe_919.tsv!")
