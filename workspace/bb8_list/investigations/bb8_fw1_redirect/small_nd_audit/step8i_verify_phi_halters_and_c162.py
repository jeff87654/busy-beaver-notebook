import os, sys, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word
from step8g_analyze_all_600_phi import cand162, ecols_map, slot_map, tag_map, phi_ehalt_map, broken_map, kb_res, unb

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")
kblank_detail_exe = os.path.join(WORKDIR, "kblank_detail.exe")

# 1. For the 38 Section-2 leaves, let's check both [1, 0^k]; a AND [2, 0^k]; a AND D on [2, 2]; a vs [2, 3]; a!
sec2 = []
for m, r in sorted(kb_res.items(), key=lambda kv: (tag_map[kv[0]], kv[0])):
    if m in broken_map and "->K:" not in broken_map[m][5] and "=H:" in broken_map[m][5]:
        nK = int(r[1])
        if 0 < nK < 100:
            sec2.append((tag_map[m], slot_map[m], m, broken_map[m][3], r, broken_map[m][5]))

test_cfgs = []
for a in (1, 2, 3, 4):
    test_cfgs.append((f"D_odd({a})", [2, 3], a))
    test_cfgs.append((f"D_evn({a})", [2, 2], a))
for k in (1, 2, 3):
    for a in (2*k+1, 2*k+2, 2*k+3, 2*k+4):
        test_cfgs.append((f"LB1_{k}({a})", [1] + [0]*k, a))
        test_cfgs.append((f"LB2_{k}({a})", [2] + [0]*k, a))

by_tag = collections.defaultdict(list)
for item in sec2:
    by_tag[item[0]].append(item)

print("=== Probing D_odd, D_evn, [1,0^k], and [2,0^k] on the 38 Section-2 leaves ===")
for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, f"tmp_s2b_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, (lbl, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, f"tmp_s2b_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for item in mlist:
            f.write(item[2] + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "50000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    for (tag, slot, m, px, r, mis), line in zip(mlist, res.stdout.strip().split("\n")):
        pcols = line.split("\t")[1:]
        cmap = {lbl: o for (lbl, _, _), o in zip(test_cfgs, pcols)}
        print(f"[{tag}] {slot:4s} {m} | {r[4]}")
        print(f"    D_odd(1..4)  : {[cmap[f'D_odd({a})'] for a in (1,2,3,4)]}")
        print(f"    D_evn(1..4)  : {[cmap[f'D_evn({a})'] for a in (1,2,3,4)]}")
        print(f"    [1,0](3..6)  : {[cmap[f'LB1_1({a})'] for a in (3,4,5,6)]}")
        print(f"    [2,0](3..6)  : {[cmap[f'LB2_1({a})'] for a in (3,4,5,6)]}")
        print(f"    [1,0,0](5..8): {[cmap[f'LB1_2({a})'] for a in (5,6,7,8)]}")
        print(f"    [2,0,0](5..8): {[cmap[f'LB2_2({a})'] for a in (5,6,7,8)]}")
