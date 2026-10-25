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
    sf = os.path.join(WORKDIR, "tmp_starts_v.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_v.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs, out))

# 1. Check G#07 [d]: [3^k, 1]; 15 for k=1..8
m07 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_0RA0RH_---0RA"
print("=== 1. G#07 [d] [3^k, 1]; 15 for k=1..8 ===")
cfgs_07 = [([3]*k + [1], 15) for k in range(1, 9)]
for cfg, ans in probe_configs("d", m07, cfgs_07, max_steps=5000000):
    print(f"  k={len(cfg[0])-1}: {cfg} -> {ans}")

# 2. Check G#25 [d]: exact formula for D on a=5, 21, 37, etc.
m25 = "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB"
print("\n=== 2. G#25 [d] [10]; a for a=1..32 ===")
cfgs_25 = [([10], a) for a in range(1, 33)]
for cfg, ans in probe_configs("d", m25, cfgs_25, max_steps=1000000):
    print(f"  {cfg} -> {ans}")

# 3. Check G#27 [d]: exact trace of [2, 130]; 4
# Let's see what happens when [2, d]; a reaches d=0, 1, 2, 3!
# From step7u:
#   On odd a=2m+1: D subtracts 1, a' = 3a + 4 (odd? Wait: 3(2m+1)+4 = 6m+7, ALWAYS ODD!)
#   On even a=2m: D subtracts 3, a' = 27a + 80 (ALWAYS EVEN!)
#   Wait: if a=4 is EVEN, then a' = 27a + 80 is ALWAYS EVEN!
#   So starting from [2, 130]; 4 (where a=4 is even):
#   Every step has a EVEN, so every step subtracts 3 from d:
#   130 -> 127 -> 124 -> ... -> 1! (since 130 = 3*43 + 1, after 43 steps d reaches 1 with a_43 EVEN!)
#   Then from [2, 1]; a (with a EVEN):
#   Look at step7u section 4:
#   ([2, 1], 2) -> K:1,40;4;0
#   ([2, 1], 4) -> K:1,58;4;0
#   ([2, 1], 6) -> K:1,76;4;0
#   In general, for even a, [2, 1]; a -> [1, 9a + 22]; 4!
#   Then from [1, D_1]; 4 (with a=4 EVEN!):
#   Note that D_1 = 9*a_43 + 22 is EVEN (since a_43 is even)!
#   Wait: what is D_1 mod 3?!
#   Since a_43 = 27*a_42 + 80 == 2 (mod 3), D_1 = 9*a_43 + 22 == 22 == 1 (mod 3)!
#   So starting from [1, D_1]; 4, every step has a EVEN and subtracts 3 from the second digit until it reaches [1, 1]; A_even!
#   Then from [1, 1]; A_even (with A_even == 2 mod 3, EVEN):
#   Look at step7u section 4:
#   ([1, 1], 2) -> K:40;4;0
#   ([1, 1], 4) -> K:58;4;0
#   So [1, 1]; A_even -> [9*A_even + 22]; 4! (a 1-digit list [D_2]; 4 with D_2 == 1 mod 3!)
#   Then from [D_2]; 4, every step subtracts 3 until it reaches [1]; A'_even!
#   And what does [1]; A'_even (or [2]; A'_even or [3]; A'_even) do in G#27?! Let's probe [1]; a, [2]; a, [3]; a in G#27!
m27 = "1RB1RA_0LC0LF_1RD1LC_1LH1RE_1LB0RG_1LE1LF_---0RA_1RG1LD"
print("\n=== 3. G#27 [d] [d]; a for d=1,2,3 and a=1..6 ===")
cfgs_27 = [([d], a) for d in [1, 2, 3] for a in range(1, 7)]
for cfg, ans in probe_configs("d", m27, cfgs_27, max_steps=1000000):
    print(f"  {cfg} -> {ans}")
