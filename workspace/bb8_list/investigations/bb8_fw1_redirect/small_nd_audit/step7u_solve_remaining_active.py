import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

def probe_configs(tag, m, cfgs, max_steps=500000):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, "tmp_starts_u.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_u.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs, out))

# 1. Check G#55 [t]: 1RB1RE_1RC1RB_0LD0LG_0RA1LH_---1RF_0LC0RB_1LC1LG_1RA1LD
m55 = "1RB1RE_1RC1RB_0LD0LG_0RA1LH_---1RF_0LC0RB_1LC1LG_1RA1LD"
print("=== 1. G#55 [t] E(a) and D(a) probe ===")
cfgs_55 = [([], a) for a in [1, 2, 3, 4, 5, 7, 9, 15, 25, 2557]]
for cfg, ans in probe_configs("t", m55, cfgs_55, max_steps=30000000):
    print(f"  {cfg} -> {ans}")

# 2. Check G#07 [d]: 1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_0RA0RH_---0RA
m07 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_0RA0RH_---0RA"
print("\n=== 2. G#07 [d] [3, 1]; a and [2, 1]; a probe ===")
cfgs_07 = [([3, 1], a) for a in range(1, 17)] + [([2, 1], a) for a in range(1, 10)]
for cfg, ans in probe_configs("d", m07, cfgs_07, max_steps=500000):
    print(f"  {cfg} -> {ans}")

# 3. Check G#25 [d]: 1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB
m25 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB"
print("\n=== 3. G#25 [d] D([2, 3]; a) and [1..4]; a probe ===")
cfgs_25 = [([2, 3], a) for a in range(1, 17)] + [([d], a) for d in [1, 2, 3, 4] for a in range(1, 9)]
for cfg, ans in probe_configs("d", m25, cfgs_25, max_steps=500000):
    print(f"  {cfg} -> {ans}")

# 4. Check G#27 [d]: 1RB1RA_0LC0LF_1RD1LC_1LH1RE_1LB0RG_1LE1LF_---0RA_1RG1LD
m27 = "1RB1RA_0LC0LF_1RD1LC_1LH1RE_1LB0RG_1LE1LF_---0RA_1RG1LD"
print("\n=== 4. G#27 [d] [2, d]; a probe for d=1,2,3 and a=1..8 ===")
cfgs_27 = [([2, d], a) for d in [1, 2, 3, 4] for a in range(1, 7)] + [([1, d], a) for d in [1, 2, 3] for a in [1, 2, 3, 4]]
for cfg, ans in probe_configs("d", m27, cfgs_27, max_steps=500000):
    print(f"  {cfg} -> {ans}")

# 5. Check G#23 [d]: 1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD
m23 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD"
print("\n=== 5. G#23 [d] D([2, 3]; a) and [2, d]; a probe ===")
cfgs_23 = [([2, 3], a) for a in range(1, 13)] + [([2, d], a) for d in [1, 2] for a in range(1, 9)]
for cfg, ans in probe_configs("d", m23, cfgs_23, max_steps=500000):
    print(f"  {cfg} -> {ans}")

# 6. Check G#24 [d]: 1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE
m24 = "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE"
print("\n=== 6. G#24 [d] D([2, 3]; a) and [2, d]; a probe ===")
cfgs_24 = [([2, 3], a) for a in range(1, 13)] + [([2, d], a) for d in [1, 2] for a in range(1, 9)]
for cfg, ans in probe_configs("d", m24, cfgs_24, max_steps=500000):
    print(f"  {cfg} -> {ans}")

# 7. Check G#44 [n]: 1RB1LH_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RB1LA
m44 = "1RB1LH_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RB1LA"
print("\n=== 7. G#44 [n] D([2, 3]; a) and [2, d]; a probe ===")
cfgs_44 = [([2, 3], a) for a in range(1, 13)] + [([2, d], a) for d in [1, 2] for a in range(1, 9)]
for cfg, ans in probe_configs("n", m44, cfgs_44, max_steps=500000):
    print(f"  {cfg} -> {ans}")
