import os, sys, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word
from step8g_analyze_all_600_phi import unb

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")
kblank_detail_exe = os.path.join(WORKDIR, "kblank_detail.exe")

# 1. Run kblank_detail for 20M steps on the 3 [s] leaves and 1 [t] leaf
for tag, m in [
    ("s", "0LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_1RG1RH"),
    ("s", "1LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_0RB1LG"),
    ("s", "1LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_0RB1RG"),
    ("t", "1RB1RE_1RH1RB_0LD0LG_0RA1LD_---1RF_0LC0RB_1LC1LG_0RF1RC"),
]:
    B0 = BASES[tag][2]
    mf = os.path.join(WORKDIR, f"tmp_20m_{tag}.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kblank_detail_exe, mf] + targs(tag) + ["20000000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    print(f"20M [{tag}] {m}: {res.stdout.strip()}")

# 2. Inspect the 29 non-intact leaves in unb
unb_phi = [x for x in unb if x[3] != "1"]
print(f"\n=== Inspecting the {len(unb_phi)} non-intact Phi_x leaves in unb ===")
test_cfgs = []
for a in (1, 2, 3, 4):
    test_cfgs.append((f"D({a})", [2, 3], a))
for k in (1, 2):
    for a in (2*k+1, 2*k+2):
        test_cfgs.append((f"B{k}({a})", [2, 2] + [0]*k, a))
        test_cfgs.append((f"LB{k}({a})", [1] + [0]*k, a))

by_tag = collections.defaultdict(list)
for item in unb_phi:
    by_tag[item[0]].append(item)

for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, f"tmp_up_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, (lbl, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, f"tmp_up_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for item in mlist:
            f.write(item[2] + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "50000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    for (tag, slot, m, ps, eh_pos, nK, mnd, last_k, ecols), line in zip(mlist, res.stdout.strip().split("\n")):
        pcols = line.split("\t")[1:]
        cmap = {lbl: o for (lbl, _, _), o in zip(test_cfgs, pcols)}
        es = [f"E({[1,2,3,4,5,6,7,8,15,16][i]})={ecols[i]}" for i in range(6)]
        print(f"[{tag}] {slot:4s} {m} | {ps} Eh={eh_pos} nK={nK} mnd={mnd} | {last_k}")
        print(f"    E(1..6): {', '.join(es)}")
        print(f"    D(1..4): {[cmap[f'D({a})'] for a in (1,2,3,4)]} | B1: {[cmap[f'B1({a})'] for a in (3,4)]} | LB1: {[cmap[f'LB1({a})'] for a in (3,4)]}")
