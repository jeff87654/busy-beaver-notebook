import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

def probe_configs(tag, m, cfgs, max_steps=1000000):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, "tmp_starts_y.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_y.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs, out))

# 1. G#23: [10]; a for a=1..32, plus [d]; a for d=1..4, a=1..12
m23 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD"
print("=== 1. G#23 [10]; a for a=1..32 ===")
for cfg, ans in probe_configs("d", m23, [([10], a) for a in range(1, 33)]):
    print(f"  {cfg} -> {ans}")

print("\n=== 1b. G#23 [d]; a for d=1..4, a=1..8 ===")
for cfg, ans in probe_configs("d", m23, [([d], a) for d in [1,2,3,4] for a in range(1, 9)]):
    print(f"  {cfg} -> {ans}")

# 2. G#24: [10]; a for a=1..32, plus [d]; a for d=1..4, a=1..12
m24 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE"
print("\n=== 2. G#24 [10]; a for a=1..32 ===")
for cfg, ans in probe_configs("d", m24, [([10], a) for a in range(1, 33)]):
    print(f"  {cfg} -> {ans}")

print("\n=== 2b. G#24 [d]; a for d=1..4, a=1..8 ===")
for cfg, ans in probe_configs("d", m24, [([d], a) for d in [1,2,3,4] for a in range(1, 9)]):
    print(f"  {cfg} -> {ans}")

# 3. G#27: test reducing [3, 2^N]; 3 for N=1..6!
m27 = "1RB1RA_0LC0LF_1RD1LC_1LH1RE_1LB0RG_1LE1LF_---0RA_1RG1LD"
print("\n=== 3. G#27 [3, 2, 0, 0]; a and [3, 1, 0, 0]; a and [2, 0, 0]; a ===")
cfgs_27 = [([2, 2, 0, 0], a) for a in range(1, 9)] + [([1, 0, 0], a) for a in range(1, 9)] + [([2, 0, 0], a) for a in range(1, 9)] + [([3, 0, 0], a) for a in range(1, 9)]
for cfg, ans in probe_configs("d", m27, cfgs_27):
    print(f"  {cfg} -> {ans}")
