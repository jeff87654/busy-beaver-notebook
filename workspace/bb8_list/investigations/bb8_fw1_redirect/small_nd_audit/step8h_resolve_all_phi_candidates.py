import os, sys, glob, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# Load step8g data
from step8g_analyze_all_600_phi import cand162, ecols_map, slot_map, tag_map, phi_ehalt_map, broken_map, kb_res, unb

print("=== Remaining 18 of the 58 unbroken Phi_x / intact leaves (40..58) ===")
for x in unb[40:]:
    print(f"  [{x[0]}] {x[1]:5s} {x[2]} | {x[3]} Eh={x[4]} nK={x[5]} mnd={x[6]} | {x[7]}")

# Now let's inspect the exact D, B1..B4, LB1..LB3 rules on the 38 Section-2 leaves!
sec2 = []
for m, r in sorted(kb_res.items(), key=lambda kv: (tag_map[kv[0]], kv[0])):
    if m in broken_map and "->K:" not in broken_map[m][5] and "=H:" in broken_map[m][5]:
        nK = int(r[1])
        if 0 < nK < 100:
            sec2.append((tag_map[m], slot_map[m], m, broken_map[m][3], r, broken_map[m][5]))

print(f"\n=== Detailed analysis of all {len(sec2)} Section-2 leaves (hhalt_active with 0 < nK < 100) ===")
# Let's probe D(1..6), B1(3..6), B2(5..8), LB1(3..6), LB2(5..8), LB3(7..10) on sec2
test_cfgs = []
for a in range(1, 7):
    test_cfgs.append((f"D({a})", [2, 3], a))
for k in (1, 2):
    for a in range(2*k+1, 2*k+5):
        test_cfgs.append((f"B{k}({a})", [2, 2] + [0]*k, a))
for k in (1, 2, 3):
    for a in range(2*k+1, 2*k+5):
        test_cfgs.append((f"LB{k}({a})", [1] + [0]*k, a))

by_tag = collections.defaultdict(list)
for item in sec2:
    by_tag[item[0]].append(item)

for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, f"tmp_s2_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, (lbl, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, f"tmp_s2_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for item in mlist:
            f.write(item[2] + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "50000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    for (tag, slot, m, px, r, mis), line in zip(mlist, res.stdout.strip().split("\n")):
        pcols = line.split("\t")[1:]
        cmap = {lbl: o for (lbl, _, _), o in zip(test_cfgs, pcols)}
        d_Summary = [f"D({a})={cmap[f'D({a})']}" for a in (1,2,3,4)]
        b1_Summary = [f"B1({a})={cmap[f'B1({a})']}" for a in (3,4)]
        lb1_Summary = [f"LB1({a})={cmap[f'LB1({a})']}" for a in (3,4,5,6)]
        lb2_Summary = [f"LB2({a})={cmap[f'LB2({a})']}" for a in (5,6)]
        print(f"[{tag}] {slot:4s} {m} | nK={r[1]} | {r[4]}")
        print(f"    D  : {', '.join(d_Summary)}")
        print(f"    B1 : {', '.join(b1_Summary)}")
        print(f"    LB1: {', '.join(lb1_Summary)} | LB2: {', '.join(lb2_Summary)}")
